# Phase 4 b006: evidence review and public disclosure

Prepared 2026-10-16. Owner authorized provisional evidence disclosure on 16 October 2026. Actual first Git disclosure and immutable release times are recorded separately in the batch publication receipt. No DOI has been assigned.

All 109 registered signals reached a terminal verifier outcome; all remain scientifically unclassified. 105 have an adopted conditional diagnostic ephemeris; 4 retain explicitly unadopted discovery seeds. A ledger-only outcome is not an adjudicated false positive.

| Outcome | Signals |
|---|---:|
| provisional signal record | 77 |
| prior report or match hypothesis | 26 |
| no adopted diagnostic ephemeris | 3 |
| insufficient multisector evidence | 3 |
| Total | 109 |

The [complete ledger](../batches/phase4-scaled-b006/outcomes.json) conserves every signal. The catalogue now has 445 dossiers, preserving the earlier 368 public dossier files and histories unchanged.

## Catalogue and stellar context

Release-time configured Exoplanet MCP checks on 16 October 2026 exactly preserved all 109 query arguments and result objects, including all 77 selected dossiers. The [comparison receipt](../batches/phase4-scaled-b006/release-preflight.json) and [new dated responses](../batches/phase4-scaled-b006/release-catalogue-checks.jsonl) supplement the original assessment without replacing it.


Fresh configured Exoplanet MCP checks used adopted diagnostic periods, or explicit unadopted seeds, and 120 arcsec. Results: 83 no match in checked sources, 20 variable star match, 6 near matches found. Queries compare coordinates, periods and harmonics; epoch and depth comparisons were not performed. Nonmatches are not exhaustive novelty; nearby matches do not identify the physical source. Exact original catalogue responses remain in each selected dossier's `evidence/catalogue-check.json`.

The dated coverage includes NASA confirmed planets/TOIs, ExoFOP CTOIs, eumemic, previous public dossiers, TESS EBs, Gaia DR3 EBs and periodic VSX entries. Recent preprints and unregistered Zenodo dossiers remain unindexed. No new missing catalogue source is established by a nonmatch alone.

All 109 aperture targets have qualifying official DR2/DR3 neighbourhood associations, with no exact DR3-ID overlap among the previous 368 dossier targets. This does not establish the eclipsed host or exclude nearby contamination. Selected dossier catalogue parameter coverage: distance pc: 77/77, mass Msun: 77/77, radius Rsun: 77/77, teff K: 77/77, tmag: 77/77. Host and dilution remain unresolved; no physical planet radius, Rp/R-star, impact parameter or a/R-star is fitted here.

An additional check against the pinned 11 October 2026 TESS Ten Thousand published EB tables parsed all 10,001 rows with verified hashes and no malformed rows. It used the existing 420-arcsec static-position diagnostic cone, wider than the MCP cone, and period/harmonic matching. No event-train comparison was performed. There are no matches among the 77 selected dossiers. One same-period neighbour (TIC 463186858, 73.76 arcsec, P 3.636975 d) is recorded for ledger-only TIC 463186783, which already had a nearby catalogue hypothesis. The earlier public TIC 463186778 dossier also has the same-period binary about 74.63 arcsec away; its existing files and classification are preserved, with a separate source-attribution and dated-amendment review recorded. This is source context, not physical attribution or a new selection change. See [the dated supplementary check](../batches/phase4-scaled-b006/additional-ffi-eb-screen.json). The original MCP snapshots and reviews remain intact.

77/77 selected dossiers retain available conditional duration errors from the original sealed shape covariance. Missing errors, if any, remain explicit; these are not bootstrap or noise-calibrated intervals.

## Warnings and individual concerns

31 selected dossiers carry descriptive flags; 46 have none in this subset. Overlapping counts: scanned secondary uncorrected: 15, odd even conditional tension: 12, period cluster 13d: 4, weak qualified sector dip: 4. Absence of a flag does not mean every scientific test is available or passed. Nominal contrast errors are conditional and uncorrected for diagnostic scans, selection and all correlated noise.

The following whole-batch concerns include ledger-only rows as well as selected dossiers.

