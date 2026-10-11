# Replay the exposure-integration diagnostic

Package version1.0.0, for the two already-public signals TIC261119502 and TIC339451799.
This reproduces **selected-input exposure calculations and bounded point refits**.
It does not reproduce raw-FITS acquisition, reduction, event selection, the original
posterior sampling, source attribution or a planet-candidate classification.

From this directory, with Python3.12 and uv:

```
uv sync --frozen
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 \
  uv run --frozen python -I replay.py
```

The command verifies the file manifest before numerical work. It replays the
original endpoint averaging and contact-panel orders16/32/64 on all saved review
vectors and the selected point refit. It then reruns all four point-fit starts per
signal and writes `replay-certificate.json` locally. No remote data are needed once
the locked Python dependencies are installed. It does not publish anything.

`events.npz` contains exact selected relative-flux/cadence arrays from the original
pilot; metadata declares exposure widths, BTJD(TDB) times, primary products, fixed
noise, ephemeris, conditional host-density prior and original baseline/model bounds.
These are derived inputs, not the full mission light curves. Uniform exposure
weighting and a circular orbit are assumed. The averaging rule differs while the
instantaneous quadratic batman kernel is shared. The source subset is copied
exactly from the numerical experiment, including original sampling helpers that
this replay does not call.

Fixed-vector checks use flux absolute tolerance1e-10 and projected-residual
absolute tolerance1e-7, both relative tolerance1e-10. Point-fit reproduction requires
matching optimizer success, objective difference<=1e-4 and maximum predicted-flux
difference<=1e-7 (0.1ppm). Those are replay tolerances, not scientific classification
criteria. A successful optimizer can reach a boundary or local optimum; these point
fits have no corrected posterior uncertainty. Gauss-order agreement is empirical,
not a rigorous error bound. Neither replay success nor a checksum validates a host,
noise model, physical interpretation, detection reliability or planet probability.

See the [dated scientific review](../../docs/exposure-integration-review-2026-10-11.md).
