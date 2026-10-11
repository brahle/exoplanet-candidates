"""A frozen ingestion contract must not acquire new null semantics silently."""
import copy
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue


class SchemaVersions(unittest.TestCase):
    def setUp(self):
        self.original = catalogue.load(ROOT / 'candidates/tic-464547401-s01/candidate.json')
        self.provisional = catalogue.load(ROOT / 'candidates/tic-101909456-s01/candidate.json')
        self.dispatch = catalogue.schema_validator()

    def test_original_contract_remains_strict_and_original_record_valid(self):
        strict = Draft202012Validator(catalogue.load(ROOT / 'schemas/candidate-1.0.schema.json'))
        strict.validate(self.original)
        for path in (ROOT / 'candidates').glob('*/candidate.json'):
            record = catalogue.load(path)
            self.dispatch.validate(record)
            if record['schema_version'] == '1.1':
                record['schema_version'] = '1.0'
                with self.assertRaises(ValidationError):
                    strict.validate(record)

    def test_null_gaia_never_permitted_under_one_point_zero(self):
        record = copy.deepcopy(self.original)
        record['target']['gaia_dr3'] = None
        with self.assertRaises(ValidationError):
            self.dispatch.validate(record)
        record['schema_version'] = '1.1'
        self.dispatch.validate(record)

    def test_unknown_version_and_null_ephemeris_error_are_rejected(self):
        record = copy.deepcopy(self.provisional)
        record['schema_version'] = '9.9'
        with self.assertRaises(ValidationError):
            self.dispatch.validate(record)
        record['schema_version'] = '1.1'
        for field in ('period_d', 'epoch_btjd'):
            broken = copy.deepcopy(record)
            broken['signal'][field]['error'] = None
            with self.assertRaises(ValidationError):
                self.dispatch.validate(broken)

    def test_nullable_shape_errors_require_limits_and_provisional_disposition_in_schema(self):
        for field in ('duration_h', 'depth_ppm'):
            record = copy.deepcopy(self.provisional)
            record['signal'][field]['error'] = None
            self.dispatch.validate(record)
            record['signal']['limits'] = ['Some unrelated limit']
            with self.assertRaises(ValidationError):
                self.dispatch.validate(record)
            record['signal']['limits'] = ['Duration uncertainty unavailable.']
            record['assessment']['disposition'] = 'planet_candidate'
            with self.assertRaises(ValidationError):
                self.dispatch.validate(record)
