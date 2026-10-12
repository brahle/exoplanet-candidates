"""Missing checks, warnings and successful execution cannot silently promote a signal."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import record_vetting_findings as importer
import vetting


class VettingAxes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'schemas').mkdir()
        (self.root / 'schemas/vetting-1.0.schema.json').write_bytes(
            (ROOT / 'schemas/vetting-1.0.schema.json').read_bytes())
        self.folder = self.root / 'candidates/tic-123-s01'
        (self.folder / 'evidence').mkdir(parents=True)
        self.record = {'id': self.folder.name, 'assessment': {
            'disposition': 'unclassified_transit_like_signal',
            'source_localisation': {'status': 'unresolved'}},
            'novelty': {'status': 'no_match_in_checked_sources'},
            'signal': {'period_d': {'value': 2.0}}}
        self.findings = {'signal_id': self.record['id'],
            'screen': {'priority': 'source_followup_without_these_warnings',
                       'all_joined_checks_available': True},
            'lightcurve': {'flags': {'odd_even': False}},
            'catalogues': {'binary_catalogue_warning': False, 'ruwe_warning': False},
            'source_warning_reviewed': False, 'external_report': None}
        stages = dict.fromkeys(vetting.STAGES, 'not_started'); stages['screening'] = 'complete'
        self.data = {'schema_version': '1.0', 'signal_id': self.record['id'],
            'assessed_utc': '2026-10-11T20:00:00Z',
            'progress': {'stage': 'screened', 'stages': stages},
            'scientific_assessment': {'status': 'unclassified', 'planet_probability': None,
                                      'basis': 'Unresolved source attribution', 'review_evidence': []},
            'initial_screen': {'outcome': 'no_initial_warnings', 'all_checks_available': True},
            'warnings': [], 'open_requirements': ['source_attribution'], 'evidence': []}

    def save(self):
        content = vetting.encoded(self.findings)
        (self.folder / 'evidence/vetting-findings.json').write_bytes(content)
        self.data['evidence'] = [{'path': 'evidence/vetting-findings.json',
                                 'sha256': hashlib.sha256(content).hexdigest()}]
        (self.folder / 'vetting.json').write_bytes(vetting.encoded(self.data))

    def test_no_warning_screen_stays_unclassified(self):
        self.save()
        result = vetting.validate(self.record, self.folder, self.root)
        self.assertEqual(result['scientific_assessment']['status'], 'unclassified')
        self.assertIsNone(result['scientific_assessment']['planet_probability'])

    def test_extended_warnings_require_the_new_schema(self):
        (self.root / 'schemas/vetting-1.1.schema.json').write_bytes(
            (ROOT / 'schemas/vetting-1.1.schema.json').read_bytes())
        self.findings['lightcurve']['flags']['no_saved_pixel_competitor'] = True
        self.findings['screen']['priority'] = 'diagnostic_warning_review'
        self.data['initial_screen']['outcome'] = 'warnings'
        self.data['warnings'] = ['no_saved_pixel_competitor']
        self.save()
        with self.assertRaises(Exception):
            vetting.validate(self.record, self.folder, self.root)
        self.data['schema_version'] = '1.1'
        self.save()
        result = vetting.validate(self.record, self.folder, self.root)
        self.assertEqual(result['scientific_assessment']['status'], 'unclassified')

    def test_unknown_schema_is_not_silently_accepted(self):
        self.data['schema_version'] = '9.9'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Unsupported vetting schema'):
            vetting.validate(self.record, self.folder, self.root)

    def test_missing_check_cannot_become_no_warning_pass(self):
        self.findings['screen']['all_joined_checks_available'] = False
        self.data['initial_screen']['all_checks_available'] = False
        self.save()
        with self.assertRaisesRegex(ValueError, 'Missing checks'):
            vetting.validate(self.record, self.folder, self.root)

    def test_warning_removal_is_rejected(self):
        self.findings['lightcurve']['flags']['odd_even'] = True
        self.save()
        with self.assertRaisesRegex(ValueError, 'Warning tags'):
            vetting.validate(self.record, self.folder, self.root)

    def test_diagnostic_execution_cannot_complete_source_qualification(self):
        self.data['progress']['stages']['source_vetting'] = 'complete'
        self.data['progress']['stage'] = 'source_vetting'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Diagnostic execution'):
            vetting.validate(self.record, self.folder, self.root)

    def test_scientific_promotion_needs_dossier_and_review(self):
        self.data['scientific_assessment']['status'] = 'likely_planet'
        self.save()
        with self.assertRaisesRegex(ValueError, 'differs from dossier'):
            vetting.validate(self.record, self.folder, self.root)
        self.record['assessment']['disposition'] = 'planet_candidate'
        with self.assertRaisesRegex(ValueError, 'documented review'):
            vetting.validate(self.record, self.folder, self.root)

    def test_changed_or_private_evidence_is_rejected(self):
        self.save()
        (self.folder / 'evidence/vetting-findings.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'hash changed'):
            vetting.validate(self.record, self.folder, self.root)
        self.findings['private'] = '/home/secret/data'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Private reference'):
            vetting.validate(self.record, self.folder, self.root)

    def test_views_are_independent_and_missing_records_are_explicit(self):
        self.data['progress']['stage'] = 'source_vetting'
        self.data['progress']['stages']['source_vetting'] = 'partial'
        self.findings['source_warning_reviewed'] = True
        self.data['warnings'] = ['off_target_diagnostic']
        self.save()
        summary = vetting.refresh([self.record], self.root)
        self.assertEqual(summary['scientific_assessment'], {'unclassified': 1})
        self.assertEqual(summary['initial_screen_all'], {'no_initial_warnings': 1})
        self.assertEqual(summary['current_warning_records'], 1)
        vetting.refresh([self.record], self.root, check=True)
        path = self.root / 'browse/process/source-vetting/README.md'
        path.write_text('stale')
        with self.assertRaisesRegex(ValueError, 'Stale vetting view'):
            vetting.refresh([self.record], self.root, check=True)

    def test_duplicate_identity_and_failed_or_changed_runs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            importer.identified([{'signal_id': 'tic-123-s01'}] * 2)
        folder = self.root / 'run'; folder.mkdir()
        manifest = {'command': 'vet-binary-priorities', 'ok': False,
                    'finished_utc': '2026-10-11T20:00:00Z', 'outputs': {}}
        (folder / 'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'successful terminal'):
            importer.checked_run(folder, 'vet-binary-priorities')
        manifest['ok'] = True
        manifest['outputs'] = {'signals.json': '0' * 64}
        (folder / 'manifest.json').write_text(json.dumps(manifest))
        (folder / 'signals.json').write_text('[]')
        with self.assertRaisesRegex(ValueError, 'source bytes changed'):
            importer.checked_run(folder, 'vet-binary-priorities')

    def test_exact_semantic_replay_preserves_original_json_representation(self):
        self.save()
        path = self.folder / 'evidence/vetting-findings.json'
        path.write_text(json.dumps(self.findings, sort_keys=True))
        self.data['evidence'][0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.folder / 'vetting.json').write_bytes(vetting.encoded(self.data))
        expected = copy.deepcopy(self.data)
        expected['evidence'][0]['sha256'] = '0' * 64  # New serializer's hash is immaterial on replay.
        self.assertTrue(importer.unchanged_findings(self.folder, expected, self.findings))
        changed = copy.deepcopy(self.findings); changed['source_warning_reviewed'] = True
        self.assertFalse(importer.unchanged_findings(self.folder, expected, changed))


if __name__ == '__main__':
    unittest.main()
