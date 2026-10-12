# Early-profile transfer review — 12 October 2026

A paired test compared archive profiles, positions learned from early data, and
usable learned cores with archive fallbacks on late data from the same sector.
It retains **all 24 source records**: 23 numerical comparisons and one execution
failure caused by an empty original source-hypothesis list. No list was invented
and completed records were not rerun. The batch remains marked partially failed.

| Outcome | Count |
|---|---:|
| Source templates tested | 184 |
| Usable conditional learned cores | 9 |
| Unusable learned cores, retained as explicit fallbacks | 175 |
| Late scene fits | 69 |
| Available actual/shifted joint contrasts | 228 |
| Missing-window contrast outcomes | 48 |
| Fields supporting an actual late transit contrast | 20 |

Failures mostly involve weak deblending constraints, crowding and negative residual
mass; those overlapping reasons do not identify an astrophysical false positive.
Learning each source's shape remains difficult under this bounded scene model.

Early-position corrections reduce late-image weighted RMS in 21 of 23 comparisons,
with a median reduction of 1.84%. Learned-core hybrids improve 22 of 23, with a
median reduction of 2.65%. Profiles stay fixed in late data, while amplitudes and
sky are refitted. These are selected, conditional shape comparisons, not frozen
image forecasts or empirical host-confidence calibration.

For [TIC 21694454](../candidates/tic-21694454-s01/README.md), the target's signed
in-stamp contribution in the actual late-window joint fit changes substantially:

| Profile model | Target contribution (e−/s) | Conditional error (e−/s) |
|---|---:|---:|
| Archive with early common registration | 307.14 | 21.16 |
| Early learned positions | 17.08 | 20.25 |
| Learned-core hybrid | 17.08 | 20.25 |

The target's learned core fails its filters, so the hybrid retains the corrected
archive profile for it. The coefficient change is 13.7 times the archive conditional
error. **That ratio measures model sensitivity; it is not calibrated significance,
a host assignment or a planet rejection.** It demonstrates why fixed-profile errors
alone are inadequate for this record.

Profiles and positions use early out-of-transit photons only. The original source
roster came from prior full-sector analysis, so this is not independent detection
validation. Late-window covariance is estimated from its OOT rows; the white
conditional comparison does not qualify temporal noise. Position, profile, blending,
registration and covariance uncertainty, full source coverage and feasibility remain
open. Shifted phases are diagnostics, not a full-search false-alarm calibration.

An independent constrained-fit optimality and SVD audit checks all 69 late scenes,
228 available contrasts, missing/failed outcomes and all 24 original identities.
Numerical agreement does not establish scientific validity. The
[aggregate receipt](../reviews/profile-transfer-review-2026-10-12-v1.json) records
results and limits. Research witnesses are retained separately; the public note
is not a complete raw-input reproduction capsule.

All 172 dossiers remain unclassified. Prior warnings and catalogue assessments are
unchanged; no host exclusion, planetary promotion or adopted uncertainty model
follows from this comparison.
