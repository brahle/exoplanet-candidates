"""Stage reviewed matching external aperture reports; publication remains an explicit push."""
from __future__ import annotations

import argparse
import copy
from pathlib import Path
import re
import shutil

import catalogue
from export_batch import load, public, seal, sha, write


SCIENCE = ('target', 'signal', 'assessment', 'host', 'fit', 'reproducibility')


def checked_report(path):
    manifest = load(path.parent / 'manifest.json')
    if (manifest.get('ok') is not True or manifest['command'] != 'vet-external-report-review'
            or manifest['outputs'].get(path.name) != sha(path)):
        raise ValueError('Unverified external-report review')
    for name, digest in manifest['outputs'].items():
        if sha(catalogue.inside(path.parent, name)) != digest:
            raise ValueError('External-report review bytes changed')
    report = load(path)
    if report['source_run'] != manifest['run_id'] or not report['cases']:
        raise ValueError('Review run/selection missing or differs')
    return report, manifest


def record_reports(root, batch, path):
    root = root.resolve()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', batch):
        raise ValueError('Unsafe batch')
    report, manifest = checked_report(path)
    previous = catalogue.ROOT
    try:
        catalogue.ROOT = root
        records = {r['id']: r for r in catalogue.records()}
        prepared = []; seen = set()
        for row in report['cases']:
            sid = row['candidate_id']
            if sid in seen or sid not in records:
                raise ValueError('Duplicate or unknown review identity')
            seen.add(sid)
            review = load(catalogue.inside(path.parent, row['file']))
            if public(review) != review:
                raise ValueError('Private fields or paths in review; refuse export')
            if sha(path.parent / row['file']) != row['sha256'] or review['candidate_id'] != sid:
                raise ValueError('External-report identity or bytes changed')
            record = records[sid]; folder = root / 'candidates' / sid
            if (record['target']['tic'] != review['tic']
                    or review['review_outcome'] != 'matching_external_aperture_report'
                    or review['nominal_centres_agree'] is not True
                    or review['event_comparison']['status'] != 'unresolved'):
                raise ValueError('Review needs an explicit uncalibrated aperture-only outcome')
            if ({k:record[k] for k in SCIENCE if k in record} !=
                    {k:v for k,v in review['input_scientific_blocks'].items() if k in SCIENCE}):
                raise ValueError('Scientific dossier differs from reviewed input')
            if sha(folder / 'evidence/photometry.json') != review['photometry_sha256']:
                raise ValueError('Photometry differs from reviewed input')
            old_publication = review['input_scientific_blocks']['publication']
            if any(record['publication'].get(k) != old_publication.get(k)
                   for k in ('first_public_utc','authors','disclosure_url')):
                raise ValueError('Original disclosure metadata differs from reviewed input')
            payload = {k: v for k, v in review.items() if k != 'input_scientific_blocks'}
            evidence = folder / 'evidence/external-report.json'
            extras = []
            for item in review['supplementary_files']:
                source = catalogue.inside(path.parent, item['file'])
                if sha(source) != item['sha256'] or source.stat().st_size != item['bytes']:
                    raise ValueError('Supplementary source bytes changed')
                name = Path(item['path']).name
                if name not in {'transit_fit.json','vetting.json','followup.json',
                                'triceratops.json','vetting.png'}:
                    raise ValueError('Unexpected supplementary source filename')
                if name.endswith('.json') and public(load(source)) != load(source):
                    raise ValueError('Private fields or paths in supplementary evidence')
                extras.append((source, 'evidence/external-source/' + name))
            if evidence.exists():
                old = load(evidence)
                if ({k:v for k,v in old.items() if k != 'previous_novelty'} != payload
                        or record['novelty']['status'] != 'previously_reported'):
                    raise ValueError('Changed external review needs a new version')
                continue
            if sha(folder / 'candidate.json') != review['source_candidate_sha256']:
                raise ValueError('Candidate changed before review delivery')
            if record['publication'] != old_publication:
                raise ValueError('Publication metadata changed before initial review delivery')
            payload['previous_novelty'] = copy.deepcopy(record['novelty'])
            updated = copy.deepcopy(record)
            major, minor, _ = map(int, updated['version'].split('.'))
            updated['version'] = f'{major}.{minor + 1}.0'
            updated['novelty'].update(status='previously_reported', checked_utc=review['reviewed_utc'])
            updated['novelty']['limits'] = [
                'A matching independent aperture report is present in the cited pinned source.',
                *review['limits'],
                'Earlier no-match queries remain dated evidence; they omitted excluded upstream reports.',
            ]
            updated['novelty']['evidence'].append('evidence/external-report.json')
            updated['evidence'].append('evidence/external-report.json')
            updated['evidence'].extend(name for _,name in extras)
            updated['provenance']['runs']['external_report_review'] = manifest['run_id']
            updated['provenance']['source_revisions']['external_report_review'] = manifest['git']['commit']
            updated['provenance']['source_revisions']['external_source'] = review['source_commit']
            updated['history'].append({'date': review['reviewed_utc'][:10], 'version': updated['version'],
                'change': 'Record matching independent aperture report and external adverse evidence; '
                          'novelty updated to previously_reported. Physical disposition, measurements, '
                          'source/timing statuses and first disclosure preserved.'})
            catalogue.schema_validator().validate(updated)
            prepared.append((folder, updated, payload, extras))
        # Validate the entire requested selection before changing a single dossier.
        for folder, record, review, extras in prepared:
            write(folder / 'candidate.json', record)
            write(folder / 'evidence/external-report.json', review)
            for source, name in extras:
                destination = folder / name; destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            source = review['source_record']
            url = (review['source_url'] + '/blob/' + review['source_commit'] + '/' +
                   source['source_file'] + '#L' + str(source['raw_row_number']))
            tier = source['reported_disposition'].get('tier', 'unclassified')
            reason = source['raw'].get('c_reason') or 'Detailed classification rationale not published in the row.'
            events = review['event_comparison']
            text = ('## Matching external aperture report\n\n'
                    f'Reviewed {review["reviewed_utc"]}. Eumemic reports this TIC at '
                    f'{source["period_d"]:.9f} days as **{tier}** ([pinned table row]({url})). '
                    f'Reported rationale: {reason}\n\n'
                    f'All {events["distinct_events"]} tested saved nominal centres agree within '
                    f'{events["maximum_abs_residual_duration"]:.3f} transit durations. '
                    'The external epoch uncertainty/covariance is absent, so timing agreement '
                    'is not uncertainty-qualified. The aperture report is recorded as previously '
                    'reported; source identity, astrophysical disposition and discovery priority '
                    'remain independent and unresolved.\n\n'
                    '[Raw report, probabilities, event residuals and limits](evidence/external-report.json). '
                    'External FPP/NFPP values are their conditional model results, not our measurements. '
                    f'Supplementary status: {review["supplementary_status"]}.\n\n'
                    'Attribution: Eumemic, exoplanets; source results/tables/figures CC BY 4.0. '
                    'Copied source files are unmodified.\n\n')
            if extras:
                text += 'Published supporting files: ' + ', '.join(
                    f'[{Path(name).name}]({name})' for _,name in extras) + '.\n\n'
            novelty = folder / 'NOVELTY.md'
            novelty.write_text('# Dated source review\n\n' + text +
                               '## Earlier dated checks (superseded current status)\n\n' + novelty.read_text())
            readme = folder / 'README.md'; original = readme.read_text(); split = original.find('\n\n')
            original = original[:split] + '\n\n' + text + original[split:]
            # Correct stale summaries using values already in the authoritative dossier.
            duration = record['signal']['duration_h']
            if duration['error'] is not None:
                original = re.sub(r'Duration: ([0-9.]+) h \(uncertainty unavailable\)\.',
                                  f'Duration: {duration["value"]:.4f} ± {duration["error"]:.3g} h (conditional error).', original)
            original = original.replace('Gaia DR3 association is deliberately null.',
                                        'The catalogue Gaia association is recorded below; the physical host remains unresolved.')
            readme.write_text(original)
            old = load(folder / 'evidence-manifest.json')
            seal(folder, {f['path']:f['source_sha256'] for f in old['files'] if 'source_sha256' in f})
        (root / 'catalogue.json').write_bytes(catalogue.index_bytes(catalogue.records()))
        receipt = {'source_run':manifest['run_id'], 'source_revision':manifest['git']['commit'],
                   'review_sha256':sha(path), 'records':report['cases'],
                   'updated_records':len(prepared), 'scope':'External aperture reports; no planet/FP promotion'}
        if prepared:
            write(root / 'batches' / batch / 'external-report-review.json', receipt)
        return receipt
    finally:
        catalogue.ROOT = previous


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--batch', required=True)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    import json
    print(json.dumps(record_reports(args.root, args.batch, args.review)))


if __name__ == '__main__':
    main()
