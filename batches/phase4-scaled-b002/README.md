# Phase 4 provisional batch b002

Provisional evidence-inspection records; all scientific assessments remain unclassified.
Actual disclosure and immutable release metadata are recorded in [publication-receipt.json](publication-receipt.json).

[Immutable b002 v0.1.0 evidence release (4 selected dossiers)](https://github.com/brahle/exoplanet-candidates/releases/tag/phase4-scaled-b002-v0.1.0).

All 9 registered signals are conserved in [outcomes.json](outcomes.json).
A match hypothesis does not resolve the physical host. A ledger-only row is not an adjudicated rejection.

[Release-time catalogue recheck](release-preflight.json) · [Exact MCP responses](release-catalogue-checks.jsonl) · [Reviews](reviews.json) · [Fresh findings](followup-findings.json) · [Stellar context receipt](stellar-enrichment.json) · [Whole-cohort findings](triage-cohort.json)

| Outcome | Count |
|---|---:|
| insufficient_multisector_evidence | 1 |
| no_adopted_diagnostic_ephemeris | 1 |
| provisional_signal_record | 4 |
| prior_report_or_match_hypothesis | 3 |

## Survey-wide false-alarm context

The fresh-host gate-2 inverted-null test left **2/1,500 survivors (0.133%, about
0.13%)**, with a **0.485% upper endpoint of the two-sided 95% Wilson interval**.
The real survey through sealed b003 left **111/27,653 (0.401%, about 0.40%)**.
If the null controls represent the real survey background, their rate ratio is
about **one third**: that fraction of initial survivors could be noise or
stellar-variability false alarms **before counting eclipsing binaries**. Because
the null upper endpoint exceeds the real survivor rate, this comparison cannot
rule out **most or all** initial survivors being false alarms.

This is a conditional survey-level comparison, not an individual signal's
false-alarm/astrophysical false-positive probability or a measured contamination
fraction for the 60 later-selected dossiers. Whole-search reliability remains
open. The scrambled controls had 0/1,500 survivors (Wilson upper endpoint 0.255%).
[Full interpretation and dated source calculation](../../docs/phase4-local-review-2026-10-14.md#survey-wide-false-alarm-estimate).

## Signals

Periods below are adopted conditional diagnostic values, or the unadopted discovery seed where the fit failed. All assessments remain unclassified.

| Signal | Period (d) | Recorded outcome | Diagnostic warnings |
|---|---:|---|---|
| tic-216660171-s01 | 2.07942461 | insufficient_multisector_evidence | scanned_secondary_uncorrected |
| tic-234525214-s01 | 53.97028789 | no_adopted_diagnostic_ephemeris | no_adopted_ephemeris |
| [tic-262093857-s01](../../candidates/tic-262093857-s01/README.md) | 29.50374296 | provisional_signal_record | scanned_secondary_uncorrected |
| [tic-272585011-s01](../../candidates/tic-272585011-s01/README.md) | 4.98292457 | provisional_signal_record | odd_even_conditional_tension |
| [tic-288765766-s01](../../candidates/tic-288765766-s01/README.md) | 2.41156008 | provisional_signal_record | scanned_secondary_uncorrected |
| tic-30141842-s01 | 0.93901895 | prior_report_or_match_hypothesis | catalogue_match_hypothesis, weak_qualified_sector_dip |
| [tic-311254233-s01](../../candidates/tic-311254233-s01/README.md) | 3.36108530 | provisional_signal_record | none in this subset |
| tic-340622211-s01 | 1.25948672 | prior_report_or_match_hypothesis | catalogue_match_hypothesis, scanned_secondary_uncorrected |
| tic-406175161-s01 | 1.24105037 | prior_report_or_match_hypothesis | catalogue_match_hypothesis, scanned_secondary_uncorrected |

Conditional/scanned contrasts are descriptive and uncorrected for selection and correlated noise. No warning in this subset does not establish a planet or complete vetting.

[Shared interpretation and remaining requirements](../../docs/phase4-local-review-2026-10-14.md).
