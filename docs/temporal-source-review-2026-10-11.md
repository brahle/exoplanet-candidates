# Joint temporal source/noise review — 11 October 2026

Supplement version **1.0.0**, following the [paired source-method diagnosis](source-control-review-2026-10-11.md).
This is an anonymous method pilot over24 source-batch records; existing dossiers,
scientific assessments, disclosure dates and browsing counts remain unchanged.

[Recorded aggregate results, scope and receipt hash](../reviews/temporal-source-review-2026-10-11-v1.json).

The new model fits signed transit-template amplitudes at prespecified catalogue
positions jointly with signed spatial-background terms and per-event pixel baselines.
Noise parameters are estimated only from out-of-transit samples: empirical pixel
covariance with declared diagonal shrinkage, and either white time noise or a common
stationary OU correlation with actual gaps. Neither model uses injected coordinates
to choose a centroid. Missing data and correlation measurements remain explicit.

Independent dense covariance calculations check the GLS algebra, signed mixtures,
near blends, rank limits and training isolation. The24-record pilot completed all
case executions in29.31seconds. Twenty-one records yielded actual-ephemeris fits;
three lacked three usable events in the first-sector selection. Those are unavailable
results for this recipe, not rejected astrophysical signals.

The two fields used in the preceding diagnosis are grouped separately from the
other22. New control phases0.17/0.43/0.79 were declared before the run. This object/
phase split is not an independent astrophysical validation population. Only the
first eligible sector was used; combining sectors remains outside this experiment.

| Field group | Noise model | Usable shifted trains | Distinct field/source/phase comparisons | Nominal amplitude-interval misses |
|---|---|---:|---:|---:|
| Development fields | White | 4 | 8 | 0 |
| Development fields | Common OU | 4 | 8 | 0 |
| Additional fields | White | 55 | 107 | 3 |
| Additional fields | Common OU | 55 | 107 | 3 |

Three requested injection levels were retained per comparison. They repeat the same
linear estimator, and brightness caps can duplicate actual levels; the table counts
each field/source/phase once. Noise models and phase trains also share photons.
These counts are not independent error-rate trials, confidence bounds or planet
probabilities. The intervals concern template amplitudes, not centroid positions.
They cannot be directly compared with the earlier centroid-ellipse diagnostics.

An injected coefficient increment is exact under this fixed linear model. That is
an algebraic identity, not a detection or coverage certificate. Untreated background
signals can shift the estimated total coefficient away from the imposed loss alone.
Surviving nominal misses therefore require investigation of background means and
variable-mode temporal correlation, rather than automatic signal rejection or
interval widening until everything passes.

Static positions/PRFs, bounded source selection, covariance/hyperparameter uncertainty,
nonstationarity, clock assumptions and omitted competing hosts remain limitations.
**Source attribution stays unresolved.** No candidate or planet promotion follows.

Public reproducibility is **evidence inspection only** for this method note. Exact
individual records remain outside this public aggregate, and a public raw-input
numerical capsule for this source pilot has not been supplied. The existing
[exposure-integration replay](exposure-integration-review-2026-10-11.md) covers its
own selected-input calculation, not this experiment or the complete vetting pipeline.
