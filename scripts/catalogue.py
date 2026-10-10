"""Validate dossiers, scientific bookkeeping and hashes; build the public index."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def inside(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError(f"Missing or unsafe artifact: {relative}")
    return path


def validate(record, folder):
    schema = load(ROOT / "schemas/candidate.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(record)
    if record['id'] != folder.name or not record['id'].startswith(f"tic-{record['target']['tic']}-"):
        raise ValueError("Folder, signal ID and target TIC disagree")
    s = record['signal']
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
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name != 'evidence-manifest.json'}
    if actual != listed:
        raise ValueError(f"Unaccounted files: {sorted(actual ^ listed)}")
    if record['reproducibility']['level'] == 'public_numerical_rerun':
        # The receipt must identify a completed, independently checked public reproduction.
        certificate = load(inside(folder, 'public-reproduction-certificate.json'))
        if certificate.get('status') != 'passed' or not certificate.get('public_input_urls'):
            raise ValueError("Public numerical rerun requires a passed public-input certificate")


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
    index = [{k: r[k] for k in ('id', 'version', 'title', 'assessment', 'novelty', 'publication')} | {
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
    print(f"PASS: {len(found)} dossiers; schema, ephemeris covariance, artifact hashes and index")


if __name__ == '__main__':
    main()
