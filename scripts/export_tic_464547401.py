"""Export a bounded scientific snapshot without private run/environment metadata.

This exports existing results; it does not rerun the analysis. Supply a local
transit-search checkout as the only argument. Existing Phase 1/2 bytes stay untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'candidates/tic-464547401-s01'


def read(path):
    return json.loads(path.read_text())


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    current = DEST / 'candidate.json'
    if current.exists() and read(current)['publication']['state'] != 'draft':
        raise ValueError('Published dossier: prepare a new reviewed version; do not overwrite disclosure history.')
    source = args.source.resolve()
    p1 = source / 'results/evidence/2026-10-10-tic-464547401-vetting'
    p2 = source / 'results/evidence/2026-10-10-tic-464547401-phase2'
    originals = {}
    selections = {
        'phase1': (p1, [
            'analysis/ephemerides.json', 'analysis/events.csv', 'analysis/all_baseline_predictions.csv',
            'analysis/robustness.csv', 'analysis/robustness_failures.json', 'analysis/bls_compute_stats.json',
            'analysis/overlap_audit.json', 'analysis/final_folds.png', 'analysis/retrospective_folds.png',
            'catalogues/catalogue_summary.json', 'catalogues/nasa_toi.csv', 'catalogues/nasa_pscomppars.csv',
            'reproducibility/comparison.json',
        ]),
        'phase2': (p2, [
            'analysis/event_timings.csv', 'analysis/timing_ephemerides.json', 'analysis/timing_sensitivity.csv',
            'analysis/leave_one_event_out.csv', 'analysis/aperture_depths.csv', 'analysis/aperture_pairs.csv',
            'analysis/pixel_events.csv', 'analysis/contaminants.csv', 'analysis/neighbours.csv',
            'analysis/source_summary.json', 'analysis/stellar_density.json', 'analysis/s13_baseline_comparison.csv',
            'analysis/s13_flagged_cadences.csv', 'analysis/source_aperture_summary.png',
            'analysis/timing_predictions.png', 'analysis/event_timing_profiles.png',
            'analysis/s13_instrument_baselines.png', 'analysis/stellar_duration_constraint.png',
            'reproducibility/comparison.json',
        ] + [f'analysis/difference_s{s}_FFI_SPOC_FFI.png' for s in [13, 67, 94, 101, 102, 103, 104]]),
    }
    for label, (base, paths) in selections.items():
        for relative in paths:
            src = base / relative
            # Check scientific outputs against the preserved run, not against a
            # newly calculated hash of a possibly edited local file.
            section, name = relative.split('/', 1)
            original_manifest = base / section / 'manifest.json'
            if original_manifest.exists():
                expected = read(original_manifest)['outputs'].get(name)
                if expected is None or hashlib.sha256(src.read_bytes()).hexdigest() != expected:
                    raise ValueError(f'Preserved source artifact changed: {label}/{relative}')
            dest = DEST / 'evidence' / label / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            originals[dest.relative_to(DEST).as_posix()] = hashlib.sha256(src.read_bytes()).hexdigest()
    # ExoFOP responses include community content: retain their checksummed source
    # identifiers and dated query outcomes, rather than blanket republishing bulk tables.
    catalogue = read(p1 / 'catalogues/catalogue_summary.json')
    ephem = read(p1 / 'analysis/ephemerides.json')
    joint = ephem['shared_final']
    cov = joint['bootstrap_covariance_epoch_period']
    depth = ephem['shared_final_depth']
    lightcurve = read(source / 'data/manifests/tic-464547401-vetting.json')
    pixels = read(source / 'data/manifests/tic-464547401-phase2.json')
    allowed = ['author', 'mission', 'target_name', 'obs_id', 'productFilename', 'dataURI', 'sha256', 'bytes',
               'sector', 'kind', 'ticid', 'identity_check', 'bjd_reference', 'timesys', 'timeref', 'timeunit',
               'time_min_btjd', 'time_max_btjd', 'n_rows', 'primary', 'flux_column', 'exposure_seconds',
               'camera', 'ccd', 'shape']
    write(DEST / 'inputs.json', {
        'description': 'Scientific input identifiers; raw files are not included in this evidence-only draft.',
        'lightcurves': [{k: r[k] for k in allowed if k in r} for r in lightcurve['products']],
        'pixels': [{k: r[k] for k in allowed if k in r} for r in pixels['products']],
        'pixel_exclusions': {'66': 'Target outside CCD science rows.', '93': 'Target outside CCD science rows.'},
        'retrieval_limit': 'MAST identifiers are public. Exact archived TESScut bytes are not yet mirrored publicly; a regenerated cutout may have different FITS headers/checksums.',
    })
    # Export scientific settings separately from operational paths/archival settings.
    import tomllib
    one = tomllib.loads((source / 'configs/survey/vetting-464547401.toml').read_text())
    two = tomllib.loads((source / 'configs/survey/phase2-464547401.toml').read_text())
    write(DEST / 'analysis-settings.json', {
        'phase1': {k: one[k] for k in ['catalogue_radius_arcsec', 'identity_radius_arcsec', 'period_match_fraction', 'epoch_match_hours', 'original', 'analysis', 'robustness']},
        'phase2': {k: two[k] for k in ['recent_sectors', 'seed', 'pixels', 'timing', 'stellar']},
        'description': 'Settings export, not a directly runnable replacement for the original configs.',
    })
    record = {
        'schema_version': '1.0', 'id': 'tic-464547401-s01', 'version': '0.1.0',
        'title': 'TIC 464547401: a 13.24438-day transit-like signal',
        'target': {'tic': '464547401', 'gaia_dr3': '6435059343942224256',
                   'aliases': one['identifiers'], 'coordinates': {
                       'ra_deg': one['ra_deg'], 'dec_deg': one['dec_deg'], 'frame': 'ICRS',
                       'epoch': 'J2000', 'provenance': 'TIC/SPOC target coordinates; proper-motion propagation used separately for pixel localisation.'}},
        'signal': {
            'period_d': {'value': joint['period_d'], 'error': math.sqrt(cov[1][1])},
            'epoch_btjd': {'value': joint['epoch_btjd'], 'error': math.sqrt(cov[0][0])},
            'epoch_bjd_tdb': joint['epoch_btjd'] + 2457000, 'bjd_offset': 2457000, 'time_scale': 'TDB',
            'covariance_epoch_period_d2': cov,
            'covariance_method': 'Phase 1 joint 128-repetition, 30-minute block-bootstrap covariance; marginal errors from this same covariance.',
            'duration_h': {'value': joint['duration_h'], 'error': joint['duration_error_h']},
            'depth_ppm': {'value': depth['depth_ppm'], 'error': depth['error_ppm']},
            'model': joint['model'] + '; separately measured local box-window depth',
            'sectors': joint['fit_sectors'], 'covered_events': joint['n_events'],
            'limits': ['Conditional diagnostic model, not a physical transit inference.',
                       'No search-calibrated false-alarm rate or planet probability.',
                       'Host identity, dilution, eccentricity and recent/older timing consistency unresolved.']},
        'assessment': {
            'disposition': 'unclassified_transit_like_signal',
            'source_localisation': {'status': 'unresolved',
                'reason': 'Conditional multi-sector centroids favour the target, but close-source exclusion lacks adequate PRF/systematics calibration.',
                'evidence': ['evidence/phase2/analysis/source_summary.json', 'evidence/phase2/analysis/source_aperture_summary.png']},
            'timing_consistency': {'status': 'unresolved',
                'reason': 'Independent free-shape older/recent periods differ by 2.43 conditional sigma; baseline/shape sensitivity prevents a robust classification.',
                'evidence': ['evidence/phase2/analysis/timing_ephemerides.json', 'evidence/phase2/analysis/timing_sensitivity.csv']}},
        'novelty': {'status': 'no_match_in_checked_sources', 'checked_utc': catalogue['queried_utc'],
                    'evidence': ['evidence/phase1/catalogues/catalogue_summary.json', 'NOVELTY.md'],
                    'limits': catalogue['limits'] + ['No matching record is not a guarantee of novelty or discovery priority.']},
        'provenance': {
            'analysis_date': '2026-10-10',
            'source_revisions': {'phase1': 'fb6c56fb7ba246d3b2c796be13549c3634fc261a', 'phase2': '0108805fdec3fd925a05331b2e3de088902f36df'},
            'runs': {'phase1': '20261010T134148Z-tic-464547401-vetting-9ad8f9', 'phase2': '20261010T154424Z-tic-464547401-phase2-analyze-c8da15'},
            'input_lock': 'inputs.json'},
        'reproducibility': {
            'level': 'evidence_inspection', 'command': 'uv sync --frozen && uv run python scripts/catalogue.py check',
            'limits': ['This validates the public evidence package; it does not recompute light-curve or pixel fits.',
                       'Numerical reruns were verified privately. Public numerical reproduction remains incomplete.'],
            'requirements_for_numerical_release': ['Publish exact input bytes, code capsule, frozen dependency lock and original configs without private archival dependencies.',
                'Re-run from a clean environment using only publicly accessible inputs; publish the output comparison certificate.']},
        'publication': {'state': 'draft', 'first_public_utc': None, 'release_url': None, 'doi': None, 'authors': ['Bruno Rahle']},
        'evidence': sorted(originals) + ['inputs.json', 'analysis-settings.json', 'README.md', 'NOVELTY.md', 'REPRODUCIBILITY.md'],
        'history': [{'date': '2026-10-10', 'version': '0.1.0', 'change': 'Initial local dossier prepared from preserved Phase 1/2 results; no public-disclosure timestamp assigned.'}],
    }
    write(DEST / 'candidate.json', record)
    files = []
    for path in sorted(DEST.rglob('*')):
        if path.is_file() and path.name != 'evidence-manifest.json':
            relative = path.relative_to(DEST).as_posix()
            item = {'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
            if relative in originals:
                item['export_mode'] = 'byte-identical scientific artifact'
                item['source_sha256'] = originals[relative]
            else:
                item['export_mode'] = 'derived publication record or authored report'
            files.append(item)
    write(DEST / 'evidence-manifest.json', {'schema_version': '1.0', 'candidate': record['id'], 'files': files})
    print(f'Exported {len(originals)} unchanged scientific artifacts; {len(files)} manifest entries.')


if __name__ == '__main__':
    main()
