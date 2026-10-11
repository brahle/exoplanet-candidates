"""Catalogue context cannot silently change signal evidence or claim a physical host."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue
import enrich_batch as enrichment
from export_batch import load, sha, write


def fixture(base):
    root = base / 'repo'; root.mkdir()
    shutil.copytree(ROOT / 'schemas', root / 'schemas')
    candidate = root / 'candidates/tic-464547401-s01'
    shutil.copytree(ROOT / 'candidates/tic-464547401-s01', candidate)
    record = load(candidate / 'candidate.json')
    write(root / 'batches/test/outcomes.json', {'outcomes': [
        {'signal_id': record['id'], 'route': 'provisional_signal_record'}]})
    source = base / 'source'; source.mkdir()
    parameter = {'value': 5800, 'unit': 'K', 'field': 'Teff',
                 'error_fields': {'error': 'e_Teff', 'error_minus': None, 'error_plus': None},
                 'uncertainty_method': 'Catalogue-reported', 'status': 'reported',
                 'error': 100, 'error_minus': None, 'error_plus': None, 'limits': []}
    params = {}
    for name, unit in [('teff_K', 'K'), ('radius_Rsun', 'R_sun'), ('mass_Msun', 'M_sun'),
                       ('tmag', 'mag'), ('distance_pc', 'pc')]:
        params[name] = {**parameter, 'unit': unit}
    target = {'tic': record['target']['tic'], 'association': {'status': 'associated',
              'gaia_dr2_source_id': '5415211319331147904', 'gaia_dr3_source_id': '5415211319331147905'},
              'parameters': params, 'limits': ['Physical host unverified']}
    report = {'source_run': 'fixture', 'configuration': {}, 'configuration_sha256': 'a' * 64,
              'batch_sha256': 'b' * 64, 'targets': [target], 'requests': [],
              'signals': [{'signal_id': record['id'], 'tic': record['target']['tic']}]}
    path = source / 'stellar.json'; write(path, report)
    write(source / 'requests.json', [])
    manifest = {'command': 'vet-stellar', 'ok': True, 'git': {'commit': 'c' * 40},
                'started_utc': '2026-10-11T00:00:00Z', 'finished_utc': '2026-10-11T00:01:00Z',
                'config': {'sha256': 'a' * 64},
                'outputs': {'stellar.json': sha(path), 'requests.json': sha(source / 'requests.json')}}
    write(source / 'manifest.json', manifest)
    return root, candidate, path, record


class StellarEnrichment(unittest.TestCase):
    def test_values_bound_to_evidence_and_repeat_preserves_versions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, folder, path, old = fixture(Path(temporary))
            result = enrichment.enrich(root, 'test', path)
            record = load(folder / 'candidate.json')
            self.assertEqual(result['updated_records'], 1)
            self.assertEqual(record['schema_version'], '1.2')
            for key in ('signal', 'assessment', 'novelty', 'publication'):
                self.assertEqual(record[key], old[key])
            self.assertEqual(record['host']['status'], 'unresolved')
            self.assertIsNone(record['host']['dilution']['target_flux_fraction'])
            self.assertEqual(enrichment.enrich(root, 'test', path)['updated_records'], 0)
            self.assertEqual(load(folder / 'candidate.json'), record)
            original = catalogue.ROOT
            try:
                catalogue.ROOT = root
                altered = copy.deepcopy(record)
                altered['host']['parameters']['radius_Rsun']['value'] = 1
                with self.assertRaisesRegex(ValueError, 'Catalogue context'):
                    catalogue.validate(altered, folder)
                altered = copy.deepcopy(record)
                altered['host']['status'] = 'supported'
                with self.assertRaises(ValidationError):
                    catalogue.validate(altered, folder)
            finally:
                catalogue.ROOT = original

    def test_stale_snapshot_rejected_before_any_dossier_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, folder, path, old = fixture(Path(temporary))
            path.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Unverified'):
                enrichment.enrich(root, 'test', path)
            self.assertEqual(load(folder / 'candidate.json'), old)

    def test_partial_batch_and_wrong_tic_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, folder, path, old = fixture(Path(temporary))
            report = load(path); report['signals'].append({'signal_id': 'tic-1-s01', 'tic': '1'})
            write(path, report)
            manifest = load(path.parent / 'manifest.json'); manifest['outputs']['stellar.json'] = sha(path)
            write(path.parent / 'manifest.json', manifest)
            with self.assertRaisesRegex(ValueError, 'whole batch'):
                enrichment.enrich(root, 'test', path)
            self.assertEqual(load(folder / 'candidate.json'), old)
