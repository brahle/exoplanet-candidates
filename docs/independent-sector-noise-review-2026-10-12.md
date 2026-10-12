# Independent-sector noise review — 12 October 2026

This follows the [held-out source-noise review](heldout-source-review-2026-10-12.md).
It separates independent fast scatter from slower stationary variability and
averages predictions over a declared finite grid of noise fractions and timescales.
**Source attribution remains unresolved, with no scientific promotions.**

Attempt all 24 previous records using each target's next available pixel sector.
Never substitute another sector because the new coverage or prediction fails.
Twenty targets support the test; four have insufficient events or full-duration
holdouts. These sectors have disjoint photons from the earlier noise experiments,
but may have appeared in the original search/source diagnostics. They are not an
independent planet-detection or astrophysical validation population.

Use full nominal-transit-duration OOT holdouts with a one-cadence training buffer.
Learn the spatial basis and select its largest three variance modes from training
pixels only. Conditional predictions integrate linear-mean/scale uncertainty and
average over the declared finite time/fraction prior. Spatial-basis uncertainty,
cross-mode dependence, nonstationarity and prior/grid sensitivity remain open.
Fast scatter is not asserted to be a verified photon-noise component.

| Cohort | Available / attempted targets | Paired modes | Point/mode evaluations per model | White nominal tail misses | Pure-OU grid misses | White/OU mixture misses |
|---|---:|---:|---:|---:|---:|---:|
| Development | 2 / 2 | 6 | 1,200 | 41 | 26 | 26 |
| Additional fields | 18 / 22 | 54 | 27,048 | 560 | 551 | 531 |

The counts use predictive-mixture CDF values outside the central nominal 99%
interval. They are correlated descriptive checks, not independent coverage bounds,
false-alarm rates or planet probabilities. Models share the same evaluation data;
counts must not be compared as rates with the earlier-sector experiments.

The full mixture has a higher mean per-block predictive score than the pure-OU
grid in 23 of 54 additional-field comparisons and two of six development
comparisons. The median difference is zero in both groups. Including fast scatter
and finite-grid uncertainty does not produce a uniform predictive improvement or
establish source-model adequacy.

The grid contains 79 components: one white model, 13 pure-OU timescales, and 65
mixed time/fraction combinations. The family prior masses are 0.25/0.25/0.5;
timescales span 0.1–10,000 exposures, with trapezoidal log-grid weights, and mixed
fractions are 0.1/0.3/0.5/0.7/0.9. These are declared research assumptions, not
empirically calibrated astrophysical priors. Block scores retain within-block
covariance but are not the whole-sector joint likelihood.

The 180 saved predictions and 4,740 component fits have been numerically replayed,
including parameters/weights, predictive means/variances, CDF values and block
scores. The public supplement is **evidence inspection only**; selected-vector
verification does not provide a complete raw-input public vetting capsule.
The maximum difference in the checked replay quantities is zero.

The [anonymous aggregate record](../reviews/independent-sector-noise-review-2026-10-12-v1.json)
retains the scope, outcomes and originating batch hash. Existing dossiers and
negative evidence are preserved; all 172 assessments remain unclassified.

Source/PRF/astrometric calibration, credible-host coverage, timing, physical/binary
alternatives, full-search reliability and a documented scientific review remain
required for stronger classifications.
