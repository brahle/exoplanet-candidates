"""Versioned, bounded batch capsules; copied science and derived views stay distinct."""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile

import catalogue
from export_batch import load, sha, write

FORMAT = 'batch-evidence-v2'
MAX_BYTES = 2 * 1024**3
MAX_MEMBERS = 100_000
COMMON = ('scripts', 'schemas', 'tests', 'docs')
AGGREGATES = {'catalogue.json', 'vetting-catalogue.json'}


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(p in {'.', '..'} for p in name.split('/')):
        raise ValueError('Unsafe package path')
    return path.as_posix()


def extract(stream, destination):
    members, size, names = [], 0, set()
    for member in stream:
        if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
            raise ValueError('Release archive may only contain regular files and directories')
        try:
            name = relative(member.name.rstrip('/'))
        except ValueError as exc:
            raise tarfile.ExtractError('Unsafe archive path') from exc
        if name in names:
            raise ValueError('Duplicate archive member')
        names.add(name); members.append(member); size += member.size
        if len(members) > MAX_MEMBERS or size > MAX_BYTES:
            raise ValueError('Release archive exceeds declared inspection limits')
    stream.extractall(destination, members=members, filter='data')


def tracked_files(root, commit):
    rows = subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', commit], cwd=root)
    files = {}
    for row in rows.split(b'\0'):
        if not row:
            continue
        header, name = row.split(b'\t', 1)
        mode, kind, oid = header.decode().split()
        files[name.decode()] = (mode, kind, oid)
    return files


def references(value, root, folder, tracked):
    """Follow explicit repository paths; remote raw-input identifiers remain external."""
    if isinstance(value, list):
        for item in value:
            yield from references(item, root, folder, tracked)
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str):
                target = None
                if item.startswith(('batches/', 'candidates/', 'assessments/', 'reproductions/', 'reviews/')):
                    target = root / item
                elif item.startswith('../') and (key in {'path', 'artifact', 'file'} or key.endswith(('_path', '_file'))):
                    target = folder / item
                if target is not None:
                    target = target.resolve()
                    if not target.is_relative_to(root) or not target.is_file():
                        raise ValueError('Missing or unsafe shared dependency: ' + item)
                    name = target.relative_to(root).as_posix()
                    if name not in tracked:
                        raise ValueError('Shared dependency is not committed: ' + name)
                    if key == 'path' and 'sha256' in value and sha(target) != value['sha256']:
                        raise ValueError('Shared dependency hash mismatch: ' + name)
                    yield name
            yield from references(item, root, folder, tracked)


