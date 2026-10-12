# Source-profile resampling review — 12 October 2026

The pipeline now carries variation in learned positions and source profiles into
late-window transit-contribution fits. Native early out-of-transit pixel images
are resampled together in nonwrapping blocks within observing segments. Each draw
refits shared registration and released source positions, then eligible cores.
Originally failed positions and unqualified cores cannot be rescued by a favorable
resample. Archive and learned-profile families remain separate.

| Outcome | Count |
|---|---:|
| Original records retained | 24 |
| Fields with resampling analyses | 23 |
| Inherited empty-roster record, unavailable | 1 |
| Resampled coadds | 736 |
| Nonlinear released-source fits | 4,416 |
| Available propagated joint contrasts | 7,296 |
| Requested family × block × phase groups | 576 |
| Complete conditional sensitivity groups | 456 |
| Inherited missing-window groups | 96 |
| Inherited failed-roster groups | 24 |

Two declared block lengths, 30 and 120 minutes, each use 16 draws per field. They
are sensitivity settings, not estimated correlation times. Repeating the command
reused all 24 sealed outcomes without new numerical cases. The previous failed
profile-transfer batch remains failed; its command now returns a nonzero exit status.
Historical-source checks preserve older audits while rejecting changed data inputs.

For [TIC 21694454](../candidates/tic-21694454-s01/README.md), the structural discrepancy
reported in the [profile comparison](profile-transfer-review-2026-10-12.md) persists:

| Model / block length | Mean target contribution (e−/s) | Between-draw spread (e−/s) | Total conditional error (e−/s) |
|---|---:|---:|---:|
| Archive / 30 min | 306.72 | 1.94 | 21.23 |
| Learned positions / 30 min | 16.94 | 1.18 | 20.29 |
| Archive / 120 min | 307.57 | 2.77 | 21.33 |
| Learned positions / 120 min | 17.31 | 1.70 | 20.33 |

The target's rejected learned core remains a corrected-archive fallback. Resampling
variation within a family is much smaller than the roughly 290 e−/s difference
between families. **The bootstrap does not establish that either family identifies
the host, and cannot turn this discrepancy into a small calibrated error bar.**
These signed in-stamp contributions and white conditional errors are not planet
probabilities or a false-positive classification.

The moment calculation separately retains mean conditional late-noise covariance
and between-draw covariance. Their sum is a conditional sensitivity calculation;
no posterior model probabilities, extreme-tail coverage or source exclusions are
adopted. Structural PRF/astrometric/deblending bias, correlated late noise, source
completeness, physical eclipse feasibility and independent transfer calibration
remain open. Sixteen draws cannot qualify 99% coverage. Original missing windows
and the failed roster remain in the complete outcome census.

Independent audits check all 736 native coadds, observing-gap and photon separation,
7,296 QR-based coefficient/covariance replays, and 456 moment summaries. Numerical
agreement does not certify global nonlinear optima or physical uncertainty coverage.
The [aggregate receipt](../reviews/profile-bootstrap-review-2026-10-12-v1.json)
records those results. Full selected witnesses are stored with the research task;
this public supplement is not a complete raw-input reproduction capsule.

All 172 public dossiers remain unclassified. Prior warnings, catalogue assessments
and disclosure dates remain unchanged; no host or planetary promotion follows.