- **tic-120066309-s01**: Minimum leave-sector conditional depth/error is about 2.26 versus aggregate 10.69; positive leaveout depth alone is weak independent-sector support.
- **tic-147275913-s01**: Alternative-profile odd/even contrasts reach about 7.12 nominal conditional error units and the strongest scanned dip about 3.70. Binary/blend and period-alias alternatives need attention; these are not calibrated significances.
- **tic-176866287-s01**: Alternative-profile parity contrast reaches about 8.58 nominal units, alongside a scanned dip about 4.15. Preserve the binary/blend warning and unresolved source; no definitive physical classification follows.
- **tic-220015202-s01**: The linear-profile dip is about 14,390 ppm with conditional aggregate depth/error about314, and alternative parity contrast reaches about7.95 nominal units. Strong detection is not planetary validation; binary/blend/dilution and physical-shape explanations remain open.
- **tic-281815121-s01**: At P about56.04d only two primary events are usable. Linear/quadratic aggregate depth/error changes from about5.28 to7.38; minimum leave-sector support is2.28. Alternative-profile parity is unavailable, while the distinct robustness parity contrast is about-4.11 nominal units. Missing parity is not a pass; sparse coverage and model sensitivity remain.
- **tic-319802646-s01**: The strongest scanned dip is at phase0.2, about1,301ppm and6.93 nominal conditional error units, with conditional scatter chi2 about101.9. This is a scanned variability/baseline/binary-alternative diagnostic, not an automatically identified secondary eclipse.
- **tic-324130853-s01**: Only three primary events are usable at P about11.16d. Alternative-profile parity is unavailable; the separate robustness parity diagnostic is available. A phase0.5 scanned dip reaches about5.26 nominal units. Preserve missing-support and binary/blend concerns rather than interpreting absence of a parity statistic as a pass.
- **tic-208089714-s01**: Catalogue variable-star hypothesis retained. The phase0.8 scanned dip reaches about26.63 nominal conditional error units; baseline dependence and limited primary-sector support require separate physical-source assessment. This is not an independently adjudicated eclipsing host.
- **tic-446889649-s01**: A phase0.5 scanned dip reaches about11.70 nominal conditional units alongside the existing variable-star match. Preserve the binary/blend alternative without treating the neighbour catalogue match as a located physical source.
- **tic-362710010-s01**: One alternative-profile parity variant reaches about8.25 nominal units while other variants are much smaller. The contrast is model-sensitive and uncalibrated; the existing nearby catalogue hypothesis remains separate from host attribution.
- **tic-412599632-s01**: Minimum leave-sector conditional support is about1.05 compared with aggregate9.75; a positive remainder is weak independent-sector evidence. Existing variable-star hypothesis remains a hypothesis, not an adjudicated source.
- **tic-459843891-s01**: At the long P about46.23d hypothesis, one alternative-profile parity contrast is unavailable and another is about3.02 nominal units. Sparse-event/parity support and correlated noise remain unresolved.

Visual observations:

- **tic-120066309-s01**: The aggregate fold shows a dip, while several individual profiles are noisy or incomplete. The numerical leave-sector concern remains; the overview alone does not establish independent-sector robustness.
- **tic-147275913-s01**: The folded centre is deeper and more rounded than the mean saved trapezoid. The displayed odd/even curves look fairly close; this display does not cancel the retained alternative-profile parity warning.
- **tic-176866287-s01**: Strong sector-35 excursions are retained. Event page 1 shows substantial sector-to-sector depth/noise differences, including deeper sector-89 profiles. Large excursions crowd the overview event labels; the separate event page is readable. Preserve baseline, parity and source concerns.
- **tic-220015202-s01**: The several-percent folded dip is strong, and its centre is deeper than the mean saved profile model. The last event page correctly retains the single final event and its missing right-side coverage. Signal strength does not qualify its physical scale, host or binary/blend alternatives.
- **tic-281815121-s01**: The long-period fold combines only three signed profiles; primary usability is a separate test. Sector 96 has a steep local baseline and an asymmetric broad feature. The odd/even display is based on one versus two profiles. Preserve sparse support and baseline sensitivity.
- **tic-319802646-s01**: Out-of-dip structure and variable individual profiles remain visible around the main dip. Keep the numerical scatter and scanned-dip concerns; these panels do not identify a secondary eclipse or physical host.
- **tic-324130853-s01**: Only four signed profiles enter this plotted fold, with three versus one in the parity display; the usable-primary count is separate. Large depth and sparse support retain physical-alternative and timing concerns.
- **tic-339037794-s01**: Both the folded and odd/even displays show positive shoulders around the central dip, with residual out-of-dip structure. The simple saved mean profile does not explain that structure; baseline/variability and physical-shape alternatives remain open.
- **tic-418382401-s01**: Five signed event profiles support the long-period overview, but individual depths and surrounding structure vary. Preserve sparse-event and timing/physical-source limitations.
- **tic-432744925-s01**: The displayed odd/even depths differ visibly with only four profiles in each group. The near-13-day period and retained parity warning remain descriptive concerns, without a calibrated false-positive conclusion.
- **tic-53689599-s01**: The fold and nine signed profiles show a several-percent dip. Its centre is deeper than the mean saved profile model, and some events have missing wings. Binary/blend, physical scale and host attribution require further work.
- **tic-293817656-s01**: The first and final event pages preserve all 189 profiles in chronological order, including missing bins and individually weak dips. The page headings, last-page range and sector/cycle labels are readable; seeing an aggregate fold does not make every individual event significant.

