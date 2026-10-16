# Phase 4 b004: evidence review and public disclosure

Prepared 15 October 2026. Owner authorized public disclosure on 16 October 2026. These are provisional
evidence records; actual Git disclosure and immutable release times are recorded
separately in the batch publication receipt. No DOI has been assigned. All 107 registered signals completed the installed
verifier stages on their first attempt. All remain scientifically unclassified.
All 73 selected dossiers now include reconstructed search spectra and diagnostic
figures: 230 PNGs retaining 3226 signed numerical event profiles.

| Outcome | Signals |
|---|---:|
| Selected provisional evidence dossiers | 73 |
| Prior report or catalogue-match hypothesis | 25 |
| No adopted diagnostic ephemeris | 8 |
| Insufficient usable multisector evidence | 1 |
| Total | 107 |

The [complete batch ledger](../batches/phase4-scaled-b004/outcomes.json) retains every
signal. There are 95 adopted conditional diagnostic ephemerides and 12 unadopted
fits overall; four of those unadopted fits are already counted in the catalogue
hypothesis route. A ledger-only outcome is not an adjudicated rejection. The b004 staging checkpoint contained 319 dossiers. The combined b004/b005
publication contains 368, preserving the previous 246 public dossiers unchanged.

## Catalogue and host context

A release-time configured-MCP recheck on 16 October 2026 conserved every query and
status. All 73 selected dossier results remain unchanged. Two ledger-only neighbour
matches have updated external catalogue labels or heuristic scores; match identities,
periods and outcome routes are unchanged. These external labels do not adjudicate
the physical source. Updated coverage and exact responses are appended in the
[comparison receipt](../batches/phase4-scaled-b004/release-preflight.json) and
[new snapshot](../batches/phase4-scaled-b004/release-catalogue-checks.jsonl);
original assessment responses are preserved.


The configured Exoplanet MCP was queried at the adopted diagnostic periods, with
explicit unadopted discovery seeds where refinement failed, using 120 arcsec.
It returned 82 nonmatches, five nearby planet/TOI hypotheses and 20 variable-star
hypotheses. No signal changed catalogue category from the initial seed-period check.
These queries compare coordinates, periods and harmonics; epochs and depths were
not compared. A nonmatch does not establish exhaustive novelty; a neighbour match
does not establish the physical source of a dip.

All 107 aperture targets have a qualifying Gaia DR3 association through TIC's DR2
ID and the official DR2 neighbourhood. All 73 selected dossiers retain Teff, radius,
mass and TESS magnitude with catalogue uncertainties and raw-response provenance.
Distance is available for 72; TIC 384467365 retains a missing distance explicitly.
The host and dilution blocks remain unresolved. These are catalogue aperture-star
values, not physical-host or derived planet-radius measurements.

All 73 selected dossiers retain conditional duration errors from their original
sealed shape-covariance fits. These are not bootstrap or noise-calibrated intervals.
Rp/R-star, impact parameter and a/R-star were not physically fitted here.

## Warnings and individual review concerns

Thirty of the 73 selected dossiers carry at least one existing descriptive warning:
19 have a scanned-secondary contrast, eight have odd/even tension, and nine have
weak qualified-sector dip support. Counts overlap. The other 43 have no flag in
this subset; that does not mean every test is available or qualified. Nominal
contrast errors are conditional and are not corrected for the diagnostic scan or
all correlated-noise/selection effects. No planet probability is assigned.

Specific numerical-summary concerns retained in the exact-hash reviews include:

- [TIC 242498653](../candidates/tic-242498653-s01/README.md): the minimum leave-sector
  conditional depth/error is only about 0.17. A positive sign is insufficient to
  establish meaningful independent-sector support, despite the stronger aggregate dip.
  This concern is recorded in its attributed review; no selection threshold was changed.
- [TIC 322086813](../candidates/tic-322086813-s01/README.md) and
  [TIC 161786522](../candidates/tic-161786522-s01/README.md): strong scanned-secondary
  contrasts need binary, blend and instrumental assessment. Their nominal error units
  are not calibrated false-alarm probabilities.
