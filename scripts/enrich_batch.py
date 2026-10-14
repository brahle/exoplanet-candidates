"""Add pinned aperture catalogue context to a public batch; never publish or promote."""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
from pathlib import Path
import shutil

import catalogue
from batch_release import safe_name
from export_batch import load, public, seal, sha, write


def checked_snapshot(path):
    manifest = load(path.parent / 'manifest.json')
    if manifest['command'] != 'vet-stellar' or manifest['outputs'].get(path.name) != sha(path):
        raise ValueError('Unverified stellar report')
    for name, digest in manifest['outputs'].items():
        if sha(path.parent / name) != digest:
            raise ValueError('Changed catalogue snapshot artifact')
    report = load(path)
    if report['configuration_sha256'] != manifest['config']['sha256']:
        raise ValueError('Catalogue policy seal differs')
    if len({r['tic'] for r in report['targets']}) != len(report['targets']):
        raise ValueError('Duplicate catalogue target')
    if len({r['signal_id'] for r in report['signals']}) != len(report['signals']):
        raise ValueError('Duplicate catalogue signal')
    return report, manifest


def context(target, report, manifest, batch):
    relevant = [r for r in report['requests'] if target['tic'] in r['ids'] or
                target['association']['gaia_dr2_source_id'] in r['ids']]
    return public({
        'target': target, 'source_run': report['source_run'],
        'acquisition_run': report.get('acquisition_run', report['source_run']),
        'source_revision': manifest['git']['commit'],
        'report_sha256': manifest['outputs']['stellar.json'],
        'configuration': report['configuration'],
        'configuration_sha256': report['configuration_sha256'],
        'requests': relevant,
        'response_artifacts': [{'path': f'batches/{batch}/stellar-snapshot/{r["artifact"]}',
                                'sha256': r['sha256']} for r in relevant if r.get('artifact')],
        'interpretation': 'Catalogue aperture association and values; source of the dip unresolved',
    })


def updated_record(record, target, run_id, source_revision, report_hash, date):
    result = copy.deepcopy(record)
    result['schema_version'] = '1.2'
    major, minor, _ = map(int, result['version'].split('.'))
    result['version'] = f'{major}.{minor + 1}.0'
    association = target['association']
    result['target']['gaia_dr3'] = association['gaia_dr3_source_id']
    result['target']['catalogue_association'] = {
        'status': association['status'], 'gaia_dr2': association['gaia_dr2_source_id'],
        'method': 'Exact TIC ID; official Gaia DR2 neighbourhood, uniqueness plus declared separation/Delta-G limits',
        'evidence': ['evidence/stellar-catalogue.json'],
    }
    result['host'] = {
        'status': 'unresolved', 'parameter_scope': 'catalogue_aperture_target',
        'catalogue_target': {'tic': target['tic'], 'gaia_dr3': association['gaia_dr3_source_id']},
        'parameters': target['parameters'],
        'dilution': {'status': 'unresolved', 'target_flux_fraction': None},
        'evidence': ['evidence/stellar-catalogue.json'],
        'limits': target['limits'] + ['No derived planet radius: physical host and dilution remain unresolved'],
    }
    result['provenance']['source_revisions']['stellar_catalogue'] = source_revision
    result['provenance']['runs']['stellar_catalogue'] = run_id
    result['evidence'].append('evidence/stellar-catalogue.json')
    result['history'].append({'date': date, 'version': result['version'],
        'change': f'Add pinned catalogue aperture association and stellar values (report {report_hash}); source, timing and disposition unchanged.'})
    return result