Reviews are attributed automated numerical-summary/visual inspections bound to exact assessment and artifact hashes. They are not independent scientific validation or reviewer consensus. No selection rule or stronger scientific disposition was changed.

## Survey-wide false-alarm context

At this dated frontier, 407/109,776 searched stars produced initial survivors (0.3708%). Inverted controls produced 2/1,500 (0.133%; two-sided 95% Wilson upper endpoint 0.485%). If the controls represent the survey background, the rate ratio is **36.0% before eclipsing binaries**. Its uncertainty cannot rule out most or all initial survivors being false alarms. This is not an individual FAP/FPP or a measured contamination fraction among these 77 later-selected dossiers. Live frontiers are asynchronous; this is not a final population rate.

[Source counts, intervals, hashes and calculation](phase4-b006-false-alarm-estimate-2026-10-16.json).

## Diagnostic figures and reproduction

All 77 full-grid reconstructions use recorded launch source 917b726, native kernel, original preprocessing/grid and sealed inputs. Required raw and final search hashes and recorded scalar tolerances match. Intermediate pre-binning hash mismatches: 0; these are retained separately. Original power vectors were never saved, so every BLS panel is labelled reconstructed BLS search.

213 diagnostic PNGs retain 2,895 signed numerical event profiles. Failed and unusable event counts remain in the plotting context and original diagnostics. Discovery and timing-qualified folds can use different product/time masks. Display-bin errors are uncalibrated white standard errors.

All 77 overviews were inspected on 5 contact sheets; 11 overviews and 4 event pages were inspected individually. Every event count and plotting-vector hash was checked programmatically; not every PNG was individually viewed.

Schema, artifact and saved-vector checks are evidence inspection, not a fresh numerical rerun from public raw inputs or a scientific-validity certificate. This owner-authorized evidence release leaves stronger scientific classification as a separate decision. See the [publication receipt](../batches/phase4-scaled-b006/publication-receipt.json) for actual public times.

## Immutable evidence release

[Release](https://github.com/brahle/exoplanet-candidates/releases/tag/phase4-scaled-b006-v0.1.0) · [Publication receipt](../batches/phase4-scaled-b006/publication-receipt.json) · [Anonymous inspection certificate](../batches/phase4-scaled-b006/public-evidence-certificate.json) · [Locked manifest](../batches/phase4-scaled-b006/release-manifest.json).

First Git disclosure: 2026-10-16T18:10:20Z. Immutable release publication: 2026-10-16T18:16:08Z. These are separate server-observed UTC timestamps. Locked dossier versions are 0.2.2; current 0.2.3 adds publication receipts without changing scientific evidence.

The versioned batch package contains 77 selected dossiers and three explicitly declared older validation-fixture dossiers (80 packaged records), from a 445-dossier source catalogue. Its full 109-row ledger and exact reviews retain all outcomes. The anonymous download passed frozen offline dependencies, catalogue inspection and all 65 tests in a fresh environment. This certifies evidence inspection only. No physical-source, timing or planetary validation, raw-input numerical rerun or DOI is claimed.
