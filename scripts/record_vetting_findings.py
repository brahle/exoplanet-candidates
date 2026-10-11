"""Import dated, sealed vetting findings; publishing requires a separate explicit push."""
from __future__ import annotations

import argparse
import copy
from datetime import UTC, datetime
from pathlib import Path
import re

import catalogue
from export_batch import load, public, seal, sha, write
import vetting


def checked_run(folder, command):
    manifest = load(folder / 'manifest.json')
    if (manifest.get('ok') is not True or not manifest.get('finished_utc') or
            manifest['command'] != command):
        raise ValueError('Requires a successful terminal run of the expected command')
    if datetime.fromisoformat(manifest['finished_utc'].replace('Z', '+00:00')).tzinfo is None:
        raise ValueError('Terminal timestamp requires a timezone')
    for name, digest in manifest['outputs'].items():
        if sha(catalogue.inside(folder, name)) != digest:
            raise ValueError('Vetting source bytes changed')
    return manifest


def identified(rows):
    result = {}
    for row in rows:
        sid = row['signal_id']
        if sid in result or not re.fullmatch(r'tic-[0-9]+-s[0-9]{2}', sid):
            raise ValueError('Duplicate or unsafe signal ID')
        result[sid] = row
    return result


def reference(folder, manifest):
    return {'run_id': manifest['run_id'], 'command': manifest['command'],
            'finished_utc': manifest['finished_utc'],
            'source_revision': manifest['git']['commit'],
            'manifest_sha256': sha(folder / 'manifest.json'), 'outputs': manifest['outputs']}


def unchanged_findings(folder, data, evidence):
    """An exact semantic replay preserves the original exported JSON bytes."""
    path = folder / 'evidence/vetting-findings.json'
    if load(path) != evidence:
        return False
    expected = copy.deepcopy(data)
    expected['evidence'][0]['sha256'] = sha(path)
    return load(folder / 'vetting.json') == expected


def source_diagnostics(folder, receipt):
    path = Path(receipt['manifest'])
    if receipt['artifacts'].get(str(path)) != sha(path):
        raise ValueError('Source receipt manifest seal differs')
    manifest = checked_run(path.parent, 'vet-localisation')
    data = load(path.parent / 'localisation.json')
    if data['ephemeris']['id'] != receipt['signal_id']:
        raise ValueError('Source diagnostics identity differs')
    return public({'reference': reference(path.parent, manifest), 'metrics': receipt['metrics'],
                   'scientific_status': receipt['scientific_status'],
                   'limits': data['limits'], 'rejected': data['rejected'],
                   'sectors': [{'sector': s['sector'], 'status': s['status'],
                                'clock_passed': s.get('clock', {}).get('passed', False)}
                               for s in data['sectors']]})


