"""Stage sealed survey follow-up, preserving the whole upstream cohort and warnings."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import catalogue
from batch_release import safe_name
from export_batch import load, public, seal, sha, write
import vetting


def prepare(root, batch, source):
    batch = safe_name(batch)
    manifest = load(source / 'manifest.json')
    if manifest.get('ok') is not True or manifest['command'] != 'vet-survey-followup-report':
        raise ValueError('Need a successful sealed survey follow-up report')
    for name, checksum in manifest['outputs'].items():
        if sha(source / name) != checksum:
            raise ValueError('Follow-up evidence changed')
    summary = load(source / 'summary.json')
    label = summary.get('label', 'Run 6 follow-up')
    provenance_key = summary.get('provenance_key', 'run6_followup')
    findings = load(source / 'findings.json')
    cohort = load(source / 'cohort.json')
    ledger = load(root / 'batches' / batch / 'outcomes.json')['outcomes']
    if any(c.get('signal_id') for c in cohort) and not all(c.get('signal_id') for c in cohort):
        raise ValueError('Signal-keyed cohort cannot contain anonymous rows')
    key = 'signal_id' if cohort and all(c.get('signal_id') for c in cohort) else 'tic'
    if (len(cohort) != summary['cohort_count'] or
            len({c[key] for c in cohort}) != len(cohort) or
            dict(Counter(c['legacy_class'] for c in cohort)) != summary['original_class_counts']):
        raise ValueError('Whole upstream cohort is not conserved')
    if (len(findings) != summary['fresh_followup_count'] or
            {f['signal_id'] for f in findings} != {
                r['signal_id'] for r in ledger if r.get('assessment_sha256')}):
        raise ValueError('Follow-up and disclosure ledger differ')
    if len({f['signal_id'] for f in findings}) != len(findings):
        raise ValueError('Duplicate follow-up signal')
    for value in (summary, findings, cohort):
        vetting.safe_public(value)
    folder = root / 'batches' / batch
    if (folder / 'triage-cohort.json').exists():
        raise ValueError('Immutable follow-up already imported')
    chosen = {r['signal_id']: r for r in ledger if r['route'] == 'provisional_signal_record'}
    prepared = []
    for f in findings:
        sid = f['signal_id']
        if sid not in chosen:
            continue
        candidate = root / 'candidates' / sid
        record = load(candidate / 'candidate.json')
        if record['target']['tic'] != f['tic'] or chosen[sid]['assessment_sha256'] != f['assessment_sha256']:
            raise ValueError('Follow-up identity or assessment differs')
        ep = f['ephemeris']
        if (ep['period_d'] != record['signal']['period_d']['value'] or
                ep['epoch_bjd_tdb'] != record['signal']['epoch_bjd_tdb']):
            raise ValueError('Follow-up uses a different ephemeris')
        warnings = sorted(k for k, value in f['flags'].items() if value)
        priority = 'diagnostic_warning_review' if warnings else 'incomplete_diagnostics'
        evidence = {
            'signal_id': sid, 'assessed_utc': manifest['finished_utc'],
            'screen': {'priority': priority, 'all_joined_checks_available': False},
            'lightcurve': {'flags': f['flags']},
            'catalogues': {'binary_catalogue_warning': False, 'ruwe_warning': False,
                'coverage': 'Saved 60-arcsec binary/variable queries have no match hypothesis here; '
                            'complete catalogue coverage and RUWE screening remain unqualified.'},
            'followup': public(f),
            'limits': summary['limits'],
            'source_run': manifest['run_id'], 'source_revision': manifest['git']['commit'],
        }
        stages = dict.fromkeys(vetting.STAGES, 'not_started')
        stages.update(screening='partial', source_vetting='partial')
        data = {'schema_version': '1.1', 'signal_id': sid,
            'assessed_utc': manifest['finished_utc'],
            'progress': {'stage': 'source_vetting', 'stages': stages},
            'scientific_assessment': {'status': 'unclassified', 'planet_probability': None,
                'basis': 'Fresh signed diagnostics and legacy pixel rankings; physical host, '
                         'timing qualification and planetary interpretation remain unresolved.',
                'review_evidence': []},
            'initial_screen': {'outcome': 'warnings' if warnings else 'incomplete',
                               'all_checks_available': False},
            'warnings': warnings,
            'open_requirements': ['calibrated_source_attribution', 'timing_consistency',
                'qualified_physical_scenarios', 'astrophysical_FPP_NFPP',
                'full_search_reliability', 'scientific_classification_review',
                'complete_binary_variable_catalogue_coverage'],
            'evidence': []}
        prepared.append((candidate, record, evidence, data))
    for candidate, record, evidence, data in prepared:
        write(candidate / 'evidence/vetting-findings.json', evidence)
        data['evidence'] = [{'path': 'evidence/vetting-findings.json',
                             'sha256': sha(candidate / 'evidence/vetting-findings.json')}]
        write(candidate / 'vetting.json', data)
        record['evidence'].extend(['vetting.json', 'evidence/vetting-findings.json'])
        record['provenance']['runs'][provenance_key] = manifest['run_id']
        record['provenance']['source_revisions'][provenance_key] = manifest['git']['commit']
        write(candidate / 'candidate.json', record)
        with (candidate / 'README.md').open('a') as stream:
            stream.write(f'\n## {label}\n\n'
                f'Fresh checks use {evidence["followup"]["primary_sectors"]} timing-qualified '
                'primary sectors, with one reduction per sector. '
                f'Diagnostic warning flags: {", ".join(data["warnings"]) or "none in this subset"}. '
                '[Detailed results and missing checks](evidence/vetting-findings.json). '
                'These descriptive flags do not assign a planet probability. '
                'The initial screen remains incomplete and source attribution unresolved.\n')
        previous = load(candidate / 'evidence-manifest.json')
        seal(candidate, {f['path']: f['source_sha256'] for f in previous['files'] if 'source_sha256' in f})
    write(folder / 'triage-cohort.json', public(cohort))
    write(folder / 'followup-findings.json', public(findings))
    write(folder / 'followup-summary.json', public(summary))
    write(folder / 'followup-source-receipt.json', {'run_id': manifest['run_id'],
        'source_revision': manifest['git']['commit'], 'finished_utc': manifest['finished_utc'],
        'manifest_sha256': sha(source / 'manifest.json'), 'outputs': manifest['outputs']})
    return {'cohort': len(cohort), 'dossiers_updated': len(prepared),
            'records_with_diagnostic_warnings': summary['records_with_diagnostic_warnings']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--batch', required=True)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    import json
    print(json.dumps(prepare(args.root, args.batch, args.source)))


if __name__ == '__main__':
    main()
