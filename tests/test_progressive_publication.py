"""One terminal batch conserves amendments, re-detections, s02 and held rows."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue
import export_batch as export
import import_survey_followup as followup
import batch_release as release


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def scientific_fixture(root, sid):
    signal = {'id': sid, 'tic': sid.split('-')[1], 'ra_deg': 30., 'dec_deg': -40.,
              'period_d': 2., 'epoch_bjd_tdb': 2457001., 'duration_h': 2., 'depth_ppm': 100.}
    payloads = {'inputs.json': {'products': []},
        'ephemeris.json': {'adopted': True, 'ephemeris': signal,
            'epoch_period_covariance': [[.01, 0], [0, .0001]], 'chosen_hypothesis': 'discovery'},
        'photometry.json': {'aggregates': [
            {'baseline_order': 1, 'depth_ppm': 100., 'error_ppm': 10., 'n_events': 4},
            {'baseline_order': 2, 'depth_ppm': 101., 'error_ppm': 10., 'n_events': 4}],
            'events': [{'sector': 1, 'usable': True, 'baseline_order': 1},
                       {'sector': 2, 'usable': True, 'baseline_order': 1}]},
        'robustness.json': {'diagnostic_tension_sigma': 3}, 'timing-summary.json': {},
        'timing-events.json': [], 'timing-controls.json': [], 'alternative-summary.json': {}}
    stages, docs = {}, {}
    for stage, names in {'acquisition': ['inputs.json'], 'photometry': ['ephemeris.json', 'photometry.json'],
            'robustness': ['robustness.json'], 'timing': ['timing-summary.json', 'timing-events.json', 'timing-controls.json'],
            'alternatives': ['alternative-summary.json']}.items():
        folder = root / sid / stage
        for name in names:
            export.write(folder / name, payloads[name])
        manifest = {'ok': True, 'outputs': {n: export.sha(folder / n) for n in names},
            'git': {'commit': 'a'*40}, 'run_id': 'fixture', 'config': {'content': {}}}
        export.write(folder / 'manifest.json', manifest)
        stages[stage] = {'execution_status': 'succeeded', 'manifest': str(folder / 'manifest.json'),
            'artifacts': {str(folder / 'manifest.json'): export.sha(folder / 'manifest.json')},
            'metrics': {'minimum_leave_sector_snr': 1}}
        for name in names:
            docs[name] = (payloads[name], folder / name, manifest)
    assessment = {'signal': signal, 'stages': stages, 'blocking_gates': ['source_localisation']}
    assessment['assessment_sha256'] = digest(assessment)
    check = {'signal_id': sid, 'ra_deg': 30., 'dec_deg': -40., 'period_d': 2.,
             'checked_utc': '2026-10-14T00:00:00Z', 'arguments': {'cone_radius_arcsec': 120},
             'result': {'checked_sources': ['snapshot'], 'near_matches': [], 'status': 'no_match_in_checked_sources'}}
    return assessment, check, docs


class ProgressivePublication(unittest.TestCase):
    def test_acceptance_batch_and_deliberate_amendment(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); repo = base / 'repo'; repo.mkdir()
            shutil.copytree(ROOT / 'schemas', repo / 'schemas')
            a, check, docs = scientific_fixture(base / 'science', 'tic-123-s01')
            export.dossier(repo, a, check, docs, [], '2026-10-13')
            old_folder = repo / 'candidates/tic-123-s01'
            old = export.load(old_folder / 'candidate.json')
            old['publication'].update(state='disclosed', first_public_utc='2026-10-13T12:00:00Z',
                disclosure_url='https://example.org/first-disclosure')
            export.write(old_folder / 'candidate.json', old); export.seal(old_folder, {})
            prior_bytes = (old_folder / 'candidate.json').read_bytes()
            a2, check2, _ = scientific_fixture(base / 'science', 'tic-123-s02')
            carried = {'signal': {'id': 'tic-456-s01', 'tic': '456', 'ra_deg': 30., 'dec_deg': -40.}, 'stages': {}, 'blocking_gates': []}
            carried['assessment_sha256'] = digest(carried)
            known = {'signal': {'id': 'tic-789-s01', 'tic': '789', 'ra_deg': 30., 'dec_deg': -40.}, 'stages': {}, 'blocking_gates': []}
            known['assessment_sha256'] = digest(known)
            assessments = [a, carried, a2, known]
            routes = ['completed', 'carried_forward', 'completed', 'completed']
            rows = [{'row_id': x['signal']['id'], 'signal_id': x['signal']['id'],
                     'assessment_sha256': x['assessment_sha256'], 'route': r}
                    for x, r in zip(assessments, routes)]
            rows += [{'row_id': 'identity:h', 'signal_id': None, 'route': 'identity_hold', 'reason': 'ambiguous identity'},
                     {'row_id': 'intake:k', 'signal_id': None, 'route': 'intake_hold', 'reason': 'missing pinned file'},
                     {'row_id': 'tic-999-s01', 'signal_id': 'tic-999-s01', 'route': 'execution_failed',
                      'reason': 'three exhausted timeouts', 'attempts': 3}]
            report = base / 'sealed/report.json'
            export.write(report, {'assessments': assessments, 'terminal_outcomes': rows})
            export.write(report.parent / 'manifest.json', {'ok': True, 'outputs': {'report.json': export.sha(report)}})
            reviews = []
            for x in assessments:
                review = {'signal_id': x['signal']['id'], 'assessment_sha256': x['assessment_sha256'],
                          'disposition': 'unclassified_transit_like_signal', 'publication_tier': 'evidence_inspection'}
                review['review_id'] = digest(review); reviews.append(review)
            review_path = base / 'reviews.json'
            export.write(review_path, {'report_sha256': export.sha(report), 'reviews': reviews})
            self_check = dict(check, result={'status': 'near_matches_found', 'checked_sources': ['snapshot'],
                'near_matches': [{'sources': ['git:brahle/exoplanet-candidates'],
                                  'source_keys': ['tic-123-s01'], 'tic_id': '123'}]})
            checks = [self_check, dict(check, signal_id=carried['signal']['id']), check2,
                      dict(check, signal_id=known['signal']['id'], result={'status': 'variable_star_match',
                           'checked_sources': ['snapshot'], 'variable_matches': [{'source': 'EB'}]})]
            check_path = base / 'checks.jsonl'; check_path.write_text(''.join(json.dumps(c)+'\n' for c in checks))
            export.prepare(report, check_path, [], repo, 'acceptance', review_path)
            outcomes = export.load(repo / 'batches/acceptance/outcomes.json')
            self.assertEqual(outcomes['count'], 7)
            self.assertEqual(set(outcomes['routes']), {'amendment_pending', 'carried_forward',
                'provisional_signal_record', 'identity_hold', 'intake_hold', 'execution_failed',
                'prior_report_or_match_hypothesis'})
            self.assertEqual((old_folder / 'candidate.json').read_bytes(), prior_bytes)
            applied = export.amend(repo, 'acceptance', 'tic-123-s01')
            new = export.load(old_folder / 'candidate.json')
            self.assertEqual(new['publication']['first_public_utc'], old['publication']['first_public_utc'])
            self.assertEqual(applied['version'], '0.2.0')
            self.assertEqual(new['novelty']['status'], 'previously_reported')
            self.assertEqual(export.load(old_folder / 'evidence-manifest.json')['candidate'], new['id'])
            self.assertIn('previously reported', (old_folder / 'NOVELTY.md').read_text())
            self.assertEqual((old_folder / 'evidence/prior-v0.1.0/candidate.json').read_bytes(), prior_bytes)
            catalogue.validate(new, old_folder)
            catalogue.validate(export.load(repo / 'candidates/tic-123-s02/candidate.json'), repo / 'candidates/tic-123-s02')
            export.write(repo / 'catalogue.json', json.loads(catalogue.index_bytes(release.validate_records(repo, False))))
            selected, _, _ = release.batch_records(repo, 'acceptance')
            self.assertEqual({r['id'] for r in selected}, {'tic-123-s01', 'tic-123-s02'})
            with self.assertRaisesRegex(ValueError, 'already applied'):
                export.amend(repo, 'acceptance', 'tic-123-s01')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                export.prepare(report, check_path, [], repo, 'acceptance', review_path)
            # A new external hypothesis also amends an existing record, while
            # preserving its previous fit rather than fabricating new errors.
            prior_signal = export.load(old_folder / 'candidate.json')['signal']
            adverse_report = base / 'adverse/report.json'
            export.write(adverse_report, {'assessments': [a], 'terminal_outcomes': [rows[0]]})
            export.write(adverse_report.parent / 'manifest.json', {'ok': True,
                'outputs': {'report.json': export.sha(adverse_report)}})
            adverse_reviews = base / 'adverse-reviews.json'
            export.write(adverse_reviews, {'report_sha256': export.sha(adverse_report), 'reviews': [reviews[0]]})
            adverse_checks = base / 'adverse-checks.jsonl'
            adverse_checks.write_text(json.dumps(dict(check, result={'status': 'variable_star_match',
                'checked_sources': ['snapshot'], 'variable_matches': [{'source': 'EB'}]}))+'\n')
            export.prepare(adverse_report, adverse_checks, [], repo, 'adverse', adverse_reviews)
            self.assertEqual(export.load(repo / 'batches/adverse/outcomes.json')['routes'], {'amendment_pending': 1})
            export.amend(repo, 'adverse', 'tic-123-s01')
            newest = export.load(old_folder / 'candidate.json')
            self.assertEqual(newest['signal'], prior_signal)
            self.assertEqual(newest['publication']['first_public_utc'], old['publication']['first_public_utc'])
            self.assertEqual(newest['version'], '0.3.0')
            self.assertEqual(newest['novelty']['status'], 'unresolved')
            self.assertTrue((old_folder / 'evidence/progressive/adverse/catalogue-check.json').exists())
            catalogue.validate(newest, old_folder)

    def test_followup_keys_multiple_signals_per_tic(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source = root / 'source'
            ids = ['tic-123-s01', 'tic-123-s02']
            cohort = [{'tic': '123', 'signal_id': sid, 'legacy_class': 'survivor'} for sid in ids]
            export.write(source / 'cohort.json', cohort)
            export.write(source / 'summary.json', {'cohort_count': 2, 'original_class_counts': {'survivor': 2},
                'fresh_followup_count': 2, 'records_with_diagnostic_warnings': 0})
            export.write(source / 'findings.json', [{'signal_id': sid} for sid in ids])
            export.write(source / 'manifest.json', {'ok': True, 'command': 'vet-survey-followup-report',
                'outputs': {n: export.sha(source / n) for n in ['cohort.json', 'summary.json', 'findings.json']},
                'run_id': 'fixture', 'git': {'commit': 'a'*40}, 'finished_utc': '2026-10-14T00:00:00Z'})
            export.write(root / 'batches/fixture/outcomes.json', {'outcomes': [
                {'signal_id': sid, 'route': 'carried_forward', 'assessment_sha256': 'b'*64} for sid in ids]})
            self.assertEqual(followup.prepare(root, 'fixture', source)['cohort'], 2)

    def test_nonterminal_batch_is_refused_before_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); report = root / 'report.json'
            for route in ['queued', 'running', 'catalogue_check_failed']:
                export.write(report, {'assessments': [], 'terminal_outcomes': [{'signal_id': 'tic-1-s01', 'route': route}]})
                export.write(root / 'manifest.json', {'ok': True, 'outputs': {'report.json': export.sha(report)}})
                with self.assertRaisesRegex(ValueError, 'non-terminal'):
                    export.prepare(report, root/'missing', [], root/'dest', 'fixture', root/'missing')
            self.assertFalse((root / 'dest').exists())
