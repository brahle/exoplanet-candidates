# Run 6: deeper follow-up, 12 October 2026

Fourteen new **unclassified signal dossiers** are added to the existing 172,
bringing the catalogue to 186. All 826 upstream vetting passes are retained in
the [triage ledger](../batches/run6-v1/triage-cohort.json). None is validated or
assigned a planet probability. Selection for a dossier is evidence disclosure,
not a finding that the signal is a planet.

## What was rerun

The saved survey evidence matches source revision
`231c6cb9b1c91131a56f137b500d3f220e099a06`. Fresh follow-up uses 96 cached FITS
products for the 14 selected targets, strict quality masks, one primary reduction
per sector, exposure-integrated diagnostic trapezoids, linear and quadratic local
baselines, sector/event leaveouts, signed timing profiles, P/2/P/2P hypotheses,
odd/even contrasts and nine secondary phases. Failed and missing events remain.
QLP timing-unverified sectors 99–104 are withheld from fresh measurements.

The configured Exoplanet MCP was queried at both discovery and refined periods,
with a 120″ cone and 1% period tolerance: all 28 queries returned
`no_match_in_checked_sources`. This is limited to the listed snapshots. Saved
Gaia/VSX neighbour searches and the catalogue gaps remain separately visible.
No-match does not establish novelty or exclude a blended binary.

All 14 have positive box-window aggregate depths with both baseline orders and
positive sector leaveouts. Exact numerical replay retained conditional duration
and ingress covariance for all 14. Official TIC-to-Gaia DR2-neighbourhood queries
associate all 14 aperture targets with DR3; TIC stellar parameters have provenance.
Those catalogue associations do not identify which star produces the dip.
Physical Rp/R★, impact parameter and a/R★ have not been fitted in these dossiers.

## Findings that change the follow-up priorities

- **TIC 284070379** remains worth prioritising: P = 3.37354327 d, positive dips
  in both baseline models, four primary sectors and no flags in this diagnostic
  subset. Host attribution and planetary interpretation remain open.
- **TIC 292547242** needs renewed scrutiny: the phase-0.7 scan gives a conditional
  1,973 ppm dip, 5.20 nominal error units. Sector 13 contributes a particularly
  strong event stack; the result is uneven across sectors. Its early-segment
  ephemeris also extrapolates poorly. This is a warning, not a proven secondary
  eclipse or calibrated significance.
- **TIC 261707476** has a phase-0.5 dip at 3.70 nominal error units, based on only
  two numeric events and driven mainly by sector 38. A binary explanation needs
  attention, alongside the limited coverage and noise assumptions.
- **TIC 38593803** has odd/even tension of 3.12 nominal error units in the reference
  profile, falling to 1.91 with a quadratic baseline. **TIC 79810298** crosses
  the descriptive threshold only in the 1.2-duration variant (3.009); the reference
  contrast is 1.94. Neither is a robust binary classification.
- **TIC 103065229 and TIC 292547242** have imprecise early-only ephemeris
  extrapolations, with maximum diagnostic residuals of approximately 6.6 and 28.6
  durations respectively. Their broad conditional prediction intervals do not
  establish a timing contradiction. Event windows and selection depend on the
  globally chosen hypothesis, so this is not an independent prediction certificate.
- **TIC 358231727 and TIC 425933702**, both near 13 d, weaken in the qualified older
  sectors: box-window S/N ≈ 3.24 and 1.47. Neither has enough diagnostic timing
  events for a joint timing fit. Period clustering is an instrumental warning,
  not proof of an artifact.

Seven records have at least one of these descriptive flags; seven have none.
Six lack usable early-to-late timing diagnostics, including four of the seven
without flags. All 14 remain incomplete. **Seven without these warnings is not
seven likely planets.** Warning rules and per-sector values are in the
[machine-readable findings](../batches/run6-v1/followup-findings.json).

## The pixel classifier needs more qualification

TIC 358231727 had one saved hypothesis per sector. The upstream classifier used
99 as a missing-alternative sentinel and summed it to a margin of 198. That is
not source discrimination. The new audit leaves its margin unavailable and
flags the missing competitor; its source attribution remains unresolved.

Only eight ranked source hypotheses were saved per sector. A target absent from
that list provides a conditional ranking bound only if its presence in the
tested-source roster is established. The complete roster is unavailable. Fixed
Gaussian profiles, signed amplitudes, uncertain difference-image noise and
sector-dependent alternatives also prevent interpreting summed Δχ² as a calibrated
host probability. The original 676 `off-target` routes are therefore retained as
**legacy diagnostic labels**, not promoted to 676 adjudicated false positives.

Likewise, the two excluded upstream survivors with nearby period-matched Gaia EBs
(TIC 215270756 and TIC 455630912) remain association hypotheses in the full ledger.
Their six-arcsecond neighbours do not alone prove contamination.

## Public evidence and remaining work

The 14 dossiers include 30 diagnostic/event-page images and saved plot vectors.
The original search spectra were not saved. On 13 October the initially empty
panels were filled with explicitly labelled [documented reconstructions](diagnostic-figures.md)
using the original discovery-sector recipe and exact input bytes. Earlier
figures remain available in each dossier's figure-history directory.
Readers can inspect and replot the evidence, but a clean public numerical rerun
is not yet supplied. Conditional errors are not qualified for observing forecasts.

Next priorities are source attribution with complete tested rosters and qualified
pixel models; sector/baseline replication of the two secondary warnings; precise
timing for the weak or poorly predicted cases; physical transit/binary/dilution
models; and detection/false-positive calibration. Complete EB/variable catalogue
coverage is still needed. Existing ingestion tasks cover Gaia DR3 EBs, VSX and
Prša's TESS EB catalogue; this follow-up creates no duplicate task or production
database change.

The [source receipt](../batches/run6-v1/followup-source-receipt.json) binds these
findings to terminal evidence runs. Earlier dossiers, assessments and dates are
preserved. New disclosure dates are recorded from the actual public push.
