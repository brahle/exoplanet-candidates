# Spatial-mode temporal covariance review — 12 October 2026

The [previous pilot](temporal-source-review-2026-10-11.md) gave all spatial modes
one common time correlation. This follow-up uses a separate out-of-transit-trained
OU correlation per spatial covariance eigenmode, retaining the same source and
background profiles, event selection, exposure waveform and spatial shrinkage.
The original common-model coefficients and uncertainties were replayed before
comparison. This is a conditional method experiment; source attribution remains
unresolved and **no scientific assessment is promoted**.

All 24 original records were attempted, with no execution failures. There are 80
conditional window fits, including 21 at the actual ephemerides. The three records
without sufficient usable events remain unavailable. All 16 original unavailable
window rows are retained.

| Cohort | Fields | Unique selected field/source/phase contrasts | Common-model nominal misses | Mode-model nominal misses |
|---|---:|---:|---:|---:|
| Development | 2 | 8 | 0 | 0 |
| Additional fields | 22 | 107 | 3 | 2 |

One original mismatch falls inside the new nominal interval; two persist, and no
new mismatches appear in these selected contrasts. Counts deduplicate the original
three injection amplitude levels. These are comparisons of background-template
bias relative to zero or an imposed loss alone, not independently calibrated
coverage or false-positive rates. Models and contrasts share photons.

Across the 80 window fits, 35 individual mode-correlation estimates exceed the
unchanged upper bound of 0.95 and are clipped. These are mode estimates, not 35
different fields. The mode treatment can retain correlated variability that a
pooled estimate dilutes. The remaining mismatches and bound clipping show that it
does not resolve the source-model adequacy problem.

The spatial-mode OU independence assumption, polynomial background means, fixed
PRF and positions, bounded host basis and empirical covariance remain conditional.
Cross-mode temporal dependence, nonstationarity and hyperparameter uncertainty
are omitted. Missing credible hosts, timing consistency, physical alternatives
and search reliability remain open. A reduced score does not identify a dip host
or demonstrate a planet.

All 80 saved selected-window fits have been numerically replayed with zero
differences in the checked coefficients and standard errors. This verification
is narrower than the whole reduction and vetting process. The public supplement
is **evidence inspection only**; it does not provide a new public numerical capsule.

The [anonymous aggregate record](../reviews/mode-temporal-source-review-2026-10-12-v1.json)
retains the counts, scope and originating batch hash. Existing dossiers, their
negative evidence and classifications remain unchanged.
