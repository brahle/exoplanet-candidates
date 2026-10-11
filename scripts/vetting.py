"""Validate the independent vetting axes and generate stable-path browsing views."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

STAGES = ('screening', 'source_vetting', 'physical_vetting', 'followup', 'validation', 'confirmation')
ASSESSMENTS = {
    'unclassified': 'unclassified_transit_like_signal',
    'candidate': 'planet_candidate',
    'likely_planet': 'planet_candidate',
    'false_positive': 'false_positive',
    'validated_planet': 'validated_planet',
    'confirmed_planet': 'confirmed_planet',
    'known_signal': 'known_signal',
}
PROCESS = ('queue', 'screening', 'screened', *STAGES[1:])
INITIAL = ('warnings', 'no_initial_warnings', 'incomplete')


def load(path):
    return json.loads(path.read_text())


def encoded(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()


def safe_public(value):
    text = json.dumps(value, allow_nan=False)
    if re.search(r'(/Users/|/home/|/private/|/tmp/|ivanka|dubravka|nexus\.brahle|'
                 r'gitea\.brahle|Bearer\s|ssh://)', text, re.I):
        raise ValueError('Private reference in public vetting evidence')


def progress_stage(stages):
    for stage in reversed(STAGES[1:]):
        if stages[stage] != 'not_started':
            return stage
    return {'not_started': 'queue', 'complete': 'screened'}.get(stages['screening'], 'screening')


def initial_outcome(screen):
    return {
        'diagnostic_warning_review': 'warnings',
        'source_followup_without_these_warnings': 'no_initial_warnings',
        'incomplete_diagnostics': 'incomplete',
    }[screen['priority']]


def warning_codes(evidence):
    lightcurve = evidence.get('lightcurve') or {}
    binary = evidence['catalogues']
    codes = [k for k, value in lightcurve.get('flags', {}).items() if value is True]
    if binary['binary_catalogue_warning']:
        codes.append('binary_catalogue_match')
    if binary['ruwe_warning']:
        codes.append('elevated_ruwe')
    if evidence.get('external_report'):
        codes.append('external_adverse_report')
    if evidence.get('source_warning_reviewed'):
        codes.append('off_target_diagnostic')
    return sorted(codes)


def validate(record, folder, root):
    path = folder / 'vetting.json'
    if not path.exists():
        return None  # Older dossiers are not assigned invented progress.
    data = load(path)
    schema = load(root / 'schemas/vetting-1.0.schema.json')
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
    safe_public(data)
    if data['signal_id'] != record['id']:
        raise ValueError('Vetting signal identity differs')
    if progress_stage(data['progress']['stages']) != data['progress']['stage']:
        raise ValueError('Vetting progress stage differs from recorded work')
    assessment = data['scientific_assessment']
    if ASSESSMENTS[assessment['status']] != record['assessment']['disposition']:
        raise ValueError('Vetting assessment differs from dossier disposition')
    if assessment['status'] != 'unclassified' and not assessment['review_evidence']:
        raise ValueError('Scientific classification requires a documented review')
    for relative in assessment['review_evidence']:
        target = (folder / relative).resolve()
        if not target.is_relative_to(folder.resolve()) or not target.is_file():
            raise ValueError('Missing or unsafe classification evidence')
    for item in data['evidence']:
        target = (folder / item['path']).resolve()
        if not target.is_relative_to(folder.resolve()) or not target.is_file():
            raise ValueError('Missing or unsafe vetting evidence')
        if hashlib.sha256(target.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Vetting evidence hash changed')
        safe_public(load(target))
    evidence = load(folder / 'evidence/vetting-findings.json')
    if evidence['signal_id'] != record['id']:
        raise ValueError('Vetting findings identity differs')
    if initial_outcome(evidence['screen']) != data['initial_screen']['outcome']:
        raise ValueError('Initial screen category differs')
    if evidence['screen']['all_joined_checks_available'] != data['initial_screen']['all_checks_available']:
        raise ValueError('Initial screen completeness differs')
    if sorted(data['warnings']) != warning_codes(evidence):
        raise ValueError('Warning tags differ from saved evidence')
    if (data['initial_screen']['outcome'] == 'no_initial_warnings' and
            not data['initial_screen']['all_checks_available']):
        raise ValueError('Missing checks cannot become an initial-screen pass')
    if data['progress']['stages']['source_vetting'] == 'complete':
        if record['assessment']['source_localisation']['status'] != 'supported':
            raise ValueError('Diagnostic execution cannot complete source qualification')
    return data


def index_rows(records, root):
    rows = []
    for record in records:
        folder = root / 'candidates' / record['id']
        data = validate(record, folder, root)
        if data is not None:
            rows.append({**data, 'novelty': record['novelty']['status'],
                         'period_d': record['signal']['period_d']['value'],
                         'path': f'candidates/{record["id"]}/README.md'})
    return rows


def table(rows, prefix):
    if not rows:
        return 'No records currently meet this category.\n'
    lines = ['| Signal | Period (d) | Progress | Assessment | Warning flags |',
             '|---|---:|---|---|---|']
    for row in rows:
        lines.append(f'| [{row["signal_id"]}]({prefix}{row["path"]}) | {row["period_d"]:.8f} | '
                     f'{row["progress"]["stage"]} | {row["scientific_assessment"]["status"]} | '
                     f'{", ".join(row["warnings"]) or "none in published screening"} |')
    return '\n'.join(lines) + '\n'


def generated_files(records, root):
    rows = index_rows(records, root)
    shortlist = [x for x in rows if x['initial_screen']['outcome'] == 'no_initial_warnings'
                 and not x['warnings'] and x['novelty'] != 'previously_reported']
    summary = {
        'records': len(rows), 'dossiers_without_vetting_record': len(records) - len(rows),
        'progress': dict(Counter(x['progress']['stage'] for x in rows)),
        'scientific_assessment': dict(Counter(x['scientific_assessment']['status'] for x in rows)),
        'initial_screen_all': dict(Counter(x['initial_screen']['outcome'] for x in rows)),
        'initial_screen_without_prior_reports': dict(Counter(
            x['initial_screen']['outcome'] for x in rows if x['novelty'] != 'previously_reported')),
        'current_warning_records': sum(bool(x['warnings']) for x in rows),
        'followup_shortlist_without_published_warnings': len(shortlist),
        'planet_probability': None,
    }
    files = {'vetting-catalogue.json': encoded({'schema_version': '1.0', 'summary': summary, 'signals': rows})}
    groups = []
    for stage in PROCESS:
        groups.append((f'process/{stage.replace("_", "-")}', stage,
                       [x for x in rows if x['progress']['stage'] == stage]))
    for assessment in ASSESSMENTS:
        groups.append((f'assessment/{assessment.replace("_", "-")}', assessment,
                       [x for x in rows if x['scientific_assessment']['status'] == assessment]))
    for outcome in INITIAL:
        groups.append((f'initial-screen/{outcome.replace("_", "-")}', outcome,
                       [x for x in rows if x['initial_screen']['outcome'] == outcome]))
    groups += [('shortlist', 'Follow-up shortlist without published warnings', shortlist),
               ('warnings', 'Current warning flags', [x for x in rows if x['warnings']]),
               ('previously-reported', 'Previously reported', [x for x in rows if x['novelty'] == 'previously_reported'])]
    lines = ['# Browse signals\n',
             'Dossiers keep stable paths. These folders are generated views of two independent axes: '
             '**work performed** and **scientific assessment**. Warnings and novelty are separate.\n',
             'A completed diagnostic calculation is not a qualified scientific pass. '
             '“No initial warnings” does not mean “likely planet.”\n',
             '[Definitions and promotion rules](../docs/classification.md) · '
             '[Dated findings](../docs/vetting-findings-2026-10-11.md) · '
             '[Machine-readable index](../vetting-catalogue.json)\n',
             '| View | Records |\n|---|---:|']
    for path, title, selected in groups:
        prefix = '../../../' if '/' in path else '../../'
        content = (f'# {title.replace("_", " ").capitalize()}\n\n'
                   f'{len(selected)} records. This is a generated view, assessed per record. '
                   f'[Classification definitions]({prefix}docs/classification.md).\n\n' + table(selected, prefix))
        files[f'browse/{path}/README.md'] = content.encode()
        lines.append(f'| [{title.replace("_", " ")}]({path}/README.md) | {len(selected)} |')
    files['browse/README.md'] = ('\n'.join(lines) + '\n').encode()
    return files


def refresh(records, root, check=False):
    files = generated_files(records, root)
    existing = {p.relative_to(root).as_posix() for p in (root / 'browse').rglob('*') if p.is_file()}
    expected = {p for p in files if p.startswith('browse/')}
    if existing - expected:
        raise ValueError('Unexpected files in generated browse views')
    for relative, content in files.items():
        path = root / relative
        if check:
            if not path.exists() or path.read_bytes() != content:
                raise ValueError(f'Stale vetting view: {relative}; run scripts/catalogue.py build')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return json.loads(files['vetting-catalogue.json'])['summary']
