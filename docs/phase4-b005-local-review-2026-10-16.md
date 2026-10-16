# Phase 4 b005: evidence review and public disclosure

Prepared 16 October 2026. Owner authorized public disclosure on 16 October 2026. These are provisional
evidence records; actual Git disclosure and immutable release times are recorded
separately in the batch publication receipt. No DOI has been assigned. All 80 registered signals completed the installed
verifier stages on their first attempt, with zero execution failures. All remain
scientifically unclassified. The 49 selected dossiers have 148 diagnostic PNGs
retaining 2,048 signed numerical event profiles.

| Outcome | Signals |
|---|---:|
| Selected provisional evidence dossiers | 49 |
| Prior report or catalogue-match hypothesis | 22 |
| Insufficient usable multisector evidence | 6 |
| No adopted diagnostic ephemeris outside the hypothesis route | 3 |
| Total | 80 |

The [complete ledger](../batches/phase4-scaled-b005/outcomes.json) conserves every
signal. There are 75 adopted conditional diagnostic ephemerides and five unadopted
fits overall; two of those unadopted fits are already in the 22 catalogue hypotheses.
A ledger-only outcome is not an adjudicated false positive. Six signals have two
recorded primary sectors but usable fitted events in only one; the dossier rule
requires usable events in at least two sectors. They remain in the ledger.
The combined b004/b005 publication contains 368 dossiers. Scientific evidence in
the 319 earlier dossiers is preserved; b004 is disclosed alongside b005. The previous
246 public dossier files and disclosure histories remain unchanged.

## Catalogue and host context

A release-time configured-MCP recheck on 16 October 2026 conserved every query and
status. All 49 selected dossier results remain unchanged. Two ledger-only neighbour
matches have updated external catalogue labels or heuristic scores; match identities,
periods and outcome routes are unchanged. These external labels do not adjudicate
the physical source. Updated coverage and exact responses are appended in the
[comparison receipt](../batches/phase4-scaled-b005/release-preflight.json) and
[new snapshot](../batches/phase4-scaled-b005/release-catalogue-checks.jsonl);
original assessment responses are preserved.


Fresh configured Exoplanet MCP checks used adopted diagnostic periods, or explicitly
unadopted discovery seeds where refinement failed, and a 120 arcsec cone. Results are
58 nonmatches, five nearby planet/TOI matches and 17 variable-star hypotheses, with
zero errors and no category changes from the seed checks. Queries compare coordinates,
periods and harmonics; epoch and depth comparisons were not performed. A nonmatch
is not exhaustive novelty, and a neighbour match does not identify the source of a dip.

The dated coverage includes NASA confirmed planets/TOIs, ExoFOP CTOIs, eumemic,
earlier public dossiers, the TESS eclipsing-binary catalogue (Prša et al. 2022), Gaia
DR3 eclipsing binaries and periodic VSX entries. Recent preprints and unregistered
Zenodo dossiers remain explicitly unindexed. See the [saved coverage receipt](../batches/phase4-scaled-b005/catalogue-snapshots.json).

All 80 aperture targets have a qualifying Gaia DR3 association through TIC's DR2 ID
and the official DR2 neighbourhood, with separation and magnitude checks retained.
The 80 aperture associations have distinct DR3 IDs, with no exact DR3-ID overlap
among the 319 earlier dossiers. This does not exclude neighbouring-source contamination.
All 49 selected dossiers include catalogue Teff, stellar radius/mass, TESS magnitude
and distance, with reported uncertainties and original response provenance. Host
and dilution remain unresolved; these are aperture-star values, not physical-host
posteriors or derived planet-radius measurements.

All 49 retain positive conditional duration errors from their original sealed shape
covariance. These are not bootstrap or noise-calibrated intervals. Rp/R-star, impact
parameter and a/R-star were not physically fitted here.

## Warnings and review concerns

Of 49 selected dossiers, **23 have automated descriptive warnings** and 26
have none in the current subset. Counts overlap: 13 scanned-secondary contrasts,
6 odd/even tensions, 5 weak qualified-sector dips and 1 period-cluster case.
Absence of a flag in this subset does not mean every scientific test is available or passed.
Nominal contrast errors are conditional and are not corrected for the diagnostic
scan, selection effects or all correlated noise. No planet probability is assigned.

