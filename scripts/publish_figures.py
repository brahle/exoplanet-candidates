"""Stage checked diagnostic figures and a gallery. Publication is an explicit Git push."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

import catalogue
from export_batch import load, public, seal, sha, write


def science_hash(record):
    value = {k: record[k] for k in ('target', 'signal', 'assessment', 'novelty', 'host', 'fit') if k in record}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def checked_bundle(source, report_path, manifest_path):
    report = load(report_path); manifest = load(manifest_path)
    if (manifest.get('ok') is not True or manifest.get('command') != 'vet-figures' or
            manifest['run_id'] != report['source_run'] or
            manifest['outputs'].get('report.json') != sha(report_path)):
        raise ValueError('Unverified figure run/report')
    binding = load(source / 'input-binding.json')
    if sha(source / 'input-binding.json') != manifest['outputs']['input-binding.json']:
        raise ValueError('Figure input binding differs from run')
    seen = set()
    for row in report['records']:
        identity = row['candidate_id']
        if identity in seen or not re.fullmatch(r'tic-[0-9]+-s[0-9]{2}', identity):
            raise ValueError('Duplicate or unsafe figure identity')
        seen.add(identity)
        for name, item in row['files'].items():
            if Path(name).name != name:
                raise ValueError('Unsafe figure filename')
            path = source / identity / name
            if sha(path) != item['sha256'] or path.stat().st_size != item['bytes']:
                raise ValueError('Figure bytes changed')
        if (not row['images'] or row['images'][0] != 'diagnostic.png' or
                not set(row['images']).issubset(row['files'])):
            raise ValueError('Figure image references incomplete')
        context = load(source / identity / 'plot-context.json')
        public(context)  # Refuse private references embedded in scientific text.
        if (context['candidate_id'] != identity or
                context['plot_data_sha256'] != row['files']['plot-data.npz']['sha256']):
            raise ValueError('Figure context/vector binding differs')
    return report, manifest, binding


def gallery(root, records):
    folder = root / 'gallery'; folder.mkdir(exist_ok=True)
    pages = []
    for page, start in enumerate(range(0, len(records), 24), 1):
        name = f'page-{page:02d}.md'; pages.append(name)
        lines = [f'# Candidate diagnostics — page {page}', '',
                 '[Gallery index](README.md). Each image opens its full-resolution PNG.', '',
                 '| | | |', '|---|---|---|']
        rows = records[start:start + 24]
        cells = [f"[![{r['id']}](../candidates/{r['id']}/evidence/figures/diagnostic.png)]"
                 f"(../candidates/{r['id']}/evidence/figures/diagnostic.png)<br>"
                 f"[{r['id']}](../candidates/{r['id']}/README.md)" for r in rows]
        for i in range(0, len(cells), 3):
            lines.append('| ' + ' | '.join((cells[i:i + 3] + [''] * 3)[:3]) + ' |')
        (folder / name).write_text('\n'.join(lines) + '\n')
    (folder / 'README.md').write_text('# Candidate diagnostic gallery\n\n'
        f'{len(records)} public dossiers. Five-panel overviews and complete chronological '
        'event pages use saved evidence. Signals remain unclassified.\n\n' +
        '\n'.join(f'- [Page {i + 1}: candidates {i * 24 + 1}–{min((i + 1) * 24, len(records))}]({p})'
                  for i, p in enumerate(pages)) + '\n\n'
        '[Methods and rendering](../docs/diagnostic-figures.md).\n')


def stage(root, source, report_path, manifest_path, require_complete=False, revision=None):
    if revision is not None and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', revision):
        raise ValueError('Unsafe figure revision')
    root = root.resolve(); source = source.resolve()
    previous_root = catalogue.ROOT
    try:
        catalogue.ROOT = root
        records = catalogue.records()
        by_id = {r['id']: r for r in records}
        report, manifest, binding = checked_bundle(source, report_path, manifest_path)
        selected = {r['candidate_id'] for r in report['records']}
        if not selected.issubset(by_id):
            raise ValueError('Figure publication contains unknown dossiers')
        if require_complete and set(by_id) != selected:
            raise ValueError('Figure publication must cover the whole public catalogue')
        prepared = []
        for row in report['records']:
            record = by_id[row['candidate_id']]
            folder = root / 'candidates' / record['id']
            if science_hash(record) != row['scientific_record_sha256']:
                raise ValueError('Figure scientific record differs from current dossier')
            context = load(source / record['id'] / 'plot-context.json')
            expected = {k: record['signal'][k] for k in ('period_d', 'epoch_btjd', 'duration_h', 'depth_ppm')}
            if context['ephemeris'] != expected:
                raise ValueError('Figure ephemeris differs')
            target = folder / 'evidence/figures'
            archive = None
            if target.exists():
                identical = all((target / name).is_file() and
                                sha(target / name) == item['sha256']
                                for name, item in row['files'].items())
                if identical:
                    continue
                if revision is None:
                    raise ValueError('Existing figure differs; requires new figure version')
                archive = folder / 'evidence/figure-history' / ('before-' + revision)
                if archive.exists():
                    raise ValueError('Figure history revision already exists')
            if sha(folder / 'candidate.json') != row['source_candidate_sha256']:
                raise ValueError('Figure source dossier changed before initial delivery')
            prepared.append((record, row, folder, target, archive))
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        for record, row, folder, target, archive in prepared:
            if archive is not None:
                shutil.copytree(target, archive)
            target.mkdir(exist_ok=True)
            for name in row['files']:
                shutil.copyfile(source / record['id'] / name, target / name)
            updated = copy.deepcopy(record)
            major, minor, patch = map(int, record['version'].split('.'))
            updated['version'] = f'{major}.{minor}.{patch + 1}'
            updated['evidence'] = list(dict.fromkeys(updated['evidence'] +
                ['evidence/figures/' + name for name in sorted(row['files'])]))
            if archive is not None:
                updated['evidence'].extend(p.relative_to(folder).as_posix()
                                           for p in sorted(archive.iterdir()) if p.is_file())
            updated['provenance']['runs']['figures'] = manifest['run_id']
            updated['provenance']['source_revisions']['figures'] = manifest['git']['commit']
            updated['history'].append({'version': updated['version'], 'date': timestamp[:10],
                'change': ('Updated diagnostic figures with explicitly reconstructed BLS spectra; '
                           'previous figure bundle retained in figure-history. '
                           if archive is not None else
                           'Added saved-evidence five-panel diagnostic and complete event pages; ') +
                          'Scientific measurements, assessments and disclosure dates unchanged.'})
            write(folder / 'candidate.json', updated)
            links = ', '.join(f'[{name}](evidence/figures/{name})' for name in row['images'][1:])
            caption = ('Saved signed local profiles; all numeric events, including negative depths. '
                       'Failures and excluded clock products remain in the context.')
            if 'source_run' in load(target / 'plot-context.json'):
                caption = 'Historical Phase 1 view. QLP clock assumptions remain unresolved; see later timing evidence.'
            block = ('\n\n## Diagnostic figures\n\n'
                     '![Five-panel diagnostic](evidence/figures/diagnostic.png)\n\n' + caption +
                     ' Display-bin error bars are uncalibrated white standard errors.\n\n' +
                     (f'All event pages: {links}.\n\n' if links else '') +
                     '[Plot context](evidence/figures/plot-context.json) · '
                     '[Saved plot vectors](evidence/figures/plot-data.npz) · '
                     '[Rendering methods](../../docs/diagnostic-figures.md).\n')
            text = (folder / 'README.md').read_text()
            if archive is None:
                split = text.find('\n\n')
                (folder / 'README.md').write_text(text[:split] + block + text[split:])
            else:
                previous_link = archive.relative_to(folder).as_posix() + '/diagnostic.png'
                note = ('\n\nThe BLS panel is now a documented reconstruction using the original '
                        'discovery-sector recipe and exact input bytes. Its timing-affected '
                        'QLP products differ from the qualified fold. '
                        f'[Previous figure]({previous_link}); full input/settings/comparison '
                        'provenance is in the current plot context.\n')
                (folder / 'README.md').write_text(text + note)
            old = load(folder / 'evidence-manifest.json')
            sources = {f['path']: f['source_sha256'] for f in old['files'] if 'source_sha256' in f}
            seal(folder, sources)
        current = catalogue.records()
        (root / 'catalogue.json').write_bytes(catalogue.index_bytes(current))
        gallery(root, [r for r in current if (root / 'candidates' / r['id'] /
                       'evidence/figures/diagnostic.png').is_file()])
        receipt = {'schema_version': '1.0', 'updated_records': len(prepared),
            'source_run': manifest['run_id'], 'source_revision': manifest['git']['commit'],
            'report_sha256': sha(report_path), 'renderer_sha256': binding['code_sha256']['figure_render.py'],
            'candidates': report['records'], 'images': sum(len(r['images']) for r in report['records'])}
        if prepared:
            if revision is not None:
                write(root / 'gallery/receipts' / (revision + '.json'), receipt)
            write(root / 'gallery/publication-receipt.json', receipt)
        return receipt
    finally:
        catalogue.ROOT = previous_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--require-complete', action='store_true')
    parser.add_argument('--revision', help='Explicit new figure version; archives any prior bundle')
    args = parser.parse_args()
    receipt = stage(args.root, args.source, args.report, args.manifest, args.require_complete,
                    args.revision)
    print(json.dumps({k: receipt[k] for k in ('updated_records', 'source_run', 'images')}))


if __name__ == '__main__':
    main()
