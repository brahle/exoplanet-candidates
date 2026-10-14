"""Package or inspect a reviewed batch release. This command never publishes."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
import urllib.parse
import urllib.request

import catalogue
from export_batch import load, seal, sha, write


def safe_name(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', value) or value in {'.', '..'}:
        raise ValueError('Unsafe batch, tag or asset name')
    return value


def validate_records(root, check_index=True):
    original = catalogue.ROOT
    try:
        catalogue.ROOT = root
        records = catalogue.records()
        if check_index and (root / 'catalogue.json').read_bytes() != catalogue.index_bytes(records):
            raise ValueError('Stale catalogue index')
        return records
    finally:
        catalogue.ROOT = original


def batch_records(root, batch):
    records = {r['id']: r for r in validate_records(root)}
    folder = root / 'batches' / safe_name(batch)
    outcomes = load(folder / 'outcomes.json')
    rows = outcomes['outcomes']
    if (len(rows) != outcomes['count'] or len({r.get('row_id', r['signal_id']) for r in rows}) != len(rows)
            or dict(Counter(r['route'] for r in rows)) != outcomes['routes']):
        raise ValueError('Batch ledger does not conserve its input records')
    review_doc = load(folder / 'reviews.json')
    if review_doc['report_sha256'] != outcomes['report_sha256']:
        raise ValueError('Review source report differs from the outcome ledger')
    reviews = {}
    for review in review_doc['reviews']:
        identity = {k: v for k, v in review.items() if k not in {'review_id', 'reviewed_utc'}}
        digest = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        if digest != review['review_id'] or review['signal_id'] in reviews:
            raise ValueError('Invalid or duplicate review')
        reviews[review['signal_id']] = review
    chosen = []
    for row in rows:
        if row['route'] in {'identity_hold', 'intake_hold', 'execution_failed'}:
            if not row.get('reason') or row.get('assessment_sha256'):
                raise ValueError('Malformed ledger-only outcome')
            continue
        review = reviews.get(row['signal_id'])
        if not review or review['assessment_sha256'] != row['assessment_sha256']:
            raise ValueError('Missing or stale assessment review')
        if row['route'] == 'amendment_pending':
            receipt = folder / 'amendment-receipts' / (row['signal_id'] + '.json')
            if not receipt.exists():
                raise ValueError('Apply and validate pending amendments before release')
            applied = load(receipt)
            if applied['assessment_sha256'] != row['assessment_sha256']:
                raise ValueError('Amendment receipt refers to another assessment')
        elif row['route'] != 'provisional_signal_record':
            continue
        record = records[row['signal_id']]
        if (review['disposition'] != record['assessment']['disposition'] or
                review['publication_tier'] != 'evidence_inspection' or
                record['reproducibility']['level'] != 'evidence_inspection'):
            raise ValueError('Record, review and release tier disagree')
        settings = load(root / 'candidates' / row['signal_id'] / 'analysis-settings.json')
        if settings['original_assessment_sha256'] != review['assessment_sha256']:
            raise ValueError('Dossier refers to another assessment')
        chosen.append(record)
    if not chosen:
        raise ValueError('No selected signal records; retain the outcome ledger without a release')
    return chosen, len(records), folder


def prepare(root, batch, tag, output):
    root = root.resolve(); tag = safe_name(tag)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True):
        raise ValueError('Release packaging requires a clean committed source')
    records, total, folder = batch_records(root, batch)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'{tag}-evidence.tar.gz'
    manifest_path = output / 'release-manifest.json'
    if archive.exists() or manifest_path.exists():
        raise ValueError('Refusing to replace a prepared release asset')
    subprocess.run(['git', 'archive', '--format=tar.gz', '--prefix=' + tag + '/',
                    '--output=' + str(archive.resolve()), commit], cwd=root, check=True)
    manifest = {
        'batch': batch, 'release_tag': tag, 'source_commit': commit,
        'new_signal_count': len(records), 'total_dossiers': total,
        'records': [{'id': r['id'], 'version': r['version'],
                     'disposition': r['assessment']['disposition'],
                     'evidence_manifest_sha256': sha(root / 'candidates' / r['id'] / 'evidence-manifest.json')}
                    for r in records],
        'asset': {'filename': archive.name, 'bytes': archive.stat().st_size, 'sha256': sha(archive)},
        'review_document_sha256': sha(folder / 'reviews.json'),
        'outcomes_sha256': sha(folder / 'outcomes.json'),
        'reproducibility_level': 'evidence_inspection',
        'limits': ['Exported evidence integrity only; no numerical rerun or scientific validity certificate.',
                   'Catalogue nonmatches do not establish discovery priority.'],
    }
    write(manifest_path, manifest)
    return manifest


def inspect_archive(archive, manifest, expected_sha256, destination):
    if manifest['reproducibility_level'] != 'evidence_inspection':
        raise ValueError('This verifier only certifies evidence inspection')
    if sha(archive) != expected_sha256 or expected_sha256 != manifest['asset']['sha256']:
        raise ValueError('Release archive checksum mismatch')
    if archive.stat().st_size != manifest['asset']['bytes']:
        raise ValueError('Release archive size mismatch')
    with tarfile.open(archive) as stream:
        members = stream.getmembers()
        if any(m.issym() or m.islnk() or not (m.isfile() or m.isdir()) for m in members):
            raise ValueError('Release archive may only contain regular files and directories')
        if len(members) > 100_000 or sum(m.size for m in members) > 2 * 1024**3:
            raise ValueError('Release archive exceeds declared inspection limits')
        stream.extractall(destination, filter='data')
    roots = list(destination.iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise ValueError('Release archive needs one source directory')
    root = roots[0]
    records = {r['id']: r for r in validate_records(root)}
    rows = manifest['records']
    if len(rows) != manifest['new_signal_count'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Invalid release record enumeration')
    for row in rows:
        record = records[row['id']]
        if record['version'] != row['version'] or record['assessment']['disposition'] != row['disposition']:
            raise ValueError('Release record metadata mismatch')
        if sha(root / 'candidates' / row['id'] / 'evidence-manifest.json') != row['evidence_manifest_sha256']:
            raise ValueError('Release dossier manifest mismatch')
    if 'review_document_sha256' in manifest:
        selected, total, folder = batch_records(root, manifest['batch'])
        if {r['id'] for r in selected} != {r['id'] for r in rows} or total != manifest['total_dossiers']:
            raise ValueError('Release and reviewed batch selection differ')
        if sha(folder / 'reviews.json') != manifest['review_document_sha256'] or sha(folder / 'outcomes.json') != manifest['outcomes_sha256']:
            raise ValueError('Release review/ledger checksum mismatch')
    return root, len(records)


def fetch(url, path):
    request = urllib.request.Request(url, headers={'User-Agent': 'exoplanet-candidates-evidence-verifier'})
    with urllib.request.urlopen(request, timeout=90) as response, path.open('wb') as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)
    return path


def inspect_assets(archive, manifest_path, expected_sha256, certificate):
    manifest = load(manifest_path)
    with tempfile.TemporaryDirectory(prefix='candidate-draft-') as temporary:
        _, count = inspect_archive(archive, manifest, expected_sha256, Path(temporary))
    result = {'status': 'passed', 'verification_kind': 'local_evidence_asset_inspection',
              'checked_utc': datetime.now(timezone.utc).isoformat(),
              'archive_sha256': expected_sha256, 'selected_records_verified': manifest['new_signal_count'],
              'total_dossiers_validated': count, 'limits': manifest['limits']}
    write(certificate, result)
    return result


def verify_public(repo, tag, expected_sha256, certificate, run_checks=True):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Invalid GitHub repository')
    tag = safe_name(tag)
    if not re.fullmatch('[a-f0-9]{64}', expected_sha256):
        raise ValueError('An independently expected SHA256 is required')
    with tempfile.TemporaryDirectory(prefix='candidate-public-') as temporary:
        work = Path(temporary)
        metadata_url = f'https://api.github.com/repos/{repo}/releases/tags/{urllib.parse.quote(tag)}'
        metadata = load(fetch(metadata_url, work / 'release.json'))
        if metadata['draft'] or not metadata['immutable'] or not metadata['published_at']:
            raise ValueError('Expected a published immutable release')
        base = f'https://github.com/{repo}/releases/download/{urllib.parse.quote(tag)}/'
        manifest = load(fetch(base + 'release-manifest.json', work / 'release-manifest.json'))
        name = safe_name(manifest['asset']['filename'])
        if manifest['release_tag'] != tag or manifest['source_commit'] != metadata['target_commitish']:
            raise ValueError('Release source or tag differs from the manifest')
        archive = fetch(base + name, work / name)
        extracted = work / 'extracted'; extracted.mkdir()
        root, count = inspect_archive(archive, manifest, expected_sha256, extracted)
        checks = []
        if run_checks:
            for argv in [['uv', 'sync', '--frozen', '--offline'],
                         ['uv', 'run', '--offline', 'python', 'scripts/catalogue.py', 'check'],
                         ['uv', 'run', '--offline', 'python', '-m', 'unittest', 'discover', '-s', 'tests']]:
                result = subprocess.run(argv, cwd=root, capture_output=True, text=True)
                if result.returncode:
                    raise ValueError('Public inspection command failed: ' + result.stderr)
                checks.append({'command': argv, 'exit_code': result.returncode})
        result = {'status': 'passed', 'verification_kind': 'public_evidence_inspection',
                  'checked_utc': datetime.now(timezone.utc).isoformat(), 'http_authentication': 'none',
                  'release_url': metadata['html_url'], 'release_published_utc': metadata['published_at'],
                  'source_commit': manifest['source_commit'], 'archive_sha256': expected_sha256,
                  'selected_records_verified': manifest['new_signal_count'], 'total_dossiers_validated': count,
                  'public_input_urls': [metadata_url, base + 'release-manifest.json', base + name],
                  'checks': checks, 'limits': manifest['limits']}
        write(certificate, result)
        return result


def record_disclosure(root, batch, repo, commit, previous_public_commit):
    records, _, folder = batch_records(root, batch)
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) or not re.fullmatch('[a-f0-9]{40}', commit):
        raise ValueError('Invalid repository or disclosure commit')
    if previous_public_commit != 'none' and not re.fullmatch('[a-f0-9]{40}', previous_public_commit):
        raise ValueError('Declare the previous public commit, or none for a new repository')
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        base = f'https://api.github.com/repos/{repo}'
        repository = load(fetch(base, work / 'repository.json'))
        branch = load(fetch(base + '/branches/' + repository['default_branch'], work / 'branch.json'))
    if repository['private'] or branch['commit']['sha'] != commit or not repository['pushed_at']:
        raise ValueError('Expected disclosure commit is not the current public branch')
    planned = []
    for record in records:
        if record['publication']['state'] != 'draft':
            continue  # First disclosure is immutable once recorded.
        path = f'candidates/{record["id"]}/candidate.json'
        frozen = json.loads(subprocess.check_output(['git', 'show', commit + ':' + path], cwd=root, text=True))
        if frozen != record:
            raise ValueError('Local dossier differs from the disclosed snapshot')
        if previous_public_commit != 'none':
            existed = subprocess.run(['git', 'cat-file', '-e', previous_public_commit + ':' + path], cwd=root, capture_output=True)
            if existed.returncode == 0:
                raise ValueError('Dossier existed in previous public commit; investigate its original disclosure')
        planned.append(record)
    for record in planned:
        candidate = root / 'candidates' / record['id']
        sources = {r['path']: r['source_sha256'] for r in load(candidate / 'evidence-manifest.json')['files'] if 'source_sha256' in r}
        url = f'https://github.com/{repo}/tree/{commit}/candidates/{record["id"]}'
        record['publication'].update(state='disclosed', first_public_utc=repository['pushed_at'], disclosure_url=url)
        major, minor, patch = map(int, record['version'].split('.')); record['version'] = f'{major}.{minor}.{patch + 1}'
        record['history'].append({'date': datetime.now(timezone.utc).date().isoformat(), 'version': record['version'],
                                  'change': 'Record observed public Git disclosure; scientific evidence unchanged.'})
        if 'publication-receipt.json' not in record['evidence']:
            record['evidence'].append('publication-receipt.json')
        write(candidate / 'candidate.json', record)
        write(candidate / 'publication-receipt.json', {'candidate': record['id'],
              'publication_kind': 'public_git_disclosure', 'first_disclosure_commit': commit,
              'previous_public_commit': previous_public_commit, 'disclosure_url': url,
              'github_pushed_at_observed': repository['pushed_at'], 'timestamp_source': base,
              'timestamp_basis': 'Server pushed_at sampled against the exact public branch commit; no author-date or discovery-priority inference.',
              'release_url': None, 'doi': None, 'reproducibility_level': 'evidence_inspection'})
        seal(candidate, sources)
    if planned:
        write(folder / 'publication-receipt.json', {'batch': batch, 'records': [r['id'] for r in records],
              'record_count': len(records), 'first_disclosure_commit': commit,
              'github_pushed_at_observed': repository['pushed_at'], 'release_url': None,
              'reproducibility_level': 'evidence_inspection'})
        write(root / 'catalogue.json', json.loads(catalogue.index_bytes(validate_records(root, False))))
    return {'status': 'recorded', 'updated_records': len(planned)}


def record_release(root, batch, repo, tag, certificate_path):
    """Append actual server release metadata, preserving first-disclosure receipts."""
    records, _, folder = batch_records(root, batch)
    certificate = load(certificate_path)
    if certificate.get('status') != 'passed' or certificate.get('verification_kind') != 'public_evidence_inspection':
        raise ValueError('A passed public evidence-inspection certificate is required')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Invalid GitHub repository')
    tag = safe_name(tag)
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        metadata_url = f'https://api.github.com/repos/{repo}/releases/tags/{urllib.parse.quote(tag)}'
        metadata = load(fetch(metadata_url, work / 'release.json'))
        manifest = load(fetch(f'https://github.com/{repo}/releases/download/{tag}/release-manifest.json', work / 'manifest.json'))
    if (metadata['draft'] or not metadata['immutable'] or not metadata['published_at'] or
            certificate['release_url'] != metadata['html_url'] or
            certificate['source_commit'] != manifest['source_commit'] or
            manifest['source_commit'] != metadata['target_commitish'] or
            certificate['archive_sha256'] != manifest['asset']['sha256']):
        raise ValueError('Release metadata and public certificate disagree')
    locked = {r['id']: r for r in manifest['records']}
    if set(locked) != {r['id'] for r in records}:
        raise ValueError('Release does not cover exactly this selected batch')
    planned = []
    for record in records:
        if record['publication']['state'] == 'draft' or not record['publication']['first_public_utc']:
            raise ValueError('Record first Git disclosure before recording a release')
        candidate = root / 'candidates' / record['id']
        frozen = json.loads(subprocess.check_output(
            ['git', 'show', manifest['source_commit'] + ':candidates/' + record['id'] + '/candidate.json'],
            cwd=root, text=True))
        for key in (set(record) | set(frozen)) - {'version', 'history', 'publication'}:
            if record.get(key) != frozen.get(key):
                raise ValueError('Current science differs from the locked release')
        frozen_manifest = json.loads(subprocess.check_output(
            ['git', 'show', manifest['source_commit'] + ':candidates/' + record['id'] + '/evidence-manifest.json'],
            cwd=root, text=True))
        for artifact in frozen_manifest['files']:
            if artifact['path'] not in {'candidate.json', 'publication-receipt.json'}:
                if sha(candidate / artifact['path']) != artifact['sha256']:
                    raise ValueError('Current scientific artifact differs from the locked release')
        if datetime.fromisoformat(metadata['published_at'].replace('Z', '+00:00')) < datetime.fromisoformat(record['publication']['first_public_utc'].replace('Z', '+00:00')):
            raise ValueError('Release precedes first disclosure')
        if record['publication']['release_url'] == metadata['html_url']:
            continue  # Exact repeated delivery does not create another version/date.
        planned.append((record, candidate))
    for record, candidate in planned:
        source_hashes = {r['path']: r['source_sha256'] for r in load(candidate / 'evidence-manifest.json')['files'] if 'source_sha256' in r}
        major, minor, patch = map(int, record['version'].split('.'))
        record['version'] = f'{major}.{minor}.{patch + 1}'
        record['publication'].update(state='published', release_url=metadata['html_url'])
        record['history'].append({'date': datetime.now(timezone.utc).date().isoformat(), 'version': record['version'],
                                  'change': 'Record immutable batch release receipt; scientific evidence unchanged.'})
        receipt = load(candidate / 'publication-receipt.json')
        receipt.update(release_url=metadata['html_url'], release_published_utc=metadata['published_at'],
                       release_immutable=True, release_source_commit=manifest['source_commit'],
                       locked_dossier_version=locked[record['id']]['version'], release_api_source=metadata_url)
        write(candidate / 'candidate.json', record)
        write(candidate / 'publication-receipt.json', receipt)
        seal(candidate, source_hashes)
    write(folder / 'public-evidence-certificate.json', certificate)
    write(folder / 'release-manifest.json', manifest)
    batch_receipt = load(folder / 'publication-receipt.json')
    versions = {identifier: row['version'] for identifier, row in locked.items()}
    unique_versions = set(versions.values())
    batch_receipt.update(release_url=metadata['html_url'], release_published_utc=metadata['published_at'],
                         release_immutable=True, release_id=metadata['id'],
                         release_source_commit=manifest['source_commit'],
                         locked_dossier_versions=versions,
                         locked_dossier_version=next(iter(unique_versions)) if len(unique_versions) == 1 else None)
    write(folder / 'publication-receipt.json', batch_receipt)
    write(root / 'catalogue.json', json.loads(catalogue.index_bytes(validate_records(root, False))))
    return {'status': 'recorded', 'updated_records': len(planned)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    package = commands.add_parser('prepare')
    package.add_argument('--root', type=Path, required=True)
    package.add_argument('--batch', required=True)
    package.add_argument('--tag', required=True)
    package.add_argument('--output', type=Path, required=True)
    verify = commands.add_parser('verify-public')
    verify.add_argument('--repo', required=True)
    verify.add_argument('--tag', required=True)
    verify.add_argument('--expected-sha256', required=True)
    verify.add_argument('--certificate', type=Path, required=True)
    receipt = commands.add_parser('record-release')
    receipt.add_argument('--root', type=Path, required=True)
    receipt.add_argument('--batch', required=True)
    receipt.add_argument('--repo', required=True)
    receipt.add_argument('--tag', required=True)
    receipt.add_argument('--certificate', type=Path, required=True)
    disclosure = commands.add_parser('record-disclosure')
    disclosure.add_argument('--root', type=Path, required=True)
    disclosure.add_argument('--batch', required=True)
    disclosure.add_argument('--repo', required=True)
    disclosure.add_argument('--commit', required=True)
    disclosure.add_argument('--previous-public-commit', required=True)
    local = commands.add_parser('inspect-assets')
    local.add_argument('--archive', type=Path, required=True)
    local.add_argument('--manifest', type=Path, required=True)
    local.add_argument('--expected-sha256', required=True)
    local.add_argument('--certificate', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        result = prepare(args.root, args.batch, args.tag, args.output)
    elif args.command == 'verify-public':
        result = verify_public(args.repo, args.tag, args.expected_sha256, args.certificate)
    elif args.command == 'record-release':
        result = record_release(args.root, args.batch, args.repo, args.tag, args.certificate)
    elif args.command == 'record-disclosure':
        result = record_disclosure(args.root, args.batch, args.repo, args.commit, args.previous_public_commit)
    else:
        result = inspect_assets(args.archive, args.manifest, args.expected_sha256, args.certificate)
    summary = {'status': result.get('status', 'prepared')}
    if 'updated_records' in result:
        summary['updated_records'] = result['updated_records']
    else:
        summary['selected_records'] = result.get('new_signal_count', result.get('selected_records_verified'))
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