def build(root, batch, tag, records, total, commit, archive):
    tracked = tracked_files(root, commit)
    config_path = 'tests/fixture-dossiers.json'
    required = {config_path, 'pyproject.toml', 'uv.lock', 'scripts/catalogue.py',
                'scripts/batch_release.py', 'scripts/batch_package.py', 'schemas/candidate.schema.json'}
    if not required <= set(tracked) or not any(n.startswith('tests/test_') and n.endswith('.py') for n in tracked):
        raise ValueError('Missing frozen validation tools or declared fixture dependencies')
    fixture_ids = load(root / config_path)['dossier_ids']
    if len(set(fixture_ids)) != len(fixture_ids):
        raise ValueError('Duplicate fixture identity')
    selected = {r['id'] for r in records}
    support = set(fixture_ids) - selected
    ids = selected | support
    for identifier in ids:
        if '/' in identifier or not identifier.startswith('tic-'):
            raise ValueError('Unsafe fixture identity')
        if f'candidates/{identifier}/candidate.json' not in tracked:
            raise ValueError('Missing selected or fixture dossier')
    prefixes = [f'candidates/{identifier}/' for identifier in sorted(ids)]
    prefixes += [f'batches/{batch}/', *(name + '/' for name in COMMON)]
    names = {name for name in tracked if '/' not in name or any(name.startswith(p) for p in prefixes)}
    # A queue over JSON source files makes cross-batch snapshot closure explicit.
    scanned = set()
    while True:
        pending = sorted(n for n in names - scanned - AGGREGATES if n.endswith('.json'))
        if not pending:
            break
        for name in pending:
            scanned.add(name)
            names.update(references(load(root / name), root, (root / name).parent, tracked))
    # Supporting references must not silently add whole unrelated dossiers.
    for name in names:
        if name.startswith('candidates/') and name.split('/')[1] not in ids:
            raise ValueError('Undeclared dossier dependency; declare its role explicitly')
        if tracked[name][0] not in {'100644', '100755'} or tracked[name][1] != 'blob':
            raise ValueError('Only regular committed source files may be packaged')
    with tempfile.TemporaryDirectory(prefix='candidate-package-') as temporary:
        stage = Path(temporary) / tag; stage.mkdir()
        source_files = {}
        for name in sorted(names):
            path = stage / name; path.parent.mkdir(parents=True, exist_ok=True)
            # Read Git objects, rather than trusting mutable or assume-unchanged working files.
            data = subprocess.check_output(['git', 'cat-file', 'blob', tracked[name][2]], cwd=root)
            path.write_bytes(data)
            path.chmod(0o755 if tracked[name][0] == '100755' else 0o644)
            source_files[name] = {'source_path': name, 'sha256': sha(path), 'bytes': len(data)}
        for name, destination in [('catalogue.json', 'package-provenance/source-catalogue.json'),
                                  ('vetting-catalogue.json', 'package-provenance/source-vetting-catalogue.json'),
                                  ('README.md', 'package-provenance/source-README.md')]:
            if name in source_files:
                target = stage / destination; target.parent.mkdir(exist_ok=True)
                (stage / name).rename(target); source_files[destination] = source_files.pop(name)
        packaged = []
        original_root = catalogue.ROOT
        try:
            catalogue.ROOT = stage
            packaged = catalogue.records()
        finally:
            catalogue.ROOT = original_root
        if {r['id'] for r in packaged} != ids:
            raise ValueError('Package dossier identities differ from the declared selection/fixtures')
        (stage / 'catalogue.json').write_bytes(catalogue.index_bytes(packaged))
        from vetting import refresh
        refresh(packaged, stage)
        from publish_figures import gallery
        gallery(stage, [r for r in packaged if (stage / 'candidates' / r['id'] / 'evidence/figures/diagnostic.png').is_file()])
        scope = {'package_format': FORMAT, 'source_commit': commit, 'batch': batch,
                 'source_catalogue_count': total, 'packaged_dossier_count': len(packaged),
                 'selected_signal_ids': sorted(selected), 'validation_fixture_ids': sorted(support),
                 'reproducibility_level': 'evidence_inspection'}
        write(stage / 'package-provenance/scope.json', scope)
        (stage / 'README.md').write_text(
            f'# {batch}: evidence-inspection package\n\n'
            f'This subset contains {len(selected)} selected batch dossiers and {len(support)} unchanged '
            f'validation-fixture dossiers ({len(packaged)} packaged dossiers). The source catalogue has '
            f'{total} dossiers. Validation fixtures are test dependencies, not additional batch candidates.\n\n'
            f'[Complete batch ledger](batches/{batch}/README.md) · [Browse packaged records](browse/README.md) · '
            '[Package scope](package-provenance/scope.json).\n\n'
            f'Copied scientific files are unchanged from [source commit {commit}]'
            f'(https://github.com/brahle/exoplanet-candidates/tree/{commit}). '
            'The release manifest enumerates exact copied-file hashes and separately generated subset views. '
            'Links to unrelated source records or method supplements can be followed in that public source snapshot. '
            'This is a batch subset, not a whole-repository snapshot or a fresh raw-input numerical rerun.\n\n'
            'Inspect in a fresh environment with `uv sync --frozen --offline`, '
            '`uv run --offline python scripts/catalogue.py check` and '
            '`uv run --offline python -m unittest discover -s tests`.\n')
        derived = {p.relative_to(stage).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size}
                   for p in stage.rglob('*') if p.is_file() and p.relative_to(stage).as_posix() not in source_files}
        files = [p for p in stage.rglob('*') if p.is_file()]
        size = sum(p.stat().st_size for p in files)
        if size > MAX_BYTES or len(list(stage.rglob('*'))) + 1 > MAX_MEMBERS:
            raise ValueError('Release archive exceeds declared inspection limits')
        def neutral_metadata(info):
            info.uid = info.gid = 0
            info.uname = info.gname = 'root'
            info.mtime = 0
            info.pax_headers = {}
            return info
        with tarfile.open(archive, 'w:gz') as stream:
            stream.add(stage, arcname=tag, filter=neutral_metadata)
        if archive.stat().st_size >= MAX_BYTES:
            archive.unlink()
            raise ValueError('Release asset exceeds the per-asset size limit')
        return {'package_format': FORMAT, 'source_catalogue_count': total,
                'packaged_dossier_count': len(packaged), 'total_dossiers': len(packaged),
                'uncompressed_bytes': size, 'source_files': source_files, 'derived_files': derived,
                'support_records': [{'id': r['id'], 'version': r['version'],
                                     'role': 'validation_test_fixture',
                                     'evidence_manifest_sha256': sha(stage / 'candidates' / r['id'] / 'evidence-manifest.json')}
                                    for r in packaged if r['id'] in support]}