def prepare(args):
    root = args.root.resolve()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.snapshot):
        raise ValueError('Unsafe assessment snapshot')
    records = {r['id']: r for r in catalogue.records()}
    runs = []; references = []
    for name, command in [('screen_run', 'vet-binary-priorities'),
                          ('lightcurve_run', 'vet-remaining-diagnostics'),
                          ('catalogue_run', 'vet-binary-catalogues')]:
        folder = getattr(args, name)
        manifest = checked_run(folder, command)
        runs.append(identified(load(folder / 'signals.json')))
        references.append(reference(folder, manifest))
    screen, lightcurve, binaries = runs
    if any(set(rows) != set(records) for rows in runs):
        raise ValueError('Every initial screen must conserve the complete public cohort')
    sources = {}; omitted_sources = set()
    allowed_nonpublic = set(args.nonpublic_signal)
    if allowed_nonpublic & set(records):
        raise ValueError('A public signal cannot be excluded as nonpublic')
    for folder in args.source_snapshot:
        manifest = checked_run(folder, 'vet-source-wave-progress-snapshot')
        references.append(reference(folder, manifest))
        for row in load(folder / 'report.json')['assessments']:
            receipt = row['stages']['localisation']
            if receipt['execution_status'] == 'succeeded':
                sid = row['signal']['id']
                if sid not in records and sid in allowed_nonpublic:
                    omitted_sources.add(sid)
                    continue
                if sid not in records or sid in sources:
                    raise ValueError('Foreign or duplicate completed source signal')
                sources[sid] = source_diagnostics(folder, receipt)
    for folder in args.source_batch:
        manifest = checked_run(folder, 'vet-localisation-batch')
        references.append(reference(folder, manifest))
        for line in (folder / 'attempts.jsonl').read_text().splitlines():
            import json
            receipt = json.loads(line)['receipt']
            if receipt['execution_status'] == 'succeeded':
                sid = receipt['signal_id']
                if sid not in records and sid in allowed_nonpublic:
                    omitted_sources.add(sid)
                    continue
                if sid not in records or sid in sources:
                    raise ValueError('Foreign or duplicate completed source signal')
                sources[sid] = source_diagnostics(folder, receipt)
    offsets = {}
    for folder in args.offset_run:
        manifest = load(folder / 'manifest.json')
        if manifest['command'] not in {'vet-counted-fields-source-checkpoint',
                                      'vet-new-source-offset-audit',
                                      'vet-next-source-terminal-audit',
                                      'vet-crowded-source-terminal-audit'}:
            raise ValueError('Unexpected offset audit command')
        checked_run(folder, manifest['command'])
        references.append(reference(folder, manifest))
        filename = 'source-fit-offsets.json' if manifest['command'] == 'vet-counted-fields-source-checkpoint' else 'offsets.json'
        for row in load(folder / filename):
            if row['signal_id'] in omitted_sources:
                continue
            if row['signal_id'] not in sources:
                raise ValueError('Offset audit does not match a completed source signal')
            offsets.setdefault(row['signal_id'], []).append(public(row))
    reviewed_warnings = set(args.source_warning)
    if len(reviewed_warnings) != len(args.source_warning) or not reviewed_warnings <= set(offsets):
        raise ValueError('Reviewed source warnings require unique completed audited signals')
    physical = {}; controls_omitted = []
    if args.physical_report:
        manifest = checked_run(args.physical_report, 'vet-physical-batch-report')
        references.append(reference(args.physical_report, manifest))
        for row in load(args.physical_report / 'report.json')['outcomes']:
            sid = row['signal_id']
            if sid not in records:
                controls_omitted.append(sid)
                continue
            physical.setdefault(sid, []).append({k: row[k] for k in
                ('signal_id', 'scenario', 'execution_outcome', 'audit_outcome',
                 'sampling_status', 'candidate_gate_satisfied', 'error')})
    prepared = []
    for sid, record in records.items():
        if record['assessment']['disposition'] != 'unclassified_transit_like_signal':
            raise ValueError('Screen import cannot replace a reviewed scientific classification')
        if record['novelty']['status'] != screen[sid]['novelty']:
            raise ValueError('Novelty differs from the dated joined screen')
        light = copy.deepcopy(lightcurve[sid]); light.pop('selected_ephemeris', None)
        if (lightcurve[sid].get('selected_ephemeris') and
                abs(lightcurve[sid]['selected_ephemeris']['period_d'] -
                    record['signal']['period_d']['value']) > 1e-12):
            raise ValueError('Diagnostics refer to a different adopted period')
        folder = root / 'candidates' / sid
        external = None
        if (folder / 'evidence/external-report.json').exists():
            previous = load(folder / 'evidence/external-report.json')['source_record']
            tier = previous['reported_disposition'].get('tier')
            if tier in {'C', 'likely EB', 'likely nearby FP'}:
                external = {'reported_tier': tier, 'rationale': previous['raw'].get('c_reason'),
                            'evidence': 'evidence/external-report.json',
                            'scope': 'Attributed external report; not our adjudicated classification'}
        evidence = public({'signal_id': sid, 'assessed_utc': args.assessed_utc,
                           'screen': screen[sid], 'lightcurve': light, 'catalogues': binaries[sid],
                           'source_diagnostics': sources.get(sid), 'source_fit_offsets': offsets.get(sid, []),
                           'source_warning_reviewed': sid in reviewed_warnings,
                           'external_report': external, 'physical_pilot': physical.get(sid, []),
                           'previous_publication': (load(folder / 'evidence/vetting-findings.json')['previous_publication']
                               if (folder / 'vetting.json').exists() else copy.deepcopy(record['publication'])),
                           'source_runs': references,
                           'limits': ['Warning triggers are descriptive and uncalibrated.',
                                      'Nearby period/alias matches do not establish the dip host.',
                                      'Incomplete or failed qualification remains unresolved.',
                                      'No FPP/NFPP, search reliability or planet probability inferred.',
                                      'Derived evidence excerpts; not a public numerical rerun.']})
        vetting.safe_public(evidence)
        stages = dict.fromkeys(vetting.STAGES, 'not_started')
        stages['screening'] = 'complete' if screen[sid]['all_joined_checks_available'] else 'partial'
        if sid in sources or any(Path(p).name == 'source_summary.json'
                                 for p in record['assessment']['source_localisation']['evidence']):
            stages['source_vetting'] = 'partial'
        if sid in physical:
            stages['physical_vetting'] = 'blocked'
        data = {'schema_version': '1.0', 'signal_id': sid, 'assessed_utc': args.assessed_utc,
                'progress': {'stage': vetting.progress_stage(stages), 'stages': stages},
                'scientific_assessment': {'status': 'unclassified', 'planet_probability': None,
                    'basis': 'Transit-like signal; source/timing qualification and remaining false-positive tests unresolved.',
                    'review_evidence': []},
                'initial_screen': {'outcome': vetting.initial_outcome(screen[sid]),
                                   'all_checks_available': screen[sid]['all_joined_checks_available']},
                'warnings': vetting.warning_codes(evidence),
                'open_requirements': ['calibrated_source_attribution', 'timing_consistency',
                                      'qualified_physical_scenarios', 'astrophysical_FPP_NFPP',
                                      'full_search_reliability', 'scientific_classification_review'],
                'evidence': [{'path': 'evidence/vetting-findings.json',
                              'sha256': __import__('hashlib').sha256(vetting.encoded(evidence)).hexdigest()}]}
        vetting.Draft202012Validator(load(root / 'schemas/vetting-1.0.schema.json'),
                                    format_checker=vetting.FormatChecker()).validate(data)
        existing = folder / 'vetting.json'
        if existing.exists():
            if not unchanged_findings(folder, data, evidence):
                raise ValueError('Existing findings differ; create an explicitly reviewed new snapshot')
            continue
        updated = copy.deepcopy(record)
        major, minor, _ = map(int, record['version'].split('.'))
        updated['version'] = f'{major}.{minor + 1}.0'
        # This new version is a Git disclosure; old immutable releases stay historical.
        updated['publication'].update(state='disclosed', release_url=None, doi=None)
        updated['evidence'] += ['vetting.json', 'evidence/vetting-findings.json']
        updated['history'].append({'date': args.assessed_utc[:10], 'version': updated['version'],
            'change': 'Publish dated light-curve/catalogue warnings, source/physical diagnostic coverage '
                      'and independent progress/assessment axes as a Git disclosure. Previous release '
                      'metadata retained in vetting evidence; disposition and first disclosure preserved.'})
        catalogue.schema_validator().validate(updated)
        prepared.append((folder, updated, data, evidence))
    if omitted_sources != allowed_nonpublic:
        raise ValueError('Declared nonpublic source exclusions differ from input signals')
    return prepared, references, sorted(set(controls_omitted)), sorted(omitted_sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=catalogue.ROOT)
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--assessed-utc', default=datetime.now(UTC).isoformat())
    for name in ('screen-run', 'lightcurve-run', 'catalogue-run'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('source-snapshot', 'source-batch', 'offset-run'):
        parser.add_argument('--' + name, type=Path, action='append', default=[])
    parser.add_argument('--source-warning', action='append', default=[])
    parser.add_argument('--nonpublic-signal', action='append', default=[])
    parser.add_argument('--physical-report', type=Path)
    args = parser.parse_args()
    catalogue.ROOT = args.root.resolve()
    prepared, references, omitted, omitted_sources = prepare(args)
    # All inputs and identities are checked before mutating a dossier.
    for folder, record, data, evidence in prepared:
        write(folder / 'candidate.json', record)
        write(folder / 'vetting.json', data)
        write(folder / 'evidence/vetting-findings.json', evidence)
        readme = folder / 'README.md'
        original = readme.read_text(); split = original.find('\n\n')
        block = ('\n\n## Current vetting status\n\n'
                 f'Assessed {data["assessed_utc"]}. **Progress: {data["progress"]["stage"]}; '
                 'scientific assessment: unclassified**.\n\n'
                 f'Initial screen: **{data["initial_screen"]["outcome"]}**. '
                 f'Warning flags: {", ".join(data["warnings"]) or "none in the published initial screen"}. '
                 'No initial warning does not establish a planet candidate.\n\n'
                 '[Dated measurements, catalogue matches and source/physical outcomes](evidence/vetting-findings.json) · '
                 '[Structured status](vetting.json) · [Category definitions](../../docs/classification.md).\n\n')
        readme.write_text(original[:split] + block + original[split:])
        old = load(folder / 'evidence-manifest.json')
        seal(folder, {x['path']: x['source_sha256'] for x in old['files'] if 'source_sha256' in x})
    records = catalogue.records()
    (catalogue.ROOT / 'catalogue.json').write_bytes(catalogue.index_bytes(records))
    summary = vetting.refresh(records, catalogue.ROOT)
    destination = catalogue.ROOT / 'assessments' / args.snapshot
    if prepared:
        write(destination / 'receipt.json', {'assessed_utc': args.assessed_utc,
            'updated_records': len(prepared), 'source_runs': references,
            'physical_recovery_controls_not_in_public_cohort': omitted,
            'completed_source_signals_not_in_public_cohort': omitted_sources,
            'records': [{'signal_id': r['id'], 'version': r['version'],
                'vetting_sha256': sha(catalogue.ROOT / 'candidates' / r['id'] / 'vetting.json'),
                'findings_sha256': sha(catalogue.ROOT / 'candidates' / r['id'] / 'evidence/vetting-findings.json')}
                for r in records],
            'scope': 'Dated warnings/progress only; no scientific classification promotion',
            'summary': summary})
    print(__import__('json').dumps({'updated_records': len(prepared), 'summary': summary}))


if __name__ == '__main__':
    main()
