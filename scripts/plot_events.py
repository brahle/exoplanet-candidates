"""Plot the public saved event depths without fitting or changing their selection.

Requires matplotlib; use the scientific pipeline's locked figure environment.
"""
import argparse
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from export_batch import load, seal


def plot(folder):
    record = load(folder / 'candidate.json')
    events = load(folder / 'evidence/photometry.json')['events']
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for order, ax in enumerate(axes, 1):
        rows = [e for e in events if e['baseline_order'] == order and e.get('depth_ppm') is not None]
        good = [e for e in rows if e.get('usable') and e.get('error_ppm') is not None]
        bad = [e for e in rows if not e.get('usable')]
        if good:
            ax.errorbar([e['center_btjd'] for e in good], [e['depth_ppm'] for e in good],
                        yerr=[e['error_ppm'] for e in good], fmt='o', markersize=3,
                        color='#136b9b', alpha=.7, linewidth=.65, label='usable; conditional errors')
        if bad:
            ax.scatter([e['center_btjd'] for e in bad], [e['depth_ppm'] for e in bad],
                       s=14, marker='x', color='#b65024', alpha=.65, label='excluded; saved depth')
        ax.axhline(0, color='#555555', linewidth=.8)
        ax.set_title('Linear baseline' if order == 1 else 'Quadratic baseline')
        ax.set_xlabel('Predicted event centre, BTJD (BJD_TDB − 2457000)')
        ax.grid(alpha=.15)
        ax.legend(fontsize=7, loc='best')
    axes[0].set_ylabel('Signed dip depth (ppm)')
    fig.suptitle(f"TIC {record['target']['tic']} — provisional signal\nSaved event diagnostics; source, clock and error coverage unresolved", fontsize=12)
    fig.tight_layout(rect=(0, .045, 1, .91))
    fig.text(.5, .012, 'All numeric event-depth estimates shown; missing/non-numeric outcomes remain in photometry.json. No new fit.', ha='center', fontsize=8)
    relative = 'evidence/event-depths.png'
    fig.savefig(folder / relative, dpi=130)
    plt.close(fig)
    record['evidence'].append(relative)
    (folder / 'candidate.json').write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
    readme = folder / 'README.md'
    readme.write_text(readme.read_text() + '\n![Saved event-depth diagnostics](evidence/event-depths.png)\n')
    sources = {r['path']: r['source_sha256'] for r in load(folder / 'evidence-manifest.json')['files'] if 'source_sha256' in r}
    seal(folder, sources)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    folders = sorted(args.root.glob('*/candidate.json'))
    for path in folders:
        plot(path.parent)
    print(f'Plotted {len(folders)} dossiers')
