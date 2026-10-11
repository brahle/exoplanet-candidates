"""Figure staging refuses stale science before copying and is idempotent."""
import copy
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalogue
import publish_figures
from export_batch import load, seal, sha, write


def fixture(base):
    root = base / 'repo'; root.mkdir()
    shutil.copytree(ROOT / 'schemas', root / 'schemas')
    folder = root / 'candidates/tic-101909456-s01'
    shutil.copytree(ROOT / 'candidates/tic-101909456-s01', folder)
    # Fixtures remain pre-figure records even after the live catalogue is enriched.
    figure_folder = folder / 'evidence/figures'
    if figure_folder.exists():
        shutil.rmtree(figure_folder)
    record = load(folder / 'candidate.json')
    record['evidence'] = [p for p in record['evidence'] if not p.startswith('evidence/figures/')]
    write(folder / 'candidate.json', record)
    previous = load(folder / 'evidence-manifest.json')
    seal(folder, {f['path']: f['source_sha256'] for f in previous['files'] if 'source_sha256' in f})
    source = base / 'source'; case = source / record['id']; case.mkdir(parents=True)
    (case / 'diagnostic.png').write_bytes(b'fixture image, not scientific data')
    (case / 'plot-data.npz').write_bytes(b'fixture vectors')
    write(case / 'plot-context.json', {'candidate_id': record['id'],
        'plot_data_sha256': sha(case / 'plot-data.npz'), 'ephemeris':
        {k: record['signal'][k] for k in ('period_d', 'epoch_btjd', 'duration_h', 'depth_ppm')}})
    files = {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in case.iterdir()}
    row = {'candidate_id': record['id'], 'source_candidate_sha256': sha(folder / 'candidate.json'),
        'scientific_record_sha256': publish_figures.science_hash(record), 'images': ['diagnostic.png'],
        'files': files}
    report = source / 'report.json'
    write(report, {'source_run': 'fixture', 'records': [row]})
    write(source / 'input-binding.json', {'code_sha256': {'figure_render.py': 'a' * 64}})
    manifest = source / 'manifest.json'
    write(manifest, {'ok': True, 'command': 'vet-figures', 'run_id': 'fixture',
        'git': {'commit': 'b' * 40}, 'outputs': {'report.json': sha(report),
            'input-binding.json': sha(source / 'input-binding.json')}})
    return root, source, folder, record, report, manifest


class FigurePublication(unittest.TestCase):
    def test_science_preserved_and_repeat_changes_no_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, source, folder, old, report, manifest = fixture(Path(temporary))
            self.assertEqual(publish_figures.stage(root, source, report, manifest)['updated_records'], 1)
            current = load(folder / 'candidate.json')
            for key in ('target', 'signal', 'assessment', 'novelty', 'host', 'fit', 'publication'):
                self.assertEqual(current.get(key), old.get(key))
            original_root = catalogue.ROOT
            try:
                catalogue.ROOT = root
                catalogue.records()
            finally:
                catalogue.ROOT = original_root
            self.assertEqual(publish_figures.stage(root, source, report, manifest)['updated_records'], 0)
            self.assertTrue((root / 'gallery/page-01.md').exists())

    def test_bad_figure_and_science_refused_before_delivery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, source, folder, old, report, manifest = fixture(Path(temporary))
            original = (source / old['id'] / 'diagnostic.png').read_bytes()
            (source / old['id'] / 'diagnostic.png').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'bytes changed'):
                publish_figures.stage(root, source, report, manifest)
            self.assertFalse((folder / 'evidence/figures').exists())
            (source / old['id'] / 'diagnostic.png').write_bytes(original)
            changed = copy.deepcopy(old); changed['signal']['depth_ppm']['value'] += 1
            write(folder / 'candidate.json', changed)
            previous = load(folder / 'evidence-manifest.json')
            seal(folder, {f['path']: f['source_sha256'] for f in previous['files'] if 'source_sha256' in f})
            with self.assertRaisesRegex(ValueError, 'scientific record differs'):
                publish_figures.stage(root, source, report, manifest)
            self.assertFalse((folder / 'evidence/figures').exists())


if __name__ == '__main__':
    unittest.main()
