# Phase 4: local owner review

Prepared 2026-10-14. This is local staging, with no release, DOI or first-publication
claim. All 111 registered survivors in three sealed batches have completed the installed
verifier stages and received an assessment-bound Codex numerical-summary review.
No signal has been promoted to a planet candidate or confirmed planet.

| Batch | Registered signals | Draft dossiers | Prior report or match hypothesis | No adopted ephemeris | Insufficient multisector evidence |
|---|---:|---:|---:|---:|---:|
| [b001](../batches/phase4-scaled-b001/README.md) | 28 | 16 | 9 | 3 | 0 |
| [b002](../batches/phase4-scaled-b002/README.md) | 9 | 4 | 3 | 1 | 1 |
| [b003](../batches/phase4-scaled-b003/README.md) | 74 | 40 | 25 | 4 | 5 |
| Total | 111 | 60 | 37 | 8 | 6 |

These routes account for every input. A ledger-only outcome is retained with its
review and evidence references; it is not an adjudicated false positive. The 37
catalogue hypotheses do not establish the source of a dip or close its analysis.
101 signals have an adopted conditional diagnostic ephemeris; the ten others retain
their failed or unadopted fit evidence. Routing also considers catalogue matches,
so those ten do not all appear in the no-adopted-ephemeris column.

## Survey-wide false-alarm estimate

Added 15 October 2026, using the saved gate-2 results and the sealed b003 survey
snapshot. Rates count stars with any automatic-triage survivor; vetting errors
count as survivors in the null test.

| Sample | Survivor stars / searched stars | Survivor rate | Upper endpoint of two-sided 95% Wilson interval |
|---|---:|---:|---:|
| Inverted null controls | 2 / 1,500 | 0.133% | 0.485% |
| Scrambled null controls | 0 / 1,500 | 0% | 0.255% |
| Real survey through b003 | 111 / 27,653 | 0.401% (about 0.40%) | Not used for this comparison |

Using the higher observed null-control rate, `(2/1500) / (111/27653) = 0.332`:
**roughly one third of the initial survey survivors could be false alarms from
noise or stellar variability, before counting eclipsing binaries**, if the null
controls represent the real survey background. The null rate's 0.485% upper
endpoint exceeds the real survey's approximately 0.40% survivor rate, so this
comparison **cannot rule out most or all initial survivors being false alarms**.

This is a conditional survey-level contamination estimate. The transformed
controls may not reproduce every real false-alarm mechanism. It is not a
calibrated per-signal false-alarm probability, an astrophysical false-positive
probability, or a measured contamination fraction for the 60 dossiers selected
after additional vetting. Binary/blend contamination needs separate assessment;
whole-search reliability remains open. The real-run denominator excludes three
no-result stars from 27,656 completed targets and is a dated snapshot, not a live
rate. [Source counts, intervals, hashes and calculation](phase4-false-alarm-estimate-2026-10-15.json).

## Fresh catalogue and stellar context

The configured Exoplanet MCP was queried at the fitted period where an adopted
diagnostic fit exists, otherwise at the explicitly unadopted discovery period,
using a 120-arcsecond radius. The batch tool matches coordinates, periods and
harmonics; it does not compare epochs or depths. Its dated responses found 74 with no match in checked
sources, five nearby planet/TOI hypotheses and 32 variable-star hypotheses.
Unindexed papers and other gaps remain in the snapshots. These checks establish
neither exhaustive novelty nor a physical host.

All 111 TIC aperture targets have a unique qualifying Gaia DR3 association via the
official DR2 neighbourhood, using the declared angular-distance and magnitude
limits. Each of the 60 draft dossiers includes TIC 8.2 stellar values, their catalogue
uncertainties, raw response provenance, and an unresolved host/dilution block.
All 60 retain a conditional local-covariance duration error from their original
sealed fit; this is not bootstrap, noise-calibrated or full physical-fit uncertainty.
Rp/R-star, impact parameter and a/R-star have not been physically fitted here.

## Warnings and work remaining

25 of the 60 drafts carry at least one descriptive warning: 15 have a scanned-secondary
contrast, nine have odd/even tension in at least one declared baseline/shape variant,
three have weak qualified-sector dip support, and two lie in the broad 13-day period
cluster. Counts overlap. The other 35 have no warning in this subset, which does not
establish a planetary interpretation. Secondary scans and conditional error units
are not corrected for selection or correlated noise.

Calibrated source attribution, clock/noise coverage, physical alternatives and dilution,
astrophysical false-positive probabilities, whole-search reliability, and scientific
classification review remain open. Existing progress and assessment folders preserve
these separate axes. Automated review authorizes evidence inspection only.

## Diagnostic figures and reproduction

The local diagnostic gallery provides the saved light curve and local baselines,
phase fold, original-grid BLS reconstruction, odd/even profiles, and all retained
individual-event pages. Search reconstruction uses the exact launch source, period
grid and native kernel. Raw realization and final binned BLS input hashes must match,
as must all recorded numerical outputs at declared tolerances. Intermediate
pre-binning hash comparisons are retained separately, including mismatches.
All three stage hashes match for all 60 final reconstructions. An initial Astropy
pilot failed its intermediate hash check and was withheld; the final plots use
the recorded native kernel.
The original spectrum bytes were never saved: these are explicitly reconstructed
spectra, not historical saved periodograms. Discovery QLP clock/product masks can
differ from the timing-qualified fold.

Plots are displays of saved diagnostic vectors and do not supply a new transit fit
or a planet probability. Display-bin errors are uncalibrated white standard errors.
Dossiers remain at evidence-inspection reproduction level; schema/hash checking
is not a clean public-input numerical replay.

The owner reviews this local staging before a deliberate release. Public dates stay
null until an actual public disclosure is recorded.
