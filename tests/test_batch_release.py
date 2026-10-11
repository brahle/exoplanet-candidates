"""A release must bind its reviewed ledger and reject stale or unsafe evidence."""
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import batch_release as release
from export_batch import seal, write


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def fixture(root, draft=False):
    root.mkdir()
    candidate = root / 'candidates/tic-464547401-s01'
    shutil.copytree(ROOT / 'candidates/tic-464547401-s01', candidate)
    shutil.copytree(ROOT / 'schemas', root / 'schemas')
    record = release.load(candidate / 'candidate.json')
    if draft:
        record['publication'].update(state='draft', first_public_utc=None, disclosure_url=None)
        record['evidence'].remove('publication-receipt.json')
        (candidate / 'publication-receipt.json').unlink()
        write(candidate / 'candidate.json', record)
    settings = release.load(candidate / 'analysis-settings.json')
    settings['original_assessment_sha256'] = 'b' * 64
    write(candidate / 'analysis-settings.json', settings)
    seal(candidate, {})
    folder = root / 'batches/fixture'
    write(folder / 'outcomes.json', {'count': 1, 'routes': {'provisional_signal_record': 1},
          'report_sha256': 'a' * 64, 'outcomes': [{'signal_id': record['id'], 'route': 'provisional_signal_record', 'assessment_sha256': 'b' * 64}]})
    review = {'signal_id': record['id'], 'assessment_sha256': 'b' * 64,
              'disposition': record['assessment']['disposition'], 'publication_tier': 'evidence_inspection'}
    review['review_id'] = hashlib.sha256(json.dumps(review, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    write(folder / 'reviews.json', {'report_sha256': 'a' * 64, 'reviews': [review]})
    write(folder / 'publication-receipt.json', {'batch': 'fixture', 'records': [record['id']]})
    write(root / 'catalogue.json', json.loads(release.catalogue.index_bytes(release.validate_records(root, False))))
    git(root, 'init', '-b', 'main'); git(root, 'config', 'user.name', 'Fixture')
    git(root, 'config', 'user.email', 'fixture@example.invalid')
    git(root, 'add', '.'); git(root, 'commit', '-qm', 'Fixture only')
    return candidate


class BatchRelease(unittest.TestCase):
    def test_prepared_archive_binds_records_reviews_and_conservation(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); root = base / 'repo'; fixture(root)
            manifest = release.prepare(root, 'fixture', 'fixture-v1', base / 'assets')
            extracted = base / 'extracted'; extracted.mkdir()
            _, count = release.inspect_archive(base / 'assets/fixture-v1-evidence.tar.gz', manifest, manifest['asset']['sha256'], extracted)
            self.assertEqual(count, 1)
            self.assertEqual(manifest['new_signal_count'], 1)
            with self.assertRaisesRegex(ValueError, 'replace a prepared'):
                release.prepare(root, 'fixture', 'fixture-v1', base / 'assets')

    def test_stale_review_and_empty_selection_cannot_prepare_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'repo'; fixture(root)
            path = root / 'batches/fixture/reviews.json'; doc = release.load(path)
            doc['report_sha256'] = 'c' * 64; write(path, doc)
            with self.assertRaisesRegex(ValueError, 'source report differs'):
                release.batch_records(root, 'fixture')
            doc['report_sha256'] = 'a' * 64; write(path, doc)
            path = root / 'batches/fixture/outcomes.json'; out = release.load(path)
            out['outcomes'][0]['route'] = 'prior_report_or_match_hypothesis'
            out['routes'] = {'prior_report_or_match_hypothesis': 1}; write(path, out)
            with self.assertRaisesRegex(ValueError, 'No selected'):
                release.batch_records(root, 'fixture')

    def test_wrong_checksum_and_unsafe_tar_cannot_validate(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); archive = base / 'unsafe.tar.gz'
            with tarfile.open(archive, 'w:gz') as stream:
                entry = tarfile.TarInfo('../../escape'); entry.size = 1
                stream.addfile(entry, io.BytesIO(b'x'))
            manifest = {'reproducibility_level': 'evidence_inspection', 'asset': {'bytes': archive.stat().st_size, 'sha256': release.sha(archive)}}
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                release.inspect_archive(archive, manifest, '0' * 64, base / 'out')
            with self.assertRaises(tarfile.TarError):
                release.inspect_archive(archive, manifest, manifest['asset']['sha256'], base / 'out')
            self.assertFalse((base.parent / 'escape').exists())

    def test_timestamp_receipts_are_idempotent_and_preserve_science(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); root = base / 'repo'; folder = fixture(root, draft=True)
            before = release.load(folder / 'candidate.json')['signal']
            commit = git(root, 'rev-parse', 'HEAD')
            def disclosure_fetch(url, path):
                write(path, {'commit': {'sha': commit}} if '/branches/' in url else
                      {'private': False, 'default_branch': 'main', 'pushed_at': '2026-10-12T01:00:00Z'})
                return path
            with patch.object(release, 'fetch', disclosure_fetch):
                self.assertEqual(release.record_disclosure(root, 'fixture', 'fixture/repo', commit, 'none')['updated_records'], 1)
                self.assertEqual(release.record_disclosure(root, 'fixture', 'fixture/repo', commit, 'none')['updated_records'], 0)
            git(root, 'add', '.'); git(root, 'commit', '-qm', 'Disclosure receipt')
            manifest = release.prepare(root, 'fixture', 'fixture-v1', base / 'assets')
            url = 'https://github.com/fixture/repo/releases/tag/fixture-v1'
            metadata = {'draft': False, 'immutable': True, 'published_at': '2026-10-12T02:00:00Z',
                        'html_url': url, 'target_commitish': manifest['source_commit'], 'id': 1}
            cert = base / 'certificate.json'; write(cert, {'status': 'passed', 'verification_kind': 'public_evidence_inspection',
                 'release_url': url, 'source_commit': manifest['source_commit'], 'archive_sha256': manifest['asset']['sha256']})
            def release_fetch(address, path):
                write(path, manifest if address.endswith('/release-manifest.json') else metadata)
                return path
            with patch.object(release, 'fetch', release_fetch):
                self.assertEqual(release.record_release(root, 'fixture', 'fixture/repo', 'fixture-v1', cert)['updated_records'], 1)
                self.assertEqual(release.record_release(root, 'fixture', 'fixture/repo', 'fixture-v1', cert)['updated_records'], 0)
            after = release.load(folder / 'candidate.json')
            self.assertEqual(after['signal'], before)
            self.assertEqual(after['publication']['first_public_utc'], '2026-10-12T01:00:00Z')
            self.assertEqual(after['publication']['state'], 'published')
            self.assertEqual(release.load(folder / 'publication-receipt.json')['release_published_utc'], '2026-10-12T02:00:00Z')