Specific concerns retained in attributed exact-assessment-bound reviews:

- [TIC 118011778](../candidates/tic-118011778-s01/README.md): alternative-profile odd/even
  contrasts reach about 11.67 nominal conditional error units, with a scanned dip
  about 7.78. Binary, blend and period-alias explanations need particular attention.
- [TIC 263952924](../candidates/tic-263952924-s01/README.md): the strongest scanned dip is
  at phase 0.3 with nominal depth/error about 13.80 and substantial sector scatter.
  It is not automatically a secondary eclipse; variability and baseline effects
  remain alternatives alongside binaries and blends.
- [TIC 319324982](../candidates/tic-319324982-s01/README.md): minimum leave-sector
  conditional depth/error is about 2.36, compared with aggregate 8.09. Positive
  remaining depth does not establish strong independent-sector support.
- [TIC 34156876](../candidates/tic-34156876-s01/README.md): the alternative-profile parity
  contrast is unavailable at the 42.96-day hypothesis. The robustness module has a
  different parity statistic; absence of one diagnostic is not a comprehensive pass.
- [TIC 160191676](../candidates/tic-160191676-s01/README.md): the 12.47-day signal retains
  the existing period-cluster warning and needs an instrumental/systematics assessment.

Visual inspection additionally records a large downward flux/baseline excursion
near the end of S12 for [TIC 263194808](../candidates/tic-263194808-s01/README.md),
and positive shoulders around the dip of TIC 118011778. These are attributed
visual concerns, with no new automated flag or scientific classification.

All 80 have one attributed automated Codex numerical-summary review, bound to the
exact sealed assessment. It is not independent scientific validation or consensus.
Source attribution, timing/noise coverage, physical alternatives/dilution, astrophysical
false-positive probabilities, search reliability and scientific classification review
remain open. Additional visual observations, if any, are retained in the batch's
[visual review](../batches/phase4-scaled-b005/visual-review.json).

## Survey-wide false-alarm context

Fresh-host inverted nulls left 2/1,500 survivors (0.133%), with a 0.485% upper endpoint
of the two-sided 95% Wilson interval. Scrambled controls left 0/1,500, upper 0.255%.
The sealed b005 snapshot has 298 distinct initial survivor stars / 82,044 searched
stars, or 0.3632%.

If transformed controls represent the survey background, the rate ratio is about
**36.7%**: initial survivors could be noise or stellar-variability false alarms at
that rate **before eclipsing binaries**. The null upper endpoint exceeds the real
survivor rate, so the comparison cannot rule out **most or all** initial survivors
being false alarms. This is neither an individual FAP/FPP nor a measured contamination
fraction for these 49 later-selected dossiers. The live search, completion, vet and
retention frontiers are asynchronous; dated counters do not establish final population
completeness. [Counts, intervals, hashes and calculation](phase4-b005-false-alarm-estimate-2026-10-16.json).

## Diagnostic figures and reproduction

All 49 original-grid reconstructions use the recorded launch source 917b726 and native
kernel, full period grid, original detrending/binning and sealed inputs. Raw realization
and final binned-search hashes match for every signal; recorded scalar outputs agree
within rtol 1e-6/atol 1e-8. All intermediate prepared-array hashes also match. Original
spectrum bytes were never saved, so plots say **reconstructed BLS search**.

All 49 overview images were inspected on 4 contact sheets;
8 representative overviews and 3 event pages were inspected individually.
Every event-page count and plotting-vector hash is checked programmatically. This
is not a claim that all 148 PNGs received individual visual inspection.
Discovery searches and timing-qualified folds can use different product/time masks.
Figures retain signed event profiles, failed/unusable event context and missing bins.
Display-bin errors are uncalibrated white standard errors.

Schema/hash/saved-vector checks are **evidence inspection**, not a public raw-input
numerical rerun or a scientific-validity certificate. The 319 earlier scientific dossiers
are preserved; only b004 publication metadata changes alongside this release. The
previous 246 public dossier files and histories remain unchanged. See the [batch publication
receipt](../batches/phase4-scaled-b005/publication-receipt.json) for actual public times. No DOI
or production database update is claimed.
