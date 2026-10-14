"""Prepare provisional signal dossiers from pinned batch receipts; never publish."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import shutil
import tempfile
import tomllib


def load(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def public(value):
    """Remove private storage references, keeping scientific values and product names."""
    if isinstance(value, dict):
        return {k: public(v) for k, v in value.items()
                if k not in {'relative_path', 'arrays_file', 'primary_header', 'lightcurve_header',
                             'server_configuration_sha256', 'cache_key', 'input_sha256'}}
    if isinstance(value, list):
        return [public(v) for v in value]
    if isinstance(value, str):
        if value.startswith(('/Users/', '/home/', '/private/', '/tmp/')):
            return Path(value).name
        if re.search(r'(/Users/|/home/|ivanka|dubravka|nexus\.brahle)', value, re.I):
            raise ValueError('Private reference embedded in exported text')
    return value


def artifact(stage, name):
    manifest_path = Path(stage['manifest'])
    if sha(manifest_path) != stage['artifacts'][str(manifest_path)]:
        raise ValueError('Stage manifest changed')
    manifest = load(manifest_path)
    path = manifest_path.parent / name
    if not manifest['ok'] or name not in manifest['outputs'] or sha(path) != manifest['outputs'][name]:
        raise ValueError(f'Unverified scientific artifact: {name}')
    return load(path), path, manifest


def scientific_recipe(manifest):
    config = manifest['config'].get('content', {}).get('science_config')
    if not config:
        return None
    # Read the recipe from the recorded numerical source revision, not today's working tree.
    root = Path(config).parents[2]
    relative = 'configs/vetting/' + Path(config).name
    data = subprocess.run(['git', 'show', manifest['git']['commit'] + ':' + relative],
                          cwd=root, check=True, capture_output=True).stdout
    return {'filename': Path(config).name, 'sha256': hashlib.sha256(data).hexdigest(),
            'source_revision': manifest['git']['commit'], 'content': tomllib.loads(data.decode())}


def route(ephemeris, photometry, robustness, check, prior):
    """Disclosure rule, not a calibrated scientific classification or discovery claim."""
    if check.get('error') or not check.get('result', {}).get('checked_sources'):
        return 'catalogue_check_failed'
    if prior or check['result'].get('near_matches') or check['result'].get('variable_matches'):
        return 'prior_report_or_match_hypothesis'
    if check['result'].get('status') != 'no_match_in_checked_sources':
        return 'catalogue_status_unresolved'
    if not ephemeris.get('adopted'):
        return 'no_adopted_diagnostic_ephemeris'
    aggregate = photometry['aggregates']
    if len(aggregate) != 2 or any((a.get('depth_ppm') or 0) <= 0 for a in aggregate):
        return 'nonpositive_or_unavailable_baseline_dip'
    sectors = {e['sector'] for e in photometry['events'] if e.get('usable') and e['baseline_order'] == 1}
    if len(sectors) < 2:
        return 'insufficient_multisector_evidence'
    leave = robustness.get('minimum_leave_sector_snr')
    if leave is None or leave <= 0:
        return 'dip_not_positive_in_all_sector_leaveouts'
    return 'provisional_signal_record'


def novelty_text(check, previously_reported=False):
    radius = check['arguments']['cone_radius_arcsec']
    finding = ('The existing public dossier for this same stable signal ID was returned. '
               'This is a re-detection and new assessment of a previously reported signal.'
               if previously_reported else 'No matching record was returned in those indexed checks.')
    return f'''# Dated catalogue check

MCP checked {check['checked_utc']} at the adopted diagnostic period, using the recorded
{radius:g}-arcsecond cone and period/harmonic matching arguments. The [receipt](evidence/catalogue-check.json)
lists checked snapshots, source timestamps and declared unindexed sources. {finding}

[Additional saved hypotheses](evidence/direct-catalogue-hypotheses.json) retain any direct-source
matches supplied to this export. An empty list does not attest that a direct catalogue query
succeeded or was performed. The batch catalogue-snapshots.json lists direct-screen coverage;
an empty snapshot list means no direct-screen receipt was supplied.

Literature completeness, catalogue gaps, proper-motion/epoch reconciliation,
physical-host attribution and discovery priority remain unresolved.
'''


def seal(folder, sources, signal_id=None):
    files = []
    for p in sorted(folder.rglob('*')):
        if p.is_file() and p != folder / 'evidence-manifest.json':
            relative = p.relative_to(folder).as_posix()
            item = {'path': relative, 'bytes': p.stat().st_size, 'sha256': sha(p),
                    'export_mode': 'derived public record'}
            if relative in sources:
                item.update(source_sha256=sources[relative], export_mode='scientific JSON with private storage references removed')
            files.append(item)
    write(folder / 'evidence-manifest.json', {'schema_version': '1.0', 'candidate': signal_id or folder.name, 'files': files})


def dossier(destination, assessment, check, documents, prior, date, review=None, previously_reported=False):
    novelty_note = novelty_text(check, previously_reported)
    seed = assessment['signal']; ep = documents['ephemeris.json'][0]
    if not re.fullmatch(r'tic-[0-9]+-s[0-9]{2}', seed['id']) or not seed['id'].startswith(f"tic-{seed['tic']}-"):
        raise ValueError('Unsafe or inconsistent signal identity')
    fitted = ep['ephemeris']; cov = ep['epoch_period_covariance']
    phot = documents['photometry.json'][0]
    depth = next(a for a in phot['aggregates'] if a['baseline_order'] == 1)
    folder = destination / 'candidates' / seed['id']
    if folder.exists():
        raise ValueError(f'Refusing to overwrite a signal: {seed["id"]}')
    folder.mkdir(parents=True)
    sources = {}
    for name, (value, path, manifest) in documents.items():
        relative = 'evidence/' + name
        write(folder / relative, public(value)); sources[relative] = sha(path)
    write(folder / 'evidence/catalogue-check.json', public(check))
    write(folder / 'evidence/direct-catalogue-hypotheses.json', public(prior))
    if review is not None:
        write(folder / 'review.json', public(review))
    inputs = documents['inputs.json'][0]
    write(folder / 'inputs.json', public(inputs))
    write(folder / 'analysis-settings.json', {
        'disclosure_rule': 'Positive under both baseline orders, >=2 usable sectors, positive all sector leaveouts; no indexed or direct-catalogue match hypothesis.',
        'interpretation': 'Record selection only; no calibrated detection or planet-probability threshold.',
        'immutable_discovery_seed': public(seed),
        'ephemeris_selection': ep['chosen_hypothesis'],
        'original_assessment_sha256': assessment['assessment_sha256'],
        'retained_unresolved_gates': list(assessment['blocking_gates']),
        'science_configuration_hashes': {name: data[2]['config'].get('sha256') for name, data in documents.items()},
        'scientific_recipes': {name: scientific_recipe(data[2]) for name, data in documents.items()},
    })
    limits = ['Preliminary unclassified signal; binary, blend and instrumental explanations remain open.',
              'Conditional diagnostic errors; no calibrated false-alarm or planet probability.',
              'Duration uncertainty unavailable; null is intentional.',
              'Mission clock, host identity, noise coverage and search selection remain unresolved.',
              'All saved event exclusions, failed fits and signed alternative diagnostics are retained.']
    record = {
        'schema_version': '1.1', 'id': seed['id'], 'version': '0.1.0',
        'title': f'TIC {seed["tic"]}: a provisional {fitted["period_d"]:.8f}-day signal',
        'target': {'tic': seed['tic'], 'gaia_dr3': None, 'aliases': ['TIC ' + seed['tic']],
                   'coordinates': {'ra_deg': seed['ra_deg'], 'dec_deg': seed['dec_deg'], 'frame': 'ICRS',
                                   'epoch': 'J2000', 'provenance': 'Saved TIC discovery coordinates; aperture target identity, not a verified eclipsed host.'}},
        'signal': {'period_d': {'value': fitted['period_d'], 'error': math.sqrt(cov[1][1])},
                   'epoch_btjd': {'value': fitted['epoch_bjd_tdb'] - 2457000, 'error': math.sqrt(cov[0][0])},
                   'epoch_bjd_tdb': fitted['epoch_bjd_tdb'], 'bjd_offset': 2457000, 'time_scale': 'TDB',
                   'covariance_epoch_period_d2': cov,
                   'covariance_method': 'Saved local integrated-trapezoid diagnostic Jacobian covariance; conditional and not empirically calibrated.',
                   'duration_h': {'value': fitted['duration_h'], 'error': None},
                   'depth_ppm': {'value': depth['depth_ppm'], 'error': depth['error_ppm']},
                   'model': 'Exposure-integrated diagnostic trapezoid; free event depths and local baseline. Separate linear-baseline box-window aggregate depth.',
                   'sectors': sorted({e['sector'] for e in phot['events'] if e.get('usable') and e['baseline_order'] == 1}),
                   'covered_events': depth['n_events'], 'limits': limits},
        'assessment': {'disposition': 'unclassified_transit_like_signal',
                       'source_localisation': {'status': 'unresolved', 'reason': 'No calibrated physical-host attribution; FITS target identity identifies the aperture only.', 'evidence': ['inputs.json']},
                       'timing_consistency': {'status': 'unresolved', 'reason': 'Signed event profiles retain failures, competing clock/shape hypotheses and conditional errors; independent clock/coverage calibration unfinished.', 'evidence': ['evidence/timing-summary.json', 'evidence/timing-events.json']}},
        'novelty': {'status': 'previously_reported' if previously_reported else 'no_match_in_checked_sources', 'checked_utc': check['checked_utc'],
                    'evidence': ['evidence/catalogue-check.json', 'evidence/direct-catalogue-hypotheses.json', 'NOVELTY.md'],
                    'limits': [('Re-detection of the existing stable signal; no new discovery claim.' if previously_reported else 'No match in listed snapshots, not established discovery priority.'), 'Unindexed literature and catalogue completeness remain unresolved.', 'Coordinates are static; nearby-source exclusion and proper-motion reconciliation remain incomplete.']},
        'provenance': {'analysis_date': date, 'source_revisions': {name[:-5]: data[2]['git']['commit'] for name, data in documents.items()},
                       'runs': {name[:-5]: data[2]['run_id'] for name, data in documents.items()}, 'input_lock': 'inputs.json'},
        'reproducibility': {'level': 'evidence_inspection', 'command': 'uv sync --frozen && uv run python scripts/catalogue.py check',
                            'limits': ['Saved scientific evidence and hashes can be inspected; this does not rerun numerical fits.', 'Exact FITS bytes, complete analysis code/environment and public numerical capsule are not bundled.'],
                            'requirements_for_numerical_release': ['Provide exact inputs, selected source, frozen environment and a verified clean public-input rerun.']},
        'publication': {'state': 'draft', 'first_public_utc': None, 'release_url': None, 'doi': None, 'authors': ['Bruno Rahle']},
        'evidence': ['inputs.json', 'analysis-settings.json', 'README.md', 'NOVELTY.md', 'REPRODUCIBILITY.md'] + sorted(sources) + ['evidence/catalogue-check.json', 'evidence/direct-catalogue-hypotheses.json'],
        'history': [{'date': date, 'version': '0.1.0', 'change': 'Initial evidence-inspection dossier from the reusable batch; all scientific classifications remain provisional.'}],
    }
    write(folder / 'candidate.json', record)
    if review is not None:
        record['evidence'].append('review.json')
        write(folder / 'candidate.json', record)
    rb = assessment['stages']['robustness']['metrics']
    odd_even = rb.get('odd_even_tension_sigma')
    odd_even_text = 'unavailable' if odd_even is None else f'{odd_even:.3g} conditional error units'
    adverse = ('The saved odd/even diagnostic exceeds its recorded three-error-unit flag; '
               'a binary or alternating-depth explanation needs particular attention.'
               if odd_even is not None and abs(odd_even) >= documents['robustness.json'][0]['diagnostic_tension_sigma']
               else 'The saved odd/even diagnostic supplies no definitive classification.')
    (folder / 'README.md').write_text(f'''# TIC {seed['tic']} / {seed['id'].rsplit('-', 1)[1].upper()}

**Provisional unclassified transit-like signal.** Source attribution and timing consistency are unresolved.
Binary, blend and instrumental explanations remain open. This is a dated evidence record, not a verified planet.

Diagnostic period: {fitted['period_d']:.10f} ± {math.sqrt(cov[1][1]):.3g} d.
Epoch: BJD_TDB {fitted['epoch_bjd_tdb']:.8f} ± {math.sqrt(cov[0][0]):.3g} d.
Duration: {fitted['duration_h']:.4f} h (uncertainty unavailable).
Linear-baseline depth: {depth['depth_ppm']:.1f} ± {depth['error_ppm']:.1f} ppm,
from {depth['n_events']} usable events in {len(record['signal']['sectors'])} sectors.
Errors are conditional diagnostic estimates.

Both saved baseline orders give positive aggregate dips. The minimum conditional depth/error
over sector leaveouts is {rb['minimum_leave_sector_snr']:.3g}; it is not a false-alarm probability.
Odd/even depth contrast: {odd_even_text}. {adverse}
The [photometry](evidence/photometry.json) retains unusable events, alternate reductions,
phase controls and timestamp-withheld products. [Robustness](evidence/robustness.json),
[timing](evidence/timing-summary.json) and [alternative signals](evidence/alternative-summary.json)
retain adverse evidence, signed secondary/odd-even/harmonic probes and failures. Strong
secondary or odd/even differences can favour a binary explanation; those probes have not
been calibrated into a definitive classification.

The immutable discovery seed and adopted diagnostic hypothesis are in [settings](analysis-settings.json).
The aperture TIC is not an established physical host; any Gaia DR3 catalogue association
is separate from attribution of the dip.
Read [novelty limits](NOVELTY.md) and [reproduction coverage](REPRODUCIBILITY.md).
''')
    (folder / 'NOVELTY.md').write_text(novelty_note)
    (folder / 'REPRODUCIBILITY.md').write_text('''# Evidence inspection only

Run `uv sync --frozen`, then `uv run python scripts/catalogue.py check`.
This verifies schema, time bookkeeping, covariance and exact exported hashes. It does not
recompute the light curve, source images or fitted event profiles. Original artifact hashes
are in the evidence manifest; private storage references were removed from exported JSON.
Mission product names, exact native-byte hashes and time/exposure conventions are in inputs.json.
A future numerical release needs exact public input bytes, versioned code, frozen environment
and a clean public-input rerun certificate. No planet probability or discovery priority is certified.
''')
    seal(folder, sources)


def verified_reviews(path, report_path):
    document = load(path)
    if document['report_sha256'] != sha(report_path):
        raise ValueError('Reviews refer to another report')
    result = {}
    for row in document['reviews']:
        identity = {k: v for k, v in row.items() if k not in {'review_id', 'reviewed_utc'}}
        digest = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        if row['review_id'] != digest or row['signal_id'] in result:
            raise ValueError('Invalid or duplicate review identity')
        result[row['signal_id']] = row
    return result


def prepare(report_path, checks_path, screens, destination, batch, reviews_path):
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', batch):
        raise ValueError('Unsafe batch identifier')
    if (destination / 'batches' / batch).exists():
        raise ValueError('Immutable publication batch already exists')
    report_manifest = load(report_path.parent / 'manifest.json')
    if not report_manifest['ok'] or report_manifest['outputs'][report_path.name] != sha(report_path):
        raise ValueError('Batch report changed or failed')
    report = load(report_path)
    assessments = {a['signal']['id']: a for a in report['assessments']}
    if len(assessments) != len(report['assessments']):
        raise ValueError('Duplicate assessment signal')
    terminal = report.get('terminal_outcomes', [
        {'row_id': sid, 'signal_id': sid, 'tic': a['signal']['tic'], 'route': 'completed',
         'assessment_sha256': a['assessment_sha256']} for sid, a in assessments.items()])
    allowed = {'completed', 'carried_forward', 'identity_hold', 'intake_hold', 'execution_failed'}
    if any(r['route'] not in allowed for r in terminal):
        raise ValueError('Publication waits for terminal outcomes; catalogue failures are non-terminal')
    row_ids = [r.get('row_id', r['signal_id']) for r in terminal]
    if len(set(row_ids)) != len(row_ids) or set(assessments) != {
            r['signal_id'] for r in terminal if r['route'] in {'completed', 'carried_forward'}}:
        raise ValueError('Terminal outcomes do not conserve assessments')
    for row in terminal:
        if row['route'] in {'identity_hold', 'intake_hold', 'execution_failed'} and not row.get('reason'):
            raise ValueError('Terminal hold or failure needs a reason')
        if row['route'] == 'execution_failed' and row.get('attempts', 0) < 3:
            raise ValueError('Execution failure must exhaust the declared bounded retries')
        if row['signal_id'] in assessments and row.get('assessment_sha256') != assessments[row['signal_id']]['assessment_sha256']:
            raise ValueError('Terminal outcome refers to another assessment')
    reviews = verified_reviews(reviews_path, report_path)
    for assessment in report['assessments']:
        identity = {k: v for k, v in assessment.items() if k != 'assessment_sha256'}
        if hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest() != assessment['assessment_sha256']:
            raise ValueError('Assessment content differs from its seal')
        for stage in assessment['stages'].values():
            for path, checksum in stage.get('artifacts', {}).items():
                if sha(path) != checksum:
                    raise ValueError('Assessment artifact changed')
        review = reviews.get(assessment['signal']['id'])
        if (not review or review['assessment_sha256'] != assessment['assessment_sha256'] or
                review['disposition'] != 'unclassified_transit_like_signal' or
                review['publication_tier'] != 'evidence_inspection'):
            raise ValueError('Provisional export requires a matching unclassified assessment review')
    rows = [json.loads(line) for line in checks_path.read_text().splitlines()]
    checks = {r['signal_id']: r for r in rows}
    if len(checks) != len(rows) or set(checks) != {a['signal']['id'] for a in report['assessments']}:
        raise ValueError('Fresh checks must account for exactly every batch signal once')
    if any(r.get('error') or not r.get('result', {}).get('checked_sources') or
           r['result'].get('status') not in {'no_match_in_checked_sources', 'near_matches_found', 'variable_star_match'}
           for r in rows):
        raise ValueError('A failed catalogue check is non-terminal')
    hypotheses = {}
    snapshots = []
    for path in screens:
        manifest = load(path.parent / 'manifest.json')
        if not manifest['ok'] or manifest['outputs'][path.name] != sha(path):
            raise ValueError('Direct catalogue screen changed or failed')
        snapshots.append({'run_id': manifest['run_id'], 'checked_utc': manifest['finished_utc'],
                          'source_revision': manifest['git']['commit'], 'hypotheses_sha256': sha(path),
                          'source_inventory': public(load(path.parent / 'source-inventory.json')),
                          'screen_summary': public(load(path.parent / 'summary.json'))})
        for line in path.read_text().splitlines():
            row = json.loads(line); hypotheses.setdefault(row['signal_id'], []).append(row)
    outcomes = []; date = datetime.now(timezone.utc).date().isoformat()
    # Validate and build everything before committing any destination directory.
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.export-', dir=destination) as temporary:
        staging = Path(temporary)
        _prepare_rows(terminal, assessments, checks, hypotheses, reviews, staging,
                      destination, batch, date, outcomes)
        counts = dict(Counter(r['route'] for r in outcomes))
        write(staging / 'batches' / batch / 'outcomes.json', {'batch': batch, 'date': date,
            'count': len(outcomes), 'routes': counts, 'report_sha256': sha(report_path),
            'fresh_checks_sha256': sha(checks_path), 'direct_screen_sha256': [sha(p) for p in screens],
            'occurrences': public(report.get('occurrences', [])), 'outcomes': outcomes})
        write(staging / 'batches' / batch / 'catalogue-snapshots.json', snapshots)
        write(staging / 'batches' / batch / 'reviews.json', public(load(reviews_path)))
        for folder in sorted((staging / 'candidates').glob('*')):
            final = destination / 'candidates' / folder.name
            if final.exists():
                raise ValueError('Refusing to overwrite a signal')
        for folder in sorted((staging / 'candidates').glob('*')):
            final = destination / 'candidates' / folder.name
            final.parent.mkdir(parents=True, exist_ok=True)
            folder.rename(final)
        final_batch = destination / 'batches' / batch
        final_batch.parent.mkdir(parents=True, exist_ok=True)
        (staging / 'batches' / batch).rename(final_batch)
    print(json.dumps({'count': len(outcomes), 'routes': counts}))


def _prepare_rows(terminal, assessments, checks, hypotheses, reviews, staging,
                  destination, batch, date, outcomes):
    for occurrence in terminal:
        sid = occurrence['signal_id']
        row = public(dict(occurrence))
        if occurrence['route'] in {'identity_hold', 'intake_hold', 'execution_failed'}:
            outcomes.append(row)
            continue
        a = assessments[sid]
        prior = hypotheses.get(sid, [])
        check = checks[sid]
        for field in ('ra_deg', 'dec_deg'):
            if field not in a['signal'] or not math.isclose(check[field], a['signal'][field], rel_tol=0, abs_tol=1e-12):
                raise ValueError('Catalogue check is for another position')
        if 'tic' in check and str(check['tic']) != a['signal']['tic']:
            raise ValueError('Catalogue target differs')
        row.update(assessment_sha256=a['assessment_sha256'], catalogue_check=public(check),
                   direct_catalogue_hypotheses=public(prior))
        if occurrence['route'] == 'carried_forward':
            row['route'] = 'carried_forward'
            outcomes.append(row)
            continue
        near = check['result'].get('near_matches', [])
        self_report = bool(near) and (destination / 'candidates' / sid).exists() and all(
            m.get('sources') == ['git:brahle/exoplanet-candidates'] and
            sid in m.get('source_keys', []) and str(m.get('tic_id')) == a['signal']['tic']
            for m in near)
        existing = (destination / 'candidates' / sid).exists()
        matched = prior or (near and not self_report) or check['result'].get('variable_matches')
        if matched and not existing:
            row['route'] = 'prior_report_or_match_hypothesis'
            outcomes.append(row)
            continue
        docs = {}
        for stage, names in {'acquisition': ['inputs.json'], 'photometry': ['ephemeris.json', 'photometry.json'],
                             'robustness': ['robustness.json'], 'timing': ['timing-summary.json', 'timing-events.json', 'timing-controls.json'],
                             'alternatives': ['alternative-summary.json']}.items():
            for name in names:
                docs[name] = artifact(a['stages'][stage], name)
        ep, phot = docs['ephemeris.json'][0], docs['photometry.json'][0]
        expected = ep['ephemeris'] if ep.get('adopted') else a['signal']
        for field in ('ra_deg', 'dec_deg', 'period_d'):
            if not math.isclose(check[field], expected[field], rel_tol=0, abs_tol=1e-12):
                raise ValueError('Catalogue check is for another ephemeris/position')
        routing_check = check
        if self_report:
            routing_check = dict(check, result=dict(check['result'], near_matches=[], status='no_match_in_checked_sources'))
            row['novelty'] = 'previously_reported'
        decision = route(ep, phot, a['stages']['robustness'].get('metrics', {}), routing_check, prior)
        row['route'] = decision
        if decision == 'provisional_signal_record':
            dossier(staging, a, check, docs, prior, date, reviews[sid], self_report)
            if (destination / 'candidates' / sid).exists():
                old = destination / 'candidates' / sid
                row.update(route='amendment_pending', previous_manifest_sha256=sha(old / 'evidence-manifest.json'))
                amendment = staging / 'batches' / batch / 'amendments' / sid
                amendment.parent.mkdir(parents=True, exist_ok=True)
                (staging / 'candidates' / sid).rename(amendment)
                row['amendment_manifest_sha256'] = sha(amendment / 'evidence-manifest.json')
        elif existing:
            # Adverse or inconclusive new evidence must also reach the existing
            # record. Retain its prior measurements, explicitly identified as
            # such, rather than inventing a replacement fit.
            amendment = staging / 'batches' / batch / 'amendments' / sid
            assessment_amendment(destination / 'candidates' / sid, amendment,
                                 batch, a, check, docs, prior, reviews[sid], decision)
            row.update(route='amendment_pending', assessment_route=decision,
                       amendment_kind='assessment_only',
                       previous_manifest_sha256=sha(destination / 'candidates' / sid / 'evidence-manifest.json'),
                       amendment_manifest_sha256=sha(amendment / 'evidence-manifest.json'))
        outcomes.append(row)


def assessment_amendment(old_folder, amendment, batch, assessment, check, docs, prior, review, decision):
    """Stage negative findings while keeping earlier measurements/provenance intact."""
    old = load(old_folder / 'candidate.json')
    if old['assessment']['disposition'] != 'unclassified_transit_like_signal':
        raise ValueError('A stronger existing classification needs a separate scientific review')
    shutil.copytree(old_folder, amendment)
    relative = 'evidence/progressive/' + batch
    hashes = {f['path']: f['source_sha256'] for f in load(old_folder / 'evidence-manifest.json')['files'] if 'source_sha256' in f}
    for name, (value, source, _) in docs.items():
        write(amendment / relative / name, public(value))
        hashes[relative + '/' + name] = sha(source)
    write(amendment / relative / 'catalogue-check.json', public(check))
    write(amendment / relative / 'direct-hypotheses.json', public(prior))
    write(amendment / relative / 'review.json', public(review))
    write(amendment / relative / 'assessment.json', {
        'signal_id': old['id'], 'assessment_sha256': assessment['assessment_sha256'],
        'route': decision, 'blocking_gates': assessment['blocking_gates'],
        'measurement_policy': 'Root signal values remain dated measurements from the previous dossier; new diagnostics do not supply a selected replacement fit.'})
    additions = [relative + '/' + name for name in docs] + [relative + '/' + n for n in
        ['catalogue-check.json', 'direct-hypotheses.json', 'review.json', 'assessment.json']]
    old['evidence'] = list(dict.fromkeys(old['evidence'] + additions))
    old['novelty'].update(status='unresolved', checked_utc=check['checked_utc'],
                         evidence=list(dict.fromkeys(old['novelty']['evidence'] +
                            [relative + '/catalogue-check.json', relative + '/direct-hypotheses.json'])))
    old['novelty']['limits'].append('New assessment and catalogue hypotheses retained; prior novelty interpretation must be reviewed.')
    write(amendment / 'candidate.json', old)
    settings = load(amendment / 'analysis-settings.json')
    settings['prior_measurement_assessment_sha256'] = settings['original_assessment_sha256']
    settings['original_assessment_sha256'] = assessment['assessment_sha256']
    settings['latest_assessment_only'] = relative + '/assessment.json'
    write(amendment / 'analysis-settings.json', settings)
    with (amendment / 'README.md').open('a') as stream:
        stream.write('\n## New adverse or inconclusive assessment\n\n'
            f'Outcome: `{decision}`. [Latest dated findings]({relative}/assessment.json). '
            'The signal measurements above remain the previous dated measurements; '
            'they are not estimates from this new assessment. New catalogue hypotheses '
            'and all supporting/adverse diagnostic files are retained. Scientific '
            'classification remains unclassified.\n')
    seal(amendment, hashes)


def amend(destination, batch, signal_id):
    """Deliberately apply a staged, reviewed amendment while preserving prior bytes."""
    import catalogue
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', batch) or not re.fullmatch(r'tic-\d+-s\d{2,}', signal_id):
        raise ValueError('Unsafe amendment identity')
    batch_dir = destination / 'batches' / batch
    rows = load(batch_dir / 'outcomes.json')['outcomes']
    row = next(r for r in rows if r['signal_id'] == signal_id)
    if row['route'] != 'amendment_pending':
        raise ValueError('No reviewed amendment pending for this signal')
    receipt = batch_dir / 'amendment-receipts' / (signal_id + '.json')
    if receipt.exists():
        raise ValueError('Immutable amendment already applied')
    old_folder = destination / 'candidates' / signal_id
    source = batch_dir / 'amendments' / signal_id
    if (sha(old_folder / 'evidence-manifest.json') != row['previous_manifest_sha256'] or
            sha(source / 'evidence-manifest.json') != row['amendment_manifest_sha256']):
        raise ValueError('Amendment or previous dossier changed since review')
    old, new = load(old_folder / 'candidate.json'), load(source / 'candidate.json')
    catalogue.validate(old, old_folder)
    catalogue.validate(new, source)
    if old['id'] != new['id'] or old['target']['tic'] != new['target']['tic']:
        raise ValueError('Amendment changes stable identity')
    if load(source / 'analysis-settings.json')['original_assessment_sha256'] != row['assessment_sha256']:
        raise ValueError('Amendment assessment differs')
    major, minor, _ = map(int, old['version'].split('.'))
    new['version'] = f'{major}.{minor + 1}.0'
    new['history'] = old['history'] + [{'date': datetime.now(timezone.utc).date().isoformat(),
        'version': new['version'], 'change': 'New sealed input assessment; prior dossier and all evidence archived. Local amendment awaiting deliberate release.'}]
    publication = dict(old['publication'])
    if publication['first_public_utc']:
        publication.update(state='disclosed', disclosure_url=publication.get('disclosure_url') or publication['release_url'],
                           release_url=None, doi=None)
    new['publication'] = publication
    # Recoverable swap: a crash leaves the previous directory beside its exact
    # replacement, rather than deleting the only copy of public evidence.
    replacement = old_folder.with_name('.' + signal_id + '-amendment')
    backup = old_folder.with_name('.' + signal_id + '-previous')
    if replacement.exists() or backup.exists():
        raise ValueError('Unfinished amendment requires recovery before retrying')
    shutil.copytree(source, replacement)
    history = replacement / 'evidence' / ('prior-v' + old['version'])
    shutil.copytree(old_folder, history)
    new['evidence'].append(history.relative_to(replacement).as_posix() + '/candidate.json')
    write(replacement / 'candidate.json', new)
    with (replacement / 'README.md').open('a') as stream:
        stream.write('\nThis local amendment preserves the signal’s first public disclosure. '
                     'Its new analysis version awaits deliberate release; previous evidence is archived.\n')
    sources = {f['path']: f['source_sha256'] for f in load(source / 'evidence-manifest.json')['files'] if 'source_sha256' in f}
    seal(replacement, sources, signal_id)
    # Validation requires the stable signal directory name.
    old_folder.rename(backup)
    try:
        replacement.rename(old_folder)
        catalogue.validate(load(old_folder / 'candidate.json'), old_folder)
        write(receipt, {'signal_id': signal_id, 'previous_version': old['version'],
            'version': new['version'], 'assessment_sha256': row['assessment_sha256'],
            'first_public_utc': publication['first_public_utc'], 'state': 'local_pending_release',
            'prior_manifest_sha256': row['previous_manifest_sha256'],
            'amended_manifest_sha256': sha(old_folder / 'evidence-manifest.json')})
    except BaseException:
        if old_folder.exists():
            old_folder.rename(replacement)
        backup.rename(old_folder)
        raise
    shutil.rmtree(backup)
    return load(receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--checks', type=Path, required=True)
    parser.add_argument('--screen', type=Path, action='append', default=[])
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--reviews', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', args.batch):
        raise ValueError('Unsafe batch identifier')
    prepare(args.report, args.checks, args.screen, args.destination, args.batch, args.reviews)


if __name__ == '__main__':
    main()