def enrich(root, batch, path):
    root = root.resolve(); batch = safe_name(batch)
    original = catalogue.ROOT
    try:
        catalogue.ROOT = root
        records = {r['id']: r for r in catalogue.records()}
        outcomes = load(root / 'batches' / batch / 'outcomes.json')
        report, manifest = checked_snapshot(path)
        signal_map = {s['signal_id']: s['tic'] for s in report['signals']}
        if set(signal_map) != {r['signal_id'] for r in outcomes['outcomes']}:
            raise ValueError('Enrichment must account for the whole batch ledger')
        targets = {t['tic']: t for t in report['targets']}
        chosen = [r['signal_id'] for r in outcomes['outcomes'] if r['route'] == 'provisional_signal_record']
        report_hash = sha(path); date = datetime.now(timezone.utc).date().isoformat()
        prepared = []
        for signal_id in chosen:
            record = records[signal_id]
            if signal_map[signal_id] != record['target']['tic']:
                raise ValueError('Catalogue and dossier TIC differ')
            target = targets[record['target']['tic']]
            folder = root / 'candidates' / signal_id
            artifact = context(target, report, manifest, batch)
            if (folder / 'evidence/stellar-catalogue.json').exists():
                if load(folder / 'evidence/stellar-catalogue.json') != artifact:
                    raise ValueError('Existing catalogue context differs; prepare a deliberate new assessment')
                continue
            if record['assessment']['disposition'] != 'unclassified_transit_like_signal':
                raise ValueError('This aperture-only enrichment requires provisional records')
            updated = updated_record(record, target, report['source_run'], manifest['git']['commit'], report_hash, date)
            catalogue.schema_validator().validate(updated)
            assert updated['signal'] == record['signal'] and updated['assessment'] == record['assessment']
            assert updated['novelty'] == record['novelty'] and updated['publication'] == record['publication']
            prepared.append((folder, updated, artifact))
        snapshot = root / 'batches' / batch / 'stellar-snapshot'
        if snapshot.exists():
            for name, digest in manifest['outputs'].items():
                if sha(snapshot / name) != digest:
                    raise ValueError('Existing public snapshot differs')
        else:
            snapshot.mkdir()
            for name in manifest['outputs']:
                shutil.copyfile(path.parent / name, snapshot / name)
            # Paths/hostnames are private; preserve the selected provenance, not the private manifest.
            write(snapshot / 'source-receipt.json', {'run_id': report['source_run'],
                'acquisition_run': report.get('acquisition_run', report['source_run']),
                'source_revision': manifest['git']['commit'], 'started_utc': manifest['started_utc'],
                'finished_utc': manifest['finished_utc'], 'ok': manifest['ok'],
                'outputs': manifest['outputs'], 'batch_sha256': report['batch_sha256'],
                'configuration_sha256': report['configuration_sha256']})
        for folder, record, artifact in prepared:
            write(folder / 'candidate.json', record)
            write(folder / 'evidence/stellar-catalogue.json', artifact)
            with (folder / 'README.md').open('a') as stream:
                stream.write('\n## Catalogue stellar context\n\n'
                    'The [pinned TIC/Gaia context](evidence/stellar-catalogue.json) supplies aperture-star '
                    'Teff, radius, mass, TESS magnitude and distance with catalogue uncertainties. '
                    'The structured host block marks the physical host and dilution unresolved; '
                    'these are catalogue values, not a planet-radius inference. '
                    f'Gaia association: {record["target"]["catalogue_association"]["status"]}.\n')
            old_receipt = load(folder / 'evidence-manifest.json')
            sources = {f['path']: f['source_sha256'] for f in old_receipt['files'] if 'source_sha256' in f}
            seal(folder, sources)
        found = catalogue.records()
        (root / 'catalogue.json').write_bytes(catalogue.index_bytes(found))
        counts = dict(Counter(targets[signal_map[s]]['association']['status'] for s in chosen))
        result = {'batch': batch, 'selected_records': len(chosen), 'updated_records': len(prepared),
                  'selected_association_counts': counts, 'source_run': report['source_run'],
                  'source_report_sha256': report_hash,
                  'unchanged': ['signal measurements', 'assessment', 'novelty', 'publication timestamps'],
                  'limits': ['Aperture catalogue context, not supported host attribution',
                             'This enrichment does not estimate transit parameters; retained fit uncertainties are unchanged']}
        if prepared:
            write(root / 'batches' / batch / 'stellar-enrichment.json', result)
        return result
    finally:
        catalogue.ROOT = original


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
