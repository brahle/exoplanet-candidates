# Observed-star position review — 12 October 2026

A separate diagnostic applied to **24 source records** now measures real stellar
position/morphology discrepancies in separate early and late out-of-transit images.
It does not qualify transit-host attribution or change any dossier assessment.

| Outcome | Count |
|---|---:|
| Selected bright stars | 144 |
| Disjoint early/late coadds | 48 |
| Position-fit attempts | 288 |
| Usable conditional diagnostics | 264 |
| Position-bound failures | 23 |
| Rank-limited fits | 1 |
| Fields with complete early controls | 17 |
| Fields with complete late controls | 19 |

The median catalogue-relative offset among usable fits is **0.0846 pixels**.
For the 131 stars with usable fits in both halves, the median change between halves
is **0.00685 pixels**. These dependent, selected diagnostics suggest persistent
morphology/model discrepancies alongside comparatively stable positions over a
sector. They do not isolate pointing error, certify absolute accuracy, or establish
the dip host. Failed fits remain in the evidence.

The first raw sector and six G-bright controls were fixed before inspecting fit
outcomes. A bounded bright-star nuisance model omits fainter and uncatalogued
sources. Coadd weights use native pixel errors under an independence assumption;
correlated noise, saturation, edges, PRF errors and unresolved blends remain open.
The held star is released while common registration is fitted to the other stars.
No fitted early registration or fit-selected blur is transferred to late images.

Field grouping checks all in-stamp catalogue IDs and overlapping detector stamps.
Late field maxima are compared with other fields' early maxima. Only 16–17 training
groups are usable per comparison, giving a rank resolution of roughly 5.6–5.9%.
Exchangeability and shared detector systematics are unqualified. These are
**descriptive ranks**, not calibrated tail probabilities or host exclusions.

An independent scalar `math.fsum` audit reproduces all 48 native-pixel coadds and
independently checks the graph/rank calculations. This audit does not replay the
nonlinear position fits or certify the clock. An earlier vector replay is retained;
this host's `longdouble` equals float64, so it provided no extra precision check.

The [aggregate receipt](../reviews/observed-position-review-2026-10-12-v1.json)
records the numerical results and limits. Full witnesses are retained with the
research task; this public supplement is not a complete public numerical capsule.
All 172 public dossiers remain unclassified. Existing warnings and prior reports
are unchanged; no uncertainty prior, source pass or planetary promotion is adopted.
