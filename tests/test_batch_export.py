"""Provisional disclosure must preserve uncertainty and exclude known-match hypotheses."""
import copy
import importlib.util
from pathlib import Path
import unittest
import tempfile
import json

spec = importlib.util.spec_from_file_location('export_batch', Path(__file__).resolve().parents[1] / 'scripts/export_batch.py')
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


class BatchExport(unittest.TestCase):
    def setUp(self):
        self.ep = {'adopted': True}
        self.phot = {'aggregates': [{'depth_ppm': 10}, {'depth_ppm': 12}],
                     'events': [{'sector': 1, 'usable': True, 'baseline_order': 1},
                                {'sector': 2, 'usable': True, 'baseline_order': 1}]}
        self.rob = {'minimum_leave_sector_snr': 1}
        self.check = {'result': {'checked_sources': ['snapshot'], 'near_matches': [], 'status': 'no_match_in_checked_sources'}}

    def route(self, prior=None):
        return export.route(self.ep, self.phot, self.rob, self.check, prior or [])

    def test_provisional_evidence_does_not_require_completed_scientific_gates(self):
        self.assertEqual(self.route(), 'provisional_signal_record')

    def test_failed_catalogue_request_cannot_become_nonmatch(self):
        self.check['error'] = 'timeout'
        self.assertEqual(self.route(), 'catalogue_check_failed')

    def test_unadjudicated_direct_report_suppresses_novel_claim(self):
        self.assertEqual(self.route([{'source': 'eb'}]), 'prior_report_or_match_hypothesis')
        self.check['result']['near_matches'] = [{'target': 'neighbour'}]
        self.assertEqual(self.route(), 'prior_report_or_match_hypothesis')

    def test_adverse_dip_and_unusable_coverage_are_retained_outcomes(self):
        self.phot['aggregates'][1]['depth_ppm'] = None
        self.assertEqual(self.route(), 'nonpositive_or_unavailable_baseline_dip')
        self.phot['aggregates'][1]['depth_ppm'] = 12
        self.phot['events'][1]['usable'] = False
        self.assertEqual(self.route(), 'insufficient_multisector_evidence')

    def test_private_reference_removal_preserves_scientific_values(self):
        source = {'depth_ppm': -20.1, 'relative_path': '/home/private/raw.fits', 'filename': 'raw.fits', 'failure': None}
        original = copy.deepcopy(source)
        self.assertEqual(export.public(source), {'depth_ppm': -20.1, 'filename': 'raw.fits', 'failure': None})
        self.assertEqual(source, original)
        with self.assertRaisesRegex(ValueError, 'Private reference'):
            export.public('See /home/private/archive')

    def test_batch_artifact_tampering_fails_before_scientific_export(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / 'photometry.json'
            export.write(data, {'depth': 12})
            manifest = root / 'manifest.json'
            export.write(manifest, {'ok': True, 'outputs': {'photometry.json': export.sha(data)}})
            stage = {'manifest': str(manifest), 'artifacts': {str(manifest): export.sha(manifest)}}
            export.write(data, {'depth': 13})
            with self.assertRaisesRegex(ValueError, 'Unverified scientific artifact'):
                export.artifact(stage, 'photometry.json')

    def test_review_identity_and_source_report_must_match(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); report = root / 'report.json'; export.write(report, {})
            row = {'signal_id': 'tic-123-s01', 'assessment_sha256': 'a' * 64}
            import hashlib
            row['review_id'] = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            doc = {'report_sha256': export.sha(report), 'reviews': [row]}
            path = root / 'reviews.json'; export.write(path, doc)
            self.assertEqual(export.verified_reviews(path, report)['tic-123-s01'], row)
            row['assessment_sha256'] = 'b' * 64; export.write(path, doc)
            with self.assertRaisesRegex(ValueError, 'Invalid or duplicate review'):
                export.verified_reviews(path, report)
            doc['report_sha256'] = 'c' * 64; export.write(path, doc)
            with self.assertRaisesRegex(ValueError, 'another report'):
                export.verified_reviews(path, report)

    def test_two_signals_on_one_target_export_without_identity_collapse(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = {'config': {'content': {}}, 'git': {'commit': 'a' * 40}, 'run_id': 'fixture'}
            payloads = {
                'inputs.json': {'products': []},
                'ephemeris.json': {'ephemeris': {'period_d': 2, 'epoch_bjd_tdb': 2457001, 'duration_h': 2},
                                   'epoch_period_covariance': [[.01, 0], [0, .0001]], 'chosen_hypothesis': 'discovery'},
                'photometry.json': {'aggregates': [{'baseline_order': 1, 'depth_ppm': 10, 'error_ppm': 1, 'n_events': 4}],
                                     'events': [{'sector': 1, 'usable': True, 'baseline_order': 1}, {'sector': 2, 'usable': True, 'baseline_order': 1}]},
                'robustness.json': {'diagnostic_tension_sigma': 3},
                'timing-summary.json': {}, 'timing-events.json': [], 'timing-controls.json': [], 'alternative-summary.json': {},
            }
            docs = {}
            for name, payload in payloads.items():
                path = root / name; export.write(path, payload); docs[name] = (payload, path, manifest)
            for number in (1, 2):
                assessment = {'signal': {'tic': '123', 'id': f'tic-123-s{number:02d}', 'ra_deg': 30, 'dec_deg': -40},
                              'assessment_sha256': 'b' * 64, 'blocking_gates': ['source_localisation'],
                              'stages': {'robustness': {'metrics': {'minimum_leave_sector_snr': 1}}}}
                export.dossier(root / 'out', assessment, {'checked_utc': '2026-10-11T00:00:00Z'}, docs, [], '2026-10-11')
            folders = sorted((root / 'out/candidates').iterdir())
            self.assertEqual([p.name for p in folders], ['tic-123-s01', 'tic-123-s02'])
            self.assertIn('/ S02', (folders[1] / 'README.md').read_text())
            with self.assertRaisesRegex(ValueError, 'Refusing to overwrite'):
                export.dossier(root / 'out', assessment, {'checked_utc': '2026-10-11T00:00:00Z'}, docs, [], '2026-10-11')
            for folder in folders:
                self.assertEqual(export.load(folder / 'candidate.json')['schema_version'], '1.1')
