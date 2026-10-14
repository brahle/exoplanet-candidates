# TIC 467668175 / S01

## Diagnostic figures

![Five-panel diagnostic](evidence/figures/diagnostic.png)

Saved signed local profiles; all numeric events, including negative depths. Failures and excluded clock products remain in the context. Display-bin error bars are uncalibrated white standard errors.

All event pages: [events-01.png](evidence/figures/events-01.png), [events-02.png](evidence/figures/events-02.png), [events-03.png](evidence/figures/events-03.png).

[Plot context](evidence/figures/plot-context.json) · [Saved plot vectors](evidence/figures/plot-data.npz) · [Rendering methods](../../docs/diagnostic-figures.md).


**Provisional unclassified transit-like signal.** Source attribution and timing consistency are unresolved.
Binary, blend and instrumental explanations remain open. This is a dated evidence record, not a verified planet.

Diagnostic period: 1.9287512865 ± 1.39e-05 d.
Epoch: BJD_TDB 2458572.96386501 ± 0.0119 d.
Duration: 4.3506 h (± 0.368 h; conditional diagnostic error).
Linear-baseline depth: 663.3 ± 75.8 ppm,
from 37 usable events in 3 sectors.
Errors are conditional diagnostic estimates.

Both saved baseline orders give positive aggregate dips. The minimum conditional depth/error
over sector leaveouts is 6.65; it is not a false-alarm probability.
Odd/even depth contrast: 0.114 conditional error units. The saved odd/even diagnostic supplies no definitive classification.
The [photometry](evidence/photometry.json) retains unusable events, alternate reductions,
phase controls and timestamp-withheld products. [Robustness](evidence/robustness.json),
[timing](evidence/timing-summary.json) and [alternative signals](evidence/alternative-summary.json)
retain adverse evidence, signed secondary/odd-even/harmonic probes and failures. Strong
secondary or odd/even differences can favour a binary explanation; those probes have not
been calibrated into a definitive classification.

The immutable discovery seed and adopted diagnostic hypothesis are in [settings](analysis-settings.json).
The aperture TIC is not an established physical host; any Gaia DR3 catalogue association
is separate from attribution of the dip.
Read [novelty limits](NOVELTY.md) and [reproduction coverage](REPRODUCIBILITY.md).

## Catalogue stellar context

The [pinned TIC/Gaia context](evidence/stellar-catalogue.json) supplies aperture-star Teff, radius, mass, TESS magnitude and distance with catalogue uncertainties. The structured host block marks the physical host and dilution unresolved; these are catalogue values, not a planet-radius inference. Gaia association: associated.

## Progressive Phase 4 follow-up

Fresh checks use 5 timing-qualified primary sectors, with one reduction per sector. Diagnostic warning flags: none in this subset. [Detailed results and missing checks](evidence/vetting-findings.json). These descriptive flags do not assign a planet probability. The initial screen remains incomplete and source attribution unresolved.
