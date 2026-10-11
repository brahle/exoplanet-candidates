"""A duration error must refer to the same saved fit and full covariance."""
import copy
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue
import enrich_uncertainty
from export_batch import load, seal, sha, write


def fixture(base):
    root = base / 'repo'; root.mkdir()
    shutil.copytree(ROOT / 'schemas', root / 'schemas')
    folder = root / 'candidates/tic-101909456-s01'
    shutil.copytree(ROOT / 'candidates/tic-101909456-s01', folder)
    record = load(folder / 'candidate.json')
    record['schema_version'] = '1.2'; record.pop('fit', None)
    record['signal']['duration_h']['error'] = None
    record['signal']['limits'].append('Duration uncertainty unavailable.')
    record['evidence'] = [x for x in record['evidence'] if x != 'evidence/shape-uncertainty.json']
    (folder / 'evidence/shape-uncertainty.json').unlink(missing_ok=True)
    write(folder / 'candidate.json', record)
    old_manifest = load(folder / 'evidence-manifest.json')
    sources = {f['path']: f['source_sha256'] for f in old_manifest['files'] if 'source_sha256' in f}
    seal(folder, sources)
    old = load(folder / 'evidence/ephemeris.json')
    matrix = [[0.0] * 4 for _ in range(4)]; reference = copy.deepcopy(matrix)
    for i in range(2):
        for j in range(2):
            matrix[i][j] = old['epoch_period_covariance'][i][j]
            reference[i][j] = old['reference_period_covariance'][i][j]
    for m in [matrix, reference]:
        m[2][2] = (0.1 / 24) ** 2; m[3][3] = 0.03 ** 2
    shape = {'status': 'conditional_local_covariance',
        'parameter_order': ['epoch_btjd', 'period_d', 'duration_d', 'ingress_fraction'],
        'parameter_units': ['d', 'd', 'd', 'dimensionless'],
        'reference_parameter_order': ['reference_epoch_btjd', 'period_d', 'duration_d', 'ingress_fraction'],
        'reference_covariance': reference, 'epoch_covariance': matrix,
        'duration_error_h': 0.1, 'ingress_fraction_error': 0.03, 'jacobian_rank': 4,
        'fit_at_bound': False, 'degrees_of_freedom': 100, 'variance_inflation': 1,
        'errors_calibrated': False, 'method': 'Synthetic conditional covariance exercise',
        'limits': ['Conditional model; no scientific validation']}
    result = {'signal_id': record['id'], 'tic': record['target']['tic'],
        'status': 'conditional_duration_error', 'exact_previous_fit_replay': True,
        'original_refinement': old, 'replayed_refinement': {**old, 'shape_uncertainty': shape},
        'duration_error_h': 0.1, 'previous_refinement_sha256': sources['evidence/ephemeris.json']}
    write(root / 'batches/test/outcomes.json', {'outcomes': [
        {'signal_id': record['id'], 'route': 'provisional_signal_record'}]})
    source = base / 'source'; source.mkdir()
    report = {'records': [result], 'source_report_sha256': 'a' * 64,
        'source_code_sha256': 'b' * 64, 'status_counts': {'conditional_duration_error': 1}}
    path = source / 'fit-uncertainty.json'; write(path, report)
    write(source / 'manifest.json', {'command': 'vet-fit-uncertainty', 'run_id': 'fixture',
        'git': {'commit': 'c' * 40}, 'ok': True, 'outputs': {path.name: sha(path)}})
    return root, folder, path, record


class UncertaintyEnrichment(unittest.TestCase):
    def test_exact_fit_error_bound_to_covariance_without_point_or_gate_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, folder, path, original = fixture(Path(temporary))
            self.assertEqual(enrich_uncertainty.enrich(root, 'test', path)['updated_records'], 1)
            record = load(folder / 'candidate.json')
            self.assertEqual(record['schema_version'], '1.3')
            self.assertEqual(record['signal']['duration_h']['error'], 0.1)
            for key in ('assessment', 'novelty', 'host', 'publication'):
                self.assertEqual(record[key], original[key])
            for key in ('period_d', 'epoch_btjd', 'depth_ppm', 'covariance_epoch_period_d2'):
                self.assertEqual(record['signal'][key], original['signal'][key])
            self.assertEqual(enrich_uncertainty.enrich(root, 'test', path)['updated_records'], 0)
            saved_root = catalogue.ROOT
            try:
                catalogue.ROOT = root
                altered = copy.deepcopy(record); altered['signal']['duration_h']['error'] = 1
                with self.assertRaisesRegex(ValueError, 'Duration error'):
                    catalogue.validate(altered, folder)
            finally:
                catalogue.ROOT = saved_root

    def test_mismatched_or_failed_replay_refuses_whole_delivery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, folder, path, original = fixture(Path(temporary))
            report = load(path); report['records'][0]['exact_previous_fit_replay'] = False
            write(path, report)
            manifest = load(path.parent / 'manifest.json'); manifest['outputs'][path.name] = sha(path)
            write(path.parent / 'manifest.json', manifest)
            with self.assertRaisesRegex(ValueError, 'unavailable or differs'):
                enrich_uncertainty.enrich(root, 'test', path)
            self.assertEqual(load(folder / 'candidate.json'), original)

    def test_unit_normalized_psd_catches_correlated_shape_failure(self):
        matrix = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            matrix[i][i] = 1e-16
        matrix[2][3] = matrix[3][2] = 2e-16
        with self.assertRaisesRegex(ValueError, 'positive semidefinite'):
            catalogue.validate_shape_covariance(matrix)

    def test_bad_scalar_error_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, folder, path, original = fixture(Path(temporary))
            report = load(path); report['records'][0]['duration_error_h'] = 1
            write(path, report)
            manifest = load(path.parent / 'manifest.json'); manifest['outputs'][path.name] = sha(path)
            write(path.parent / 'manifest.json', manifest)
            with self.assertRaisesRegex(ValueError, 'Duration error'):
                enrich_uncertainty.enrich(root, 'test', path)
            self.assertEqual(load(folder / 'candidate.json'), original)
