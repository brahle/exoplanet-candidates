"""Validate dossiers, scientific bookkeeping and hashes; build the public index."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def inside(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError(f"Missing or unsafe artifact: {relative}")
    return path


def schema_validator():
    """Resolve only checked-in versioned contracts; validation never fetches a schema."""
    schema = load(ROOT / "schemas/candidate.schema.json")
    registry = Registry()
    for path in sorted((ROOT / 'schemas').glob('candidate-*.schema.json')):
        contract = load(path)
        registry = registry.with_resource(contract['$id'], Resource.from_contents(contract))
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def validate(record, folder):
    schema_validator().validate(record)
    if record['id'] != folder.name or not record['id'].startswith(f"tic-{record['target']['tic']}-"):
        raise ValueError("Folder, signal ID and target TIC disagree")
    s = record['signal']
    provisional = record['assessment']['disposition'] == 'unclassified_transit_like_signal'
    for key in ('period_d', 'epoch_btjd', 'duration_h', 'depth_ppm'):
        if s[key]['error'] is None:
            if not provisional or key in ('period_d', 'epoch_btjd'):
                raise ValueError('Unavailable uncertainty is only permitted for provisional duration/depth')
            if not any('uncertainty unavailable' in limit.lower() for limit in s['limits']):
                raise ValueError('Unavailable uncertainty needs an explicit scientific limit')
    if record['assessment']['disposition'] in ('planet_candidate', 'validated_planet', 'confirmed_planet'):
        if any(record['assessment'][key]['status'] != 'supported' for key in ('source_localisation', 'timing_consistency')):
            raise ValueError('Stronger classification requires supported source and timing')
    for key in ('period_d', 'duration_h', 'depth_ppm'):
        if s[key]['value'] <= 0:
            raise ValueError(f"Nonpositive {key}")
    if not math.isclose(s['epoch_bjd_tdb'] - s['bjd_offset'], s['epoch_btjd']['value'], abs_tol=1e-8):
        raise ValueError("BTJD and BJD_TDB epochs disagree")
    c = s['covariance_epoch_period_d2']
    if not math.isclose(c[0][1], c[1][0], rel_tol=1e-10, abs_tol=1e-16):
        raise ValueError("Ephemeris covariance is not symmetric")
    if min(c[0][0], c[1][1]) <= 0 or c[0][0] * c[1][1] < c[0][1] ** 2:
        raise ValueError("Ephemeris covariance is not positive semidefinite")
    for variance, key in ((c[0][0], 'epoch_btjd'), (c[1][1], 'period_d')):
        if not math.isclose(math.sqrt(variance), s[key]['error'], rel_tol=1e-8):
            raise ValueError(f"{key} uncertainty and chosen covariance disagree")
    p = record['publication']
    if p['state'] == 'draft' and any(p.get(k) is not None for k in ('first_public_utc', 'disclosure_url', 'release_url', 'doi')):
        raise ValueError("A draft must not invent publication timestamps, releases or DOIs")
    if p['state'] == 'disclosed' and not all(p.get(k) for k in ('first_public_utc', 'disclosure_url')):
        raise ValueError("Disclosed dossiers need an actual public timestamp and disclosure URL")
    if p['state'] == 'published' and not all(p[k] for k in ('first_public_utc', 'release_url')):
        raise ValueError("Published dossiers need an actual public timestamp and release URL")
    references = list(record['evidence']) + record['novelty']['evidence']
    if record['schema_version'] in ('1.2', '1.3'):
        references.extend(record['target']['catalogue_association']['evidence'])
        references.extend(record['host']['evidence'])
        context = load(inside(folder, 'evidence/stellar-catalogue.json'))
        target = context['target']; association = target['association']
        if (target['tic'] != record['target']['tic'] or
                association['gaia_dr3_source_id'] != record['target']['gaia_dr3'] or
                association['status'] != record['target']['catalogue_association']['status'] or
                association['gaia_dr2_source_id'] != record['target']['catalogue_association']['gaia_dr2'] or
                target['parameters'] != record['host']['parameters'] or
                record['host']['catalogue_target'] != {
                    'tic': target['tic'], 'gaia_dr3': association['gaia_dr3_source_id']} or
                context['source_revision'] != record['provenance']['source_revisions']['stellar_catalogue'] or
                context['source_run'] != record['provenance']['runs']['stellar_catalogue']):
            raise ValueError('Catalogue context and structured association/stellar values disagree')
    if record['schema_version'] == '1.3':
        references.extend(record['fit']['evidence'])
        context = load(inside(folder, 'evidence/shape-uncertainty.json'))
        validate_fit_uncertainty(record, context)
    references.append(record['provenance']['input_lock'])
    for key in ('source_localisation', 'timing_consistency'):
        references.extend(record['assessment'][key]['evidence'])
    for relative in references:
        inside(folder, relative)
    receipt = load(folder / 'evidence-manifest.json')
    listed = set()
    for artifact in receipt['files']:
        path = inside(folder, artifact['path'])
        if path.stat().st_size != artifact['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != artifact['sha256']:
            raise ValueError(f"Artifact bytes changed: {artifact['path']}")
        listed.add(artifact['path'])
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*')
              if p.is_file() and p != folder / 'evidence-manifest.json'}
    if actual != listed:
        raise ValueError(f"Unaccounted files: {sorted(actual ^ listed)}")
    if record['reproducibility']['level'] == 'public_numerical_rerun':
        # The receipt must identify a completed, independently checked public reproduction.
        certificate = load(inside(folder, 'public-reproduction-certificate.json'))
        if (certificate.get('status') != 'passed' or not certificate.get('public_input_urls') or
                certificate.get('verification_kind') != 'public_numerical_rerun' or
                certificate.get('signal_id') != record['id'] or
                certificate.get('numeric_comparison', {}).get('status') != 'passed'):
            raise ValueError("Public numerical rerun requires a passed public-input certificate")
    from vetting import validate as validate_vetting
    validate_vetting(record, folder, ROOT)


def validate_fit_uncertainty(record, context):
    s = record['signal']; c = s['covariance_epoch_period_d2']
    replay = context['record']; shape = record['fit']['shape_uncertainty']
    if (replay['signal_id'] != record['id'] or replay['tic'] != record['target']['tic'] or
            replay['exact_previous_fit_replay'] is not True or
            replay['status'] != 'conditional_duration_error' or
            shape != replay['replayed_refinement']['shape_uncertainty'] or
            context['source_revision'] != record['provenance']['source_revisions']['shape_uncertainty'] or
            context['source_run'] != record['provenance']['runs']['shape_uncertainty']):
        raise ValueError('Shape uncertainty and pinned replay disagree')
    fit = replay['original_refinement']
    ep = fit['ephemeris']
    for value, actual in ((ep['duration_h'], s['duration_h']['value']),
                          (ep['period_d'], s['period_d']['value']),
                          (ep['epoch_bjd_tdb'], s['epoch_bjd_tdb'])):
        if value != actual:
            raise ValueError('Uncertainty refers to a different fitted ephemeris')
    matrix = shape['epoch_covariance']
    validate_shape_covariance(matrix)
    validate_shape_covariance(shape['reference_covariance'])
    reference = shape['reference_covariance']; anchor = fit['anchor_cycle']
    for i in range(4):
        for j in range(4):
            expected = reference[i][j]
            if i == 0:
                expected -= anchor * reference[1][j]
            if j == 0:
                expected -= anchor * reference[i][1]
            if i == j == 0:
                expected += anchor ** 2 * reference[1][1]
            if not math.isclose(expected, matrix[i][j], rel_tol=1e-8, abs_tol=1e-14):
                raise ValueError('Reference and epoch shape covariance transformation disagree')
    for i in range(2):
        for j in range(2):
            if not math.isclose(matrix[i][j], c[i][j], rel_tol=1e-8, abs_tol=1e-14):
                raise ValueError('Shape covariance and ephemeris covariance disagree')
    duration_error = 24 * math.sqrt(matrix[2][2])
    if not all(math.isclose(duration_error, value, rel_tol=1e-10) for value in (
            s['duration_h']['error'], shape['duration_error_h'], replay['duration_error_h'])):
        raise ValueError('Duration error and full covariance disagree')
    if not math.isclose(math.sqrt(matrix[3][3]), shape['ingress_fraction_error'], rel_tol=1e-10):
        raise ValueError('Ingress error and full covariance disagree')


def validate_shape_covariance(matrix):
    """Check PSD after unit normalization, so period scale cannot hide shape defects."""
    if any(matrix[i][i] <= 0 for i in range(4)):
        raise ValueError('Shape covariance has nonpositive marginal variance')
    normalized = [[matrix[i][j] / math.sqrt(matrix[i][i] * matrix[j][j])
                   for j in range(4)] for i in range(4)]
    lower = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(i + 1):
            if not math.isclose(normalized[i][j], normalized[j][i], rel_tol=1e-8, abs_tol=1e-10):
                raise ValueError('Shape covariance is not symmetric')
            value = normalized[i][j] - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if value < -1e-8:
                    raise ValueError('Shape covariance is not positive semidefinite')
                lower[i][j] = math.sqrt(max(0, value))
            elif lower[j][j] > 1e-12:
                lower[i][j] = value / lower[j][j]
            elif abs(value) > 1e-8:
                raise ValueError('Shape covariance is not positive semidefinite')


def records():
    found = []
    for path in sorted((ROOT / 'candidates').glob('*/candidate.json')):
        record = load(path)
        validate(record, path.parent)
        found.append(record)
    if len({r['id'] for r in found}) != len(found):
        raise ValueError("Duplicate signal ID")
    return found


def index_bytes(found):
    index = [{k: r[k] for k in ('schema_version', 'id', 'version', 'title', 'assessment', 'novelty', 'publication')} | {
        'period_d': r['signal']['period_d']['value'], 'path': f"candidates/{r['id']}/README.md"
    } for r in found]
    return (json.dumps(index, indent=2, allow_nan=False) + '\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'check'])
    args = parser.parse_args()
    found = records()
    target = ROOT / 'catalogue.json'
    content = index_bytes(found)
    if args.command == 'build':
        target.write_bytes(content)
    elif not target.exists() or target.read_bytes() != content:
        raise ValueError("Generated index is stale: run scripts/catalogue.py build")
    if (ROOT / 'vetting-catalogue.json').exists() or any(
            (ROOT / 'candidates').glob('*/vetting.json')):
        from vetting import refresh
        summary = refresh(found, ROOT, check=args.command == 'check')
        print(f'Vetting views: {summary["records"]} signals; independent progress/assessment axes')
    print(f"PASS: {len(found)} dossiers; schema, ephemeris covariance, artifact hashes and index")


if __name__ == '__main__':
    main()
