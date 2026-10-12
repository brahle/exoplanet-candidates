# Held-out source-noise review — 12 October 2026

This follows the [spatial-mode covariance review](mode-temporal-source-review-2026-10-12.md).
It tests prediction of unseen out-of-transit data, rather than selecting a noise
model because it makes a known source-interval mismatch disappear. **Source
attribution remains unresolved; no scientific assessment is promoted.**

All 24 records were attempted, with no execution failures. For each saved window,
hold out alternating blocks spanning its full nominal transit duration, with a
one-cadence buffer on either side. Learn the spatial basis, select its three largest
variance modes and fit noise/mean parameters using training rows alone. Compare
white noise, the old clipped-lag OU recipe, and an irregular-time OU timescale fitted
by restricted likelihood on a declared grid with local refinements.

Seventy-four windows support this test, including 19 at the actual ephemerides.
Six additional windows have insufficient data for the declared holdout. The original
16 unavailable rows remain retained. Shorter blocks cannot substitute for missing
full-duration tests.

| Cohort | Fields | Paired mode comparisons | Held-out point/mode evaluations per model | White nominal misses | Clipped OU misses | Fitted OU misses |
|---|---:|---:|---:|---:|---:|---:|
| Development | 2 | 18 | 984 | 26 | 33 | 27 |
| Additional fields | 22 | 204 | 34,230 | 1,012 | 892 | 766 |

These are marginal nominal 99% interval misses in conditional Student-t predictions.
The predictions include linear-mean and scale uncertainty, but condition on the
spatial basis and timescale. Modes, phases and points share correlated data. These
counts are descriptive diagnostics, not independent coverage bounds, false-alarm
rates or planet probabilities.

The fitted OU model has a higher held-out joint predictive score than clipped OU
in 104 of 204 additional-field comparisons and nine of 18 development comparisons.
The median score difference is about +0.249 and +0.052 respectively. Improvements
are not uniform. Seventy-two of the 222 fitted timescales reach the declared upper
bound of 10,000 exposures, leaving many timescales poorly constrained. Increasing
that bound until selected cases pass would not establish model adequacy.

All 666 saved conditional predictions have been numerically replayed, including
training means/scales, predicted means, scale diagonals, residuals and joint scores,
with zero difference in the checked quantities. This is selected-window verification;
the public supplement is **evidence inspection only**, with no new complete public
numerical vetting capsule.

Cross-mode dependence, timescale/basis uncertainty, nonstationarity and inadequate
background means remain possible limitations. This check covers the largest three
variance modes within existing sectors; it is not independent field/sector
astrophysical validation or all-pixel/source calibration. Timing, credible hosts,
physical alternatives and search reliability remain open.

The [anonymous aggregate record](../reviews/heldout-source-review-2026-10-12-v1.json)
retains the scope, counts and originating batch hash. Existing dossiers and their
negative evidence are preserved. All 172 scientific assessments remain unclassified.
