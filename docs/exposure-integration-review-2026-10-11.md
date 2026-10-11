# Exposure-integration and point-fit review — 11 October 2026

Supplement version **1.0.0**, following the [earlier conditional-chain review](physical-fit-review-2026-10-11.md).
The historical dossiers and original posterior summaries remain unchanged.

A separate averaging rule addresses the numerical concern from the earlier review:
each exposure is split at circular transit contacts and integrated using
Gauss-Legendre orders16,32,64. The instantaneous quadratic batman kernel is shared;
this is a separate exposure rule, not an independent transit kernel. Uniform
exposure weighting, the original catalogue host, circular orbit, fixed white noise,
no dilution, event arrays, baselines and parameter bounds are retained.

[Machine-readable point results, units, assumptions and numerical comparisons](../reviews/exposure-integration-review-2026-10-11-v1.json).

| Signal | Point-fit density / assumed catalogue prior centre | Largest order32→64 exposure difference across ten reviewed vectors | Assessment |
|---|---:|---:|---|
| [TIC261119502](../candidates/tic-261119502-s01/README.md) | 1.041 | 0.00000333ppm | Unclassified; prior/adverse reports retained |
| [TIC339451799](../candidates/tic-339451799-s01/README.md) | 42.04 | 0.000100ppm | Unclassified; density/shape concern persists |

All four bounded optimizer starts terminated successfully for each signal. The
order32→64 maximum absolute log-objective changes across the reviewed vectors were
about5.1e-9 and4.3e-7, respectively. These are empirical numerical comparisons on
fixed vectors, not a rigorous error bound or a posterior-wide convergence proof.

TIC339451799's selected point fit still requires a density about42times the assumed
catalogue prior centre, with limb-darkening coordinates near their lower bounds.
At that same point, the original seven-sample averaging and contact-panel order32
predictions differ by up to969ppm and11.22log-objective units. Exposure averaging
matters numerically, but replacing it **does not remove the density concern at these
point fits**. The other public signal also has a point optimum near a limb-darkening
boundary; a boundary optimum alone does not determine the physical interpretation.

These are **point fits**, not corrected posterior medians or credible intervals.
No new parameter uncertainties, covariance, absolute planet radius or planet
probability are assigned. Successful optimizer termination does not prove a global
optimum. Host, orbital, noise, photometric and nonplanetary alternatives remain open;
this experiment does not establish a false-positive mechanism or support promotion.

## Reproduce this diagnostic

The [replay package](../reproductions/exposure-integration-2026-10-11/README.md)
contains selected cadence/flux arrays, event metadata, exact model-source copies,
review vectors, flux/residual witnesses and frozen Python dependencies for these
two public signals. It checks file hashes, replays all ten fixed vectors per signal
under every averaging rule, then reruns all four point-fit starts per signal.
The [fresh-environment replay certificate](../reviews/exposure-integration-review-2026-10-11-replay.json)
records zero differences for the saved exposures/residuals and all eight refit
objectives/predictions in that environment.

This calculation is reproducible **from the supplied derived inputs**. Raw-FITS
acquisition, reduction, event selection, posterior sampling, source attribution,
timing consistency, noise calibration, alternatives/FPP and full-search reliability
are outside this package. The complete candidate vetting remains unfinished; the
existing dossier reproduction assessments and scientific classifications are unchanged.
