"""Batch capsules preserve science, close dependencies and remain size bounded."""
import copy
import io
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from test_batch_release import fixture, git, ROOT
import batch_release as release
import batch_package as package
from export_batch import load, seal, write


def capsule_fixture(base):
    root = base / 'repo'; selected = fixture(root)
    for tic in ('999', '998'):
        folder = root / 'candidates' / f'tic-{tic}-s01'
        shutil.copytree(selected, folder)
        record = load(folder / 'candidate.json');record['id'] = folder.name;record['target']['tic'] = tic
        record['evidence'] = [p for p in record['evidence'] if p != 'vetting.json']
        (folder / 'vetting.json').unlink(missing_ok=True)
        write(folder / 'candidate.json', record);seal(folder, {})
    shutil.copytree(ROOT / 'scripts', root / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('pyproject.toml', 'uv.lock'):
        shutil.copy2(ROOT / name, root / name)
    write(root / 'tests/fixture-dossiers.json', {'dossier_ids': ['tic-999-s01']})
    (root / 'tests/test_fixture.py').write_text('import unittest\nclass Fixture(unittest.TestCase):\n def test_environment(self): self.assertTrue(True)\n')
    shared = root / 'batches/other/snapshot.json';write(shared, {'fixture': 'pinned shared bytes'})
    write(selected / 'evidence/shared-context.json', {'raw_responses': [{'path':'batches/other/snapshot.json', 'sha256':release.sha(shared)}]})
    seal(selected, {})
    write(root / 'catalogue.json', __import__('json').loads(release.catalogue.index_bytes(release.validate_records(root, False))))
    git(root, 'add', '.');git(root, 'commit', '-qm', 'Capsule fixture only')
    return root


def packed(base):
    root=capsule_fixture(base)
    manifest=release.prepare(root,'fixture','fixture-v2',base/'assets')
    extracted=base/'extracted';extracted.mkdir()
    capsule,count=release.inspect_archive(base/'assets/fixture-v2-evidence.tar.gz',manifest,manifest['asset']['sha256'],extracted)
    return root,manifest,capsule,count


class BatchPackage(unittest.TestCase):
    def test_subset_copies_selected_and_declared_fixtures_with_shared_closure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root,m,capsule,count=packed(Path(temporary))
            self.assertEqual((m['source_catalogue_count'],m['new_signal_count'],count),(3,1,2))
            self.assertEqual(m['packaged_dossier_count'],2)
            self.assertEqual([r['id'] for r in m['support_records']],['tic-999-s01'])
            self.assertFalse((capsule/'candidates/tic-998-s01').exists())
            self.assertEqual((root/'batches/other/snapshot.json').read_bytes(),(capsule/'batches/other/snapshot.json').read_bytes())
            for name,row in m['source_files'].items():
                self.assertEqual((capsule/name).read_bytes(),(root/row['source_path']).read_bytes())
            self.assertIn('catalogue.json',m['derived_files'])
            self.assertIn('package-provenance/source-catalogue.json',m['source_files'])
            with tarfile.open(Path(temporary)/'assets/fixture-v2-evidence.tar.gz') as stream:
                self.assertTrue(all(x.uid == x.gid == 0 and x.uname == x.gname == 'root' for x in stream))

    def test_unlisted_files_and_stale_copied_hashes_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            _,m,capsule,_=packed(Path(temporary))
            (capsule/'extra.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'Unlisted'):
                package.verify(capsule,m)
            (capsule/'extra.json').unlink()
            path=capsule/'batches/other/snapshot.json';path.write_text(path.read_text().replace('pinned', 'broken'))
            with self.assertRaisesRegex(ValueError,'hash or size mismatch'):
                package.verify(capsule,m)

    def test_invented_counts_and_extra_record_identities_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            _,m,capsule,_=packed(Path(temporary))
            wrong=copy.deepcopy(m);wrong['source_catalogue_count']+=1
            with self.assertRaisesRegex(ValueError,'scope'):
                package.verify(capsule,wrong)
            wrong=copy.deepcopy(m);wrong['support_records'][0]['id']='tic-998-s01'
            with self.assertRaisesRegex(ValueError,'fixtures'):
                package.verify(capsule,wrong)

    def test_scientific_files_cannot_be_relabelled_as_generated_views(self):
        with tempfile.TemporaryDirectory() as temporary:
            _,m,capsule,_=packed(Path(temporary))
            name='candidates/tic-464547401-s01/evidence/shared-context.json'
            wrong=copy.deepcopy(m);row=wrong['source_files'].pop(name)
            wrong['derived_files'][name]={k:row[k] for k in ('bytes','sha256')}
            with self.assertRaisesRegex(ValueError,'Scientific files'):
                package.verify(capsule,wrong)

    def test_missing_or_wrong_hash_dependency_fails_before_packaging(self):
        for missing in (True,False):
            with tempfile.TemporaryDirectory() as temporary:
                base=Path(temporary);root=capsule_fixture(base)
                path=root/'batches/other/snapshot.json'
                if missing:path.unlink()
                else:path.write_text('{}')
                git(root,'add','.');git(root,'commit','-qm','Invalid dependency fixture')
                with self.assertRaisesRegex(ValueError,'shared dependency|Shared dependency'):
                    release.prepare(root,'fixture','fixture-v2',base/'assets')

    def test_preparation_keeps_the_existing_size_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary);root=capsule_fixture(base)
            with patch.object(package,'MAX_BYTES',1):
                with self.assertRaisesRegex(ValueError,'inspection limits'):
                    release.prepare(root,'fixture','fixture-v2',base/'assets')
            self.assertFalse((base/'assets/fixture-v2-evidence.tar.gz').exists())

    def test_duplicate_and_link_archive_members_fail_before_extraction(self):
        for link in (False,True):
            with tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary);archive=root/'bad.tar'
                with tarfile.open(archive,'w') as out:
                    first=tarfile.TarInfo('fixture/data');first.size=1;out.addfile(first,io.BytesIO(b'x'))
                    second=tarfile.TarInfo('fixture/data')
                    if link:second.type=tarfile.SYMTYPE;second.linkname='/outside'
                    else:second.size=1
                    out.addfile(second,None if link else io.BytesIO(b'y'))
                with tarfile.open(archive) as stream:
                    with self.assertRaises(ValueError):package.extract(stream,root/'out')
                self.assertFalse((root/'out').exists())

    def test_size_and_member_limits_fail_before_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);archive=root/'small.tar'
            with tarfile.open(archive,'w') as stream:
                entry=tarfile.TarInfo('fixture/data');entry.size=1;stream.addfile(entry,io.BytesIO(b'x'))
            for key in ('MAX_BYTES','MAX_MEMBERS'):
                with patch.object(package,key,0),tarfile.open(archive) as stream:
                    with self.assertRaisesRegex(ValueError,'inspection limits'):package.extract(stream,root/'out')
                self.assertFalse((root/'out').exists())
