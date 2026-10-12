# Run 6: complete triage ledger and 14 provisional dossiers

The original survey produced 826 vetting passes. This batch retains all of them
in [triage-cohort.json](triage-cohort.json), including known reports, adverse
diagnostics, ambiguous cases and failed tests. Fourteen targets receive new
dossiers after fresh light-curve, timing and astrophysical-alternative checks.
All are unclassified; no planet has been validated or confirmed.

Read the [dated findings](../../docs/run6-followup-2026-10-12.md),
[follow-up summary](followup-summary.json), [per-signal results](followup-findings.json)
and [source receipt](followup-source-receipt.json). The
[14-row disclosure ledger](outcomes.json) records the independent dossier-selection
rule. Disclosure selection is separate from scientific qualification.

## Original triage routes

These mutually exclusive first-match routes reproduce the upstream classifier.
They are legacy diagnostic labels and have not been adjudicated as physical
explanations. Catalogue, pixel, timing and other warnings can overlap.

| Original route | Passes |
|---|---:|
| Off-target diagnostic | 676 |
| Known on-target report | 40 |
| On-target ambiguous | 38 |
| EB-like diagnostic | 24 |
| Neighbour of a known planet/TOI/CTOI | 17 |
| Weak or unavailable global fold | 9 |
| Neighbour of a TESS EB | 5 |
| Pixel test failed | 1 |
| On-target diagnostic | 16 |
| **Total** | **826** |

Two of the 16 have period-matched Gaia EBs nearby and were excluded from the
14-item priority selection. Their association evidence remains in the full
ledger; nearby matches alone do not prove contamination.

## New dossier additions

The seven flagged records and seven without these flags all have incomplete
scientific qualification. Figures and conditional uncertainties are inspection
evidence; public numerical reproduction and physical-host attribution remain open.

| Dossier | Refined period (d) | Primary sectors | Box-window S/N | Diagnostic flags |
|---|---:|---:|---:|---|
| [tic-38593803-s01](../../candidates/tic-38593803-s01/README.md) | 4.70261764 | 4 | 16.10 | odd_even_conditional_tension |
| [tic-79810298-s01](../../candidates/tic-79810298-s01/README.md) | 0.87270875 | 4 | 41.06 | odd_even_conditional_tension |
| [tic-93234652-s01](../../candidates/tic-93234652-s01/README.md) | 4.15415245 | 4 | 7.01 | none in this subset; incomplete |
| [tic-103065229-s01](../../candidates/tic-103065229-s01/README.md) | 3.46680914 | 5 | 13.73 | early_prediction_imprecise |
| [tic-179297560-s01](../../candidates/tic-179297560-s01/README.md) | 4.85524257 | 4 | 21.93 | none in this subset; incomplete |
| [tic-216780294-s01](../../candidates/tic-216780294-s01/README.md) | 3.78911658 | 4 | 7.24 | none in this subset; incomplete |
| [tic-261707476-s01](../../candidates/tic-261707476-s01/README.md) | 14.75344771 | 4 | 10.63 | scanned_secondary_uncorrected |
| [tic-272794454-s01](../../candidates/tic-272794454-s01/README.md) | 4.98649930 | 6 | 12.58 | none in this subset; incomplete |
| [tic-284070379-s01](../../candidates/tic-284070379-s01/README.md) | 3.37354327 | 4 | 10.24 | none in this subset; incomplete |
| [tic-292547242-s01](../../candidates/tic-292547242-s01/README.md) | 7.13929992 | 5 | 11.62 | early_prediction_imprecise, scanned_secondary_uncorrected |
| [tic-303845679-s01](../../candidates/tic-303845679-s01/README.md) | 5.38978042 | 3 | 14.36 | none in this subset; incomplete |
| [tic-358231727-s01](../../candidates/tic-358231727-s01/README.md) | 12.97574537 | 8 | 3.24 | no_saved_pixel_competitor, period_cluster_13d, weak_qualified_sector_dip |
| [tic-390719318-s01](../../candidates/tic-390719318-s01/README.md) | 3.88927641 | 3 | 13.58 | none in this subset; incomplete |
| [tic-425933702-s01](../../candidates/tic-425933702-s01/README.md) | 12.93962926 | 8 | 1.47 | period_cluster_13d, weak_qualified_sector_dip |

## BLS figure update, 13 October 2026

All 14 dossiers now include full reconstructed BLS spectra using the original
discovery recipe and exact inputs. All recorded numerical search results agree
within declared tolerances, and a second reconstruction reproduces the new
period/power vectors exactly. The panels explicitly say **Reconstructed BLS
search**. [Methods and limits](../../docs/diagnostic-figures.md) explain the
backend and timing differences. Prior figure bundles remain linked in each
dossier; scientific measurements, assessments and disclosure dates are unchanged.