- [TIC 384467365](../candidates/tic-384467365-s01/README.md): odd/even tension is retained,
  together with the unavailable catalogue distance.
- [TIC 144313460](../candidates/tic-144313460-s01/README.md) and
  [TIC 91788879](../candidates/tic-91788879-s01/README.md): odd/even contrast is unavailable.
  An absent parity statistic is not a passed parity test, even when no automated
  warning in the current subset is triggered.

- [TIC 292125277](../candidates/tic-292125277-s01/README.md): visual inspection shows
  pronounced positive shoulders on both sides of the folded dip, also visible in
  odd/even displays and not accounted for by the saved mean profile model. Baseline,
  variability and binary/blend alternatives need investigation. This is an attributed
  [visual observation](../batches/phase4-scaled-b004/visual-review.json), not a new
  automatic flag, calibrated significance or classification.

All 107 have one attributed automated Codex numerical-summary review tied to the
exact sealed assessment hash. This is not independent scientific validation or
reviewer consensus. Calibrated source attribution, timing/noise coverage, physical
alternatives and dilution, astrophysical false-positive probabilities, whole-search
reliability and scientific classification review remain open.

## Survey-wide false-alarm context

The fresh-host inverted-null test left 2/1,500 survivors (0.133%), with a 0.485%
upper endpoint of the two-sided 95% Wilson interval. Scrambled controls left
0/1,500, with upper endpoint 0.255%. The sealed b004 snapshot has 218 distinct
initial survivor stars / 54,494 searched stars, or 0.4000%.

If the transformed controls represent the real survey background, their rate
ratio is approximately **one third**: that fraction of initial survivors could be
noise or stellar-variability false alarms **before eclipsing binaries**. The null
upper endpoint exceeds the observed real survivor rate, so the comparison cannot
rule out **most or all** initial survivors being false alarms. This is neither an
individual FAP/FPP nor a measured contamination fraction for the 73 later-selected
dossiers. The live survey's search, vet and retention frontiers are asynchronous;
these dated counters do not establish final population completeness.

[Exact counts, intervals, hashes and calculation](phase4-b004-false-alarm-estimate-2026-10-15.json).

## Diagnostic figures and reproduction

All 73 full-grid reconstructions use the recorded launch source and native kernel,
original detrending/binning and sealed inputs. All three array-stage hashes match
(raw realization, prepared array and final binned search), and all recorded scalar
outputs agree within the declared rtol 1e-6 / atol 1e-8. Original spectrum bytes were
not saved, so the plots say **reconstructed BLS search**.

All 73 overview images were visually inspected on five contact sheets, with five
representative overviews also inspected at full size. Three representative event
pages, including final pages and missing-bin gaps, were inspected at full size.
Every event-page count and plotting-vector hash is checked programmatically; this
is not a claim that all 230 images received individual visual inspection. No empty
BLS panels were observed. The first rendering launcher failed before package
import because it resolved the virtual-environment executable symlink; that failure
is retained privately, and the corrected launcher completed without science changes.

Discovery and timing-qualified folds can use different clock/product masks. The
figures retain signed event profiles, failed/unusable events and excluded-product
context. Display-bin errors are uncalibrated white standard errors. Schema, hash
and saved-vector inspection is **evidence inspection**, not a fresh numerical
rerun from public inputs or a scientific validity certificate.

The previous 246 public dossier files and their disclosure/release histories are
unchanged. See the [batch publication receipt](../batches/phase4-scaled-b004/publication-receipt.json)
for observed Git disclosure and actual release times. Scientific assessments remain
unclassified; evidence inspection does not qualify these as planets.

## Publication receipt

First Git disclosure was observed at **2026-10-16 09:31:13 UTC**; the immutable
release was published at **2026-10-16T09:39:16Z**. The [public inspection
certificate](../batches/phase4-scaled-b004/public-evidence-certificate.json) verifies
anonymous downloads, hashes, all 368 dossiers and fresh frozen-environment tests.
These are evidence-integrity checks; scientific classifications remain unchanged.
