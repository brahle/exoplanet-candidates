# Diagnostic figures

[Browse the gallery](../gallery/README.md). Every dossier has a five-panel PNG:
normalized light curves and saved baselines, recorded BLS spectrum, folded profiles,
odd/even curves and chronological individual events. PNGs are 2520×1960 pixels.
Additional 1680×1680 event pages show all saved numeric events, including negative
depths. Failed events and withheld products stay in the JSON context.

These are diagnostic illustrations of provisional unclassified signals. They
add no physical fit, planet designation, false-alarm probability or new measurement.

Run-5 timelines use the primary acquisition masks (quality-zero, finite positive
flux) and sector-median normalization. Red segments are saved local baselines;
no global detrending is claimed. Folds subtract the saved additive baseline from
signed fixed-centre profiles, preserving event depths of both signs. The red
profile line averages the saved models with their recorded ingress setting;
it is distinct from the joint refinement and separately measured box-window depth.
The duration and its conditional error are read from the dossier.

The recorded periodogram is the uniquely matching observed full-search
reconstruction, not a new search. Its sectors and preprocessing/time scope can
differ from the fold, including clock-unverified QLP products withheld from local
profiles. Original launch provenance remains unbound. An unavailable unique
spectrum is explicitly marked rather than silently substituted.

The TIC464547401 adapter renders saved historical Phase-1 masked-biweight flux
and its saved search spectrum. Its QLP clock assumptions remain unresolved; this
view does not supersede later timing/clock evidence in its dossier.

Fold and odd/even bins contain at least two cadences. Error bars are sample
scatter/sqrt(N); red-noise coverage is uncalibrated. Individual-event display bins
allow a single cadence, with no uncertainty estimate. Event paths break across
missing bins. The overview shows the first twelve chronological numeric events,
with complete event pages linked. Sector gaps are compressed; within-sector gaps
remain. The folded y-axis zoom covers all binned means plus two display errors and
25% margin; the number of off-scale raw points is printed. Every underlying point
is retained in `plot-data.npz`.

## Regenerate the rendering

The public standalone renderer is an exact copy of the pipeline source. With
NumPy and Matplotlib installed:

```
python scripts/render_figures.py candidates/tic-101909456-s01/evidence/figures
```

The renderer checks the vector SHA-256 recorded in `plot-context.json`. Run the
repository catalogue check first to verify the context, vectors and PNGs against
the dossier manifest. Pixel identity requires the recorded rendering environment;
different library/font versions may render differently. Replotting saved evidence
is not a fresh numerical reproduction of acquisition, searches or fits.

`scripts/publish_figures.py` checks the complete catalogue against the Run report,
exact scientific-record hash, ephemeris and every artifact hash before copying.
It preserves scientific fields, classifications and disclosure timestamps, adds
patch versions and dated history, reseals dossiers and builds the gallery. Repeat
staging is idempotent. Git publication remains a separate explicit action.
