"""Release-integrity checks: errors that could mislead a reader must fail validation."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('catalogue', ROOT / 'scripts/catalogue.py')
catalogue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalogue)
FOLDER = ROOT / 'candidates/tic-464547401-s01'


class PublicationIntegrity(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((FOLDER / 'candidate.json').read_text())

    def test_all_real_dossiers_and_generated_index(self):
        found = catalogue.records()
        self.assertTrue(found)
        self.assertEqual((ROOT / 'catalogue.json').read_bytes(), catalogue.index_bytes(found))

    def test_uncertainty_covariance_mismatch_rejected(self):
        self.record['signal']['period_d']['error'] /= 2
        with self.assertRaisesRegex(ValueError, 'uncertainty and chosen covariance'):
            catalogue.validate(self.record, FOLDER)

    def test_wrong_mission_time_offset_rejected(self):
        self.record['signal']['epoch_bjd_tdb'] += 2167
        with self.assertRaisesRegex(ValueError, 'BTJD and BJD_TDB'):
            catalogue.validate(self.record, FOLDER)

    def test_unknown_duration_error_requires_provisional_classification_and_limit(self):
        self.record['schema_version'] = '1.1'
        self.record['signal']['duration_h']['error'] = None
        with self.assertRaises(ValidationError):
            catalogue.validate(self.record, FOLDER)
        self.record['signal']['limits'].append('Duration uncertainty unavailable.')
        self.record['assessment']['disposition'] = 'planet_candidate'
        with self.assertRaises(ValidationError):
            catalogue.validate(self.record, FOLDER)

    def test_unresolved_source_and_timing_cannot_be_promoted(self):
        self.record['assessment']['disposition'] = 'planet_candidate'
        with self.assertRaisesRegex(ValueError, 'requires supported source and timing'):
            catalogue.validate(self.record, FOLDER)

    def test_false_publication_claim_rejected(self):
        self.record['publication']['state'] = 'published'
        with self.assertRaisesRegex(ValueError, 'actual public timestamp'):
            catalogue.validate(self.record, FOLDER)

    def test_target_signal_identity_mismatch_rejected(self):
        self.record['target']['tic'] = '1'
        with self.assertRaisesRegex(ValueError, 'signal ID and target TIC'):
            catalogue.validate(self.record, FOLDER)

    def test_path_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsafe artifact'):
            catalogue.inside(FOLDER, '../../LICENSE')

    def test_changed_artifact_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / FOLDER.name
            shutil.copytree(FOLDER, folder)
            with (folder / 'inputs.json').open('a') as handle:
                handle.write(' ')
            with self.assertRaisesRegex(ValueError, 'Artifact bytes changed'):
                catalogue.validate(self.record, folder)

    def test_public_rerun_not_inferred_from_inspection(self):
        record = copy.deepcopy(self.record)
        record['reproducibility']['level'] = 'public_numerical_rerun'
        with self.assertRaisesRegex(ValueError, 'public-reproduction-certificate'):
            catalogue.validate(record, FOLDER)

    def test_inspection_certificate_cannot_be_renamed_into_numerical_proof(self):
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / FOLDER.name
            shutil.copytree(FOLDER, folder)
            certificate = {'status': 'passed', 'public_input_urls': ['https://example.invalid/archive'],
                           'verification_kind': 'public_evidence_inspection'}
            (folder / 'public-reproduction-certificate.json').write_text(json.dumps(certificate))
            record = copy.deepcopy(self.record)
            record['reproducibility']['level'] = 'public_numerical_rerun'
            # Re-seal this synthetic fixture so the certificate content, not its hash, is tested.
            import sys
            sys.path.insert(0, str(ROOT / 'scripts'))
            from export_batch import seal
            seal(folder, {})
            with self.assertRaisesRegex(ValueError, 'passed public-input certificate'):
                catalogue.validate(record, folder)


if __name__ == '__main__':
    unittest.main()
