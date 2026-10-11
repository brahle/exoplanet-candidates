"""Deliver exactly replayed conditional duration errors; never publish or promote."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from pathlib import Path

import catalogue
from batch_release import safe_name
from export_batch import load, public, seal, sha, write


def checked_report(path):
    manifest = load(path.parent / 'manifest.json')
    if (not manifest['ok'] or manifest['command'] != 'vet-fit-uncertainty' or
            manifest['outputs'].get(path.name) != sha(path)):
        raise ValueError('Unverified fit uncertainty report')
    for name, checksum in manifest['outputs'].items():
        if sha(catalogue.inside(path.parent, name)) != checksum:
            raise ValueError('Fit uncertainty snapshot changed')
    report = load(path)
    if len({r['signal_id'] for r in report['records']}) != len(report['records']):
        raise ValueError('Duplicate fit uncertainty signal')
    return report, manifest


def enrich(root, batch, path):
    root = root.resolve(); batch = safe_name(batch)
    original_root = catalogue.ROOT
    try:
        catalogue.ROOT = root
        records = {r['id']: r for r in catalogue.records()}
        ledger = load(root / 'batches' / batch / 'outcomes.json')['outcomes']
        report, manifest = checked_report(path)
        batch_results = root / 'batches' / batch / 'shape-uncertainty-results.json'
        if batch_results.exists() and load(batch_results) != public(report):
            raise ValueError('Existing batch uncertainty snapshot differs')
        by_id = {r['signal_id']: r for r in report['records']}
        if set(by_id) != {r['signal_id'] for r in ledger}:
            raise ValueError('Uncertainty delivery must retain the whole batch ledger')
        prepared = []
        for row in ledger:
            if row['route'] != 'provisional_signal_record':
                continue
            record = records[row['signal_id']]; fit = by_id[record['id']]
            folder = root / 'candidates' / record['id']
            evidence = public({'record': fit, 'source_run': manifest['run_id'],
                'source_revision': manifest['git']['commit'], 'report_sha256': sha(path),
                'source_report_sha256': report['source_report_sha256'],
                'source_code_sha256': report['source_code_sha256']})
            context = folder / 'evidence/shape-uncertainty.json'
            if context.exists():
                if load(context) != evidence:
                    raise ValueError('Existing uncertainty differs; requires a new assessment')
                continue
            old = load(folder / 'evidence/ephemeris.json')
            receipt = load(folder / 'evidence-manifest.json')
            source_hash = next(f.get('source_sha256') for f in receipt['files']
                               if f['path'] == 'evidence/ephemeris.json')
            replayed = fit['replayed_refinement']
            old_model = {k: v for k, v in replayed.items() if k != 'shape_uncertainty'}
            if (fit['status'] != 'conditional_duration_error' or
                    fit['exact_previous_fit_replay'] is not True or
                    old_model != old or fit['previous_refinement_sha256'] != source_hash or
                    fit['tic'] != record['target']['tic']):
                raise ValueError('Selected duration uncertainty is unavailable or differs from saved fit')
            if record['assessment']['disposition'] != 'unclassified_transit_like_signal':
                raise ValueError('Conditional covariance delivery requires provisional records')
            updated = copy.deepcopy(record)
            updated['schema_version'] = '1.3'
            major, minor, _ = map(int, record['version'].split('.'))
            updated['version'] = f'{major}.{minor + 1}.0'
            updated['signal']['duration_h']['error'] = fit['duration_error_h']
            updated['signal']['limits'] = [x for x in updated['signal']['limits']
                                            if 'duration uncertainty unavailable' not in x.lower()]
            updated['signal']['limits'].append(
                'Duration uncertainty is conditional on the saved trapezoid model, selected events '
                'and diagonal beta-scaled noise; model/clock/host errors and coverage uncalibrated.')
            updated['fit'] = {'model': 'signed_exposure_sampled_trapezoid',
                'physical_parameters_status': 'not_fitted',
                'shape_uncertainty': replayed['shape_uncertainty'],
                'evidence': ['evidence/shape-uncertainty.json']}
            updated['provenance']['runs']['shape_uncertainty'] = manifest['run_id']
            updated['provenance']['source_revisions']['shape_uncertainty'] = manifest['git']['commit']
            updated['evidence'].append('evidence/shape-uncertainty.json')
            updated['history'].append({'date': datetime.now(timezone.utc).date().isoformat(),
                'version': updated['version'], 'change':
                'Retain previously omitted conditional duration/ingress covariance after exact fit '
                'replay; point estimates, ephemeris, classification and publication dates preserved.'})
            catalogue.schema_validator().validate(updated)
            catalogue.validate_fit_uncertainty(updated, evidence)
            for key in ('assessment', 'novelty', 'host', 'target', 'publication'):
                assert updated[key] == record[key]
            prepared.append((folder, updated, evidence))
        # All selections verified before writing any candidate.
        for folder, record, evidence in prepared:
            write(folder / 'candidate.json', record)
            write(folder / 'evidence/shape-uncertainty.json', evidence)
            with (folder / 'README.md').open('a') as stream:
                stream.write('\n## Conditional duration uncertainty\n\n'
                    f'The saved trapezoid duration now has a conditional error of '
                    f'{record["signal"]["duration_h"]["error"]:.6g} hours. '
                    '[Full shape covariance and exact replay](evidence/shape-uncertainty.json) '
                    'retain the model, rank/bound checks and uncertainty limitations. '
                    'This is a local Gaussian fit error with uncalibrated coverage. '
                    'Physical transit geometry remains unfitted.\n')
            previous = load(folder / 'evidence-manifest.json')
            sources = {f['path']: f['source_sha256'] for f in previous['files'] if 'source_sha256' in f}
            seal(folder, sources)
        (root / 'catalogue.json').write_bytes(catalogue.index_bytes(catalogue.records()))
        if not batch_results.exists():
            write(batch_results, public(report))
        receipt = {'batch': batch, 'updated_records': len(prepared),
            'whole_cohort_status_counts': report['status_counts'],
            'source_report_sha256': sha(path), 'source_run': manifest['run_id'],
            'limits': ['Conditional covariance; no physical fit or classification promotion']}
        if prepared:
            write(root / 'batches' / batch / 'shape-uncertainty-enrichment.json', receipt)
        return receipt
    finally:
        catalogue.ROOT = original_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--batch', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    import json
    print(json.dumps(enrich(args.root, args.batch, args.report)))


if __name__ == '__main__':
    main()
