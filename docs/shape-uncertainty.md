# Conditional shape uncertainties

Schema1.3 retains the previously omitted duration/ingress covariance from the existing
exposure-sampled trapezoid refinement. Strict1.0, nullable1.1 and catalogue-context1.2
remain available as pinned contracts. This addition preserves the fitted values and
the original epoch-period covariance, catalogue snapshots and provisional assessments.

The numerical command replays every recorded refinement using its original clean-Git
TOML recipe, sealed request, pinned primary products and legacy starting hypotheses.
All source assessments and artifacts are checked before fitting. Each row records the
original and replayed diagnostics and their exact equality after removing only the
new covariance field. A mismatch, bound/rank failure or failed execution cannot supply
a public duration error. The complete cohort, including unsuccessful fits, is retained.

```bash
uv run --extra agent transit-search vet fit-uncertainty --report /path/to/report.json \
  --output /path/to/new-fit-errors.json --workers 3
# A separate numerical repeat uses a new output, without --snapshot.
# Sealed cached delivery preserves the earlier numerical results:
uv run --extra agent transit-search vet fit-uncertainty --report /path/to/report.json \
  --output /path/to/cached-fit-errors.json --snapshot /path/to/previous/RUN
# Public repository: prepare validated changes, without publishing:
uv run python scripts/enrich_uncertainty.py --root . --batch campaign \
  --report /path/to/RUN/fit-uncertainty.json
```

The fit uses finite-difference Jacobians of profiled least-squares residuals, free
signed depths and linear baselines per event, and diagonal noise with the saved
out-of-transit beta diagnostic. The pseudoinverse covariance is inflated by
`max(1, reduced chi-square)`. The duration error in hours is
`24 * sqrt(covariance[2][2])`; the covariance itself uses days for duration.
The complete parameter order is epoch, period, duration and ingress fraction, with
the reference-epoch matrix also retained. The epoch transformation is recorded by
the original anchor cycle. The validator checks covariance symmetry and PSD after
unit normalization, its timing block, and its duration/ingress marginal errors.

These are **conditional local Gaussian errors**, with uncalibrated coverage. They
omit uncertainty from seed/event selection, clock corrections, timing variability,
baseline/model choice, host identity and dilution. A covariance is not a posterior
and does not characterize multimodality. Correlated-noise models can materially
change transit error estimates ([Carter and Winn,2009](https://arxiv.org/abs/0909.0747));
this update does not claim that the diagonal approximation covers those effects.

The duration describes the first-to-last-contact width of the fitted trapezoid,
including its declared exposure sampling. It is not a limb-darkened physical transit
fit. Rp/Rstar, impact parameter and a/Rstar remain unfitted; the schema says so
explicitly. Physical modelling and uncertainty calibration require later evidence.
Public reproduction remains **evidence inspection only**; the private numerical
replay does not imply a fresh public-input numerical reproduction.
