# Full diagnostic replay — 12 October 2026

The experimental [contact-face fitting repair](contact-faces-review-2026-10-12.md)
now connects to the complete original light-curve diagnostics, including fit
uncertainties, secondary checks, odd/even contrasts, event consistency, coverage,
phase variability and warning flags. It remains an experimental method.

All 12 saved vetted inputs from the two presampled engineering controls were
replayed three times: **36 complete diagnostic records**. All four trial groups
repeat within the unchanged numerical tolerances. All necessary scalar fields
are finite. The other 18 search trials had no saved vetting output and remain
explicitly unvetted; this experiment does not invent selection passes for them.

The conditional uncertainty calculation uses a four-parameter white-noise
Jacobian and SVD covariance. At piecewise transit contacts it averages limiting
derivatives within a declared machine-roundoff window. Contact counts, active
parameter bounds and rank are retained. An independent scalar-summed information
matrix audit agrees with the covariance, with a maximum difference normalized by
the parameter-error outer product of approximately 1.91 × 10⁻¹³. All errors,
covariance terms, fitted parameters and warning sets repeat in these four groups.

**These are computational uncertainty diagnostics, not qualified confidence
intervals.** Contacts are nonsmooth, one trial group reaches a parameter bound,
and the model still assumes fixed white errors, an unintegrated transit shape and
a unit baseline. No noise, exposure, identifiability or interval-coverage
qualification is claimed. These uncertainties are not inserted into the public
candidate dossiers.

All four groups retain their original warning sets, although many fitted and
downstream measurements change. Thus this experiment shows limited repeatability
of a changed fitting method, not equivalence to the old fit or evidence that the
controls are planets. The earlier instability and unsuccessful first repair are
preserved. The [aggregate receipt](../reviews/trapezoid-interface-review-2026-10-12-v1.json)
records execution and audit scope.

The complete replay is conditional on stored prepared arrays and saved search
rows. It does not rerun native acquisition, detrending or the full period search.
The next test must use a broader presampled native-input queue with independent
process repetitions under a separately versioned experimental recipe. The
8,192-target reliability campaign remains held and the method is not adopted.

All 172 published dossiers remain unclassified. This method supplement changes
no signal disposition, warning evidence, novelty record or disclosure date. It
provides aggregate evidence inspection; no public native-input numerical capsule
or end-to-end reproduction is supplied by this supplement.
