# Background-search fitting repair — 12 October 2026

The independent background-control campaign remains **held**. Its earlier pilot
showed that tiny detrending roundoff could change legacy trapezoid-fit parameters.
A separate experiment now addresses that numerical failure without changing the
original search grids, data, thresholds, source or acceptance tolerances.

The test retains all 12 saved flux-only interventions from two presampled targets,
including observed and injected fits. Each method fits each input three times.
Depth is solved analytically for a proposed shape, and 27 fixed starts search
within the original bounds. A second version solves bounded convex problems inside
the visited contact regions, retaining rank failures and optimizer diagnostics.

| Check | Depth-projection v1 | Contact-face v2 |
|---|---:|---:|
| Fits executed | 36 | 36 |
| Same-input repetitions deterministic | Yes | Yes |
| Groups stable across recorded flux roundoff, using existing tolerances | 3/4 | 4/4 |
| Objectives lower than best legacy fits | 4/4 | 4/4 |

Version 1's failed group is preserved. Version 2's maximum parameter variation
across recorded flux versions is at roundoff in this limited test. The independently
evaluated legacy-model chi-square improves by about 0.95–2.43 across the four groups.
A lower objective or numerical stability does not establish a planet or correct
physical interpretation.

Independent audits replay every final curve, objective and bounded scalar depth
solution, and check primal feasibility/stationarity for the saved convex contact
certificates. These certificates cover visited full-rank contact regions; they do
not establish a global nonsmooth optimum or validate the white, unintegrated model.
The [aggregate receipt](../reviews/contact-faces-review-2026-10-12-v1.json) preserves
the two versions, comparisons and audit scope.

**The repair is not adopted, and the full 8,192-target campaign has not launched.**
The next step is integration with the unchanged vetting rules, covariance/diagnostic
outputs and broader presampled pipeline repetitions under an explicitly versioned
recipe. Null-model adequacy, physical/noise validation and candidate reliability
remain separate requirements. The original numerical failures remain in history.
This supplement does not provide a complete public raw-input reproduction capsule.

Separately, the long-running source wave finished all 42 executions. Its source
attribution gate remains unresolved; execution completion is not a scientific pass.
All 172 public dossiers remain unclassified, with no host or planetary promotion.