def verify(root, manifest):
    root = root.resolve()
    source, derived = manifest['source_files'], manifest['derived_files']
    if set(source) & set(derived):
        raise ValueError('Source and derived package inventories overlap')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if actual != set(source) | set(derived):
        raise ValueError('Unlisted or missing package files')
    if sum((root / name).stat().st_size for name in actual) != manifest['uncompressed_bytes']:
        raise ValueError('Package uncompressed size differs from its manifest')
    for name, item in {**source, **derived}.items():
        path = root / relative(name)
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise ValueError('Package file hash or size mismatch: ' + name)
        if name in source:
            relative(item['source_path'])
            if not name.startswith('package-provenance/') and item['source_path'] != name:
                raise ValueError('Copied scientific/source file was relocated without provenance')
        elif name not in {'README.md', 'catalogue.json', 'vetting-catalogue.json', 'package-provenance/scope.json'} and not name.startswith(('browse/', 'gallery/')):
            raise ValueError('Scientific files cannot be derived package metadata')
    scope = load(root / 'package-provenance/scope.json')
    selected = {r['id'] for r in manifest['records']}
    support = {r['id'] for r in manifest['support_records']}
    if (selected & support or len(support) != len(manifest['support_records']) or
            any(r['role'] != 'validation_test_fixture' for r in manifest['support_records'])):
        raise ValueError('Invalid validation fixture enumeration')
    fixture_ids = set(load(root / 'tests/fixture-dossiers.json')['dossier_ids'])
    if support != fixture_ids - selected:
        raise ValueError('Declared validation fixtures differ from package support records')
    ids = {p.parent.name for p in (root / 'candidates').glob('*/candidate.json')}
    if ids != selected | support or len(ids) != manifest['packaged_dossier_count'] or len(ids) != manifest['total_dossiers']:
        raise ValueError('Extra or missing package dossier identities')
    if (scope['package_format'] != FORMAT or scope['source_commit'] != manifest['source_commit'] or
            scope['batch'] != manifest['batch'] or set(scope['selected_signal_ids']) != selected or
            set(scope['validation_fixture_ids']) != support or scope['packaged_dossier_count'] != len(ids) or
            scope['source_catalogue_count'] != manifest['source_catalogue_count'] or
            scope['reproducibility_level'] != 'evidence_inspection'):
        raise ValueError('Package scope and release manifest disagree')
    source_index = load(root / 'package-provenance/source-catalogue.json')
    originals = {r['id']: r for r in source_index}
    if len(originals) != len(source_index) or len(source_index) != manifest['source_catalogue_count']:
        raise ValueError('Source catalogue count differs from pinned source index')
    for identifier in ids:
        if catalogue.load(root / 'catalogue.json').count(originals.get(identifier)) != 1:
            raise ValueError('Packaged index differs from the source catalogue record')
        for name in ['candidate.json', 'evidence-manifest.json']:
            if f'candidates/{identifier}/{name}' not in source:
                raise ValueError('Scientific dossier must be copied source, not derived metadata')
    for row in manifest['support_records']:
        folder = root / 'candidates' / row['id']
        if (load(folder / 'candidate.json')['version'] != row['version'] or
                sha(folder / 'evidence-manifest.json') != row['evidence_manifest_sha256']):
            raise ValueError('Validation fixture differs from its pinned dossier')
    # Recheck closure in the extracted package, including hash-bound shared snapshots.
    inventory = {name: None for name in actual}
    for name in source:
        if name.endswith('.json') and source[name]['source_path'] not in AGGREGATES:
            list(references(load(root / name), root, (root / name).parent, inventory))
