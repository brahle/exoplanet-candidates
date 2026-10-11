# Vetting findings — 11 October 2026

These findings add dated warnings and coverage to all **172 retained dossiers**.
They partially adapt the diagnostics used by [Eumemic](https://github.com/eumemic/exoplanets);
they do not reproduce its complete LEO-Vetter, calibrated source, physical/FPP or
search-reliability assessment. Scientific dispositions remain unclassified.

## Dated initial screen

| Initial result | All 172 | Without the 16 prior-report overlaps |
|---|---:|---:|
| At least one light-curve/catalogue warning | 124 | 116 |
| Available initial diagnostics without these warnings | 40 | 33 |
| Incomplete diagnostics without an existing warning | 8 | 7 |

The 33 are follow-up priorities, not likely planets. Among the 156 without prior
reports, overlapping warning counts are 32 odd/even, 38 phase-half secondary,
27 nearby eclipsing-binary period/alias hypotheses and 34 elevated RUWE.
The nine-phase secondary scan has 79 uncorrected warnings and includes phase 0.5.
Those counts overlap; the nominal error estimates and scan significance remain
uncalibrated. Nearby objects and period harmonics do not establish the dip host.

There are also 16 matching Eumemic aperture reports: 12 labelled likely nearby
false positives, two likely eclipsing binaries and two tier C. These earlier
reports are already recorded in [the external source review](external-reports.md).
They remain adverse evidence attributed to that project rather than adjudicated
false-positive labels from this pipeline.

## Source and physical diagnostics

The frozen source snapshot has **10 completed diagnostic executions out of 24**,
with 14 pending. Eight of those completed signals belong to this public cohort;
two are outside it and are explicitly listed in the export receipt. A separate
crowded-field signal, TIC 313083329, has completed diagnostics, giving nine newly
documented public source checks. Completion is not a calibrated attribution pass.

Notable first-treatment, unblurred source warnings include:

| Signal | Diagnostic offset from target | Interpretation |
|---|---|---|
| [TIC 163031959](../candidates/tic-163031959-s01/README.md) | 4.25–4.34 pixels, S37/S64 | Near tested Gaia 6079384031196151168 / TIC 163042814; strong off-target warning. |
| [TIC 101909456](../candidates/tic-101909456-s01/README.md) | 1.64–1.71 pixels, S9/S36/S63/S90 | Near tested Gaia 5415211315030077184 / TIC 101909418. |
| [TIC 260569590](../candidates/tic-260569590-s01/README.md) | 1.24–1.38 pixels, S9/S10/S63/S90 | S36 is unavailable because it would require prohibited PRF extrapolation. |
| [TIC 313083329](../candidates/tic-313083329-s01/README.md) | 1.02–1.19 pixels, S11/S38/S65 | Nearest tested source varies between sectors. |

These are warnings, not definitive host assignments or planet rejections. All
saved treatment/width fit rows from the imported audits are retained per signal,
including failed/bounded fits. Shared-photon controls and uncalibrated confidence
coverage remain limits. Some source diagnostics use an unresolved clock hypothesis.

Three members of the original 33-signal initial shortlist now carry these
published off-target warning flags: TIC 101909456, TIC 163031959 and TIC 313083329.
The [current follow-up shortlist](../browse/shortlist/README.md) therefore contains
30 signals without published warning flags. Most still await source vetting;
absence of a warning is not a completed test or a planet probability.

The physical pilot attempted four signals × six scenarios. All 24 passed the
saved-output integrity audits; **none passed sampling qualification**. Three of
those signals are in this public cohort, with all 18 scenario outcomes recorded;
the fourth is a separate recovery control. Failed qualification blocks physical
interpretation and does not falsify a planetary explanation.

## Acquisition correction and remaining work

Independent counts found four silently short Gaia DR2/DR3 association tables in
the next source wave. Counted repair preserved the other 38 target records and
the original failed evidence. Repaired row totals are 37,028, 40,847, 17,650 and
17,120. The reusable launcher now requires complete independently counted fields
and complete TIC pages before numerical source fitting. The corrected full-field
audit was still underway when these findings were assembled.

Qualified physical/scenario fits, FPP/NFPP, empirical source calibration,
full-search reliability, timing consistency and documented classification review
remain open. No candidate, likely-planet, validated-planet or confirmed-planet
promotion follows from this update. Public numerical reproduction is incomplete;
this release provides inspection of derived evidence and hashes.

This update is a versioned Git disclosure. Earlier immutable release URLs and
publication metadata are retained in each findings file's `previous_publication`
block; the latest dossier version does not claim those releases contain this new
assessment. Original first-disclosure dates and authors are unchanged.

The [assessment receipt](../assessments/2026-10-11-vetting/receipt.json) identifies
the exact source runs, revisions and output hashes. Per-signal excerpts are linked
from each README and sealed by its evidence manifest. The initial-screen views
stay fixed to that dated census; later warning flags can change the current view.
