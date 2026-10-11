#!/usr/bin/env python3
"""Replay selected-input exposure diagnostics and point fits; no planet validation."""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from transit_search.exposure_integration import ContactIntegratedLikelihood  # noqa: E402
from transit_search.vetting.physical import PhysicalLikelihood  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / "files.json").read_text())
    for name, checksum in manifest["sha256"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or sha(ROOT / path) != checksum:
            raise ValueError(f"Package seal differs: {name}")
    certificates = []
    for sid in manifest["signals"]:
        root = ROOT / sid
        meta = json.loads((root / "metadata.json").read_text())
        expected = json.loads((root / "expected.json").read_text())
        cfg = meta["review_config"]
        events = meta["events"]
        with np.load(root / "events.npz", allow_pickle=False) as arrays:
            for i, event in enumerate(events):
                for key in ("t", "y"):
                    event[key] = arrays[f"event{i:04d}_{key}"]
        original = PhysicalLikelihood(events, meta["ephemeris"], meta["density_prior"],
                                      meta["scenario"], meta["original_config"])
        models = {"original_endpoint_mean": original}
        models.update({f"contact_gauss_{order}": ContactIntegratedLikelihood(original, order)
                       for order in cfg["orders"]})
        with np.load(root / "review-vectors.npz", allow_pickle=False) as arrays:
            vectors = arrays["parameters"]
        with np.load(root / "expected-witness.npz", allow_pickle=False) as witness:
            max_flux, max_residual = 0.0, 0.0
            for prefix, theta in [(f"saved{i:03d}", v) for i, v in enumerate(vectors)] + [
                ("refit", np.asarray(expected["selected_point_refit"]["parameters"]))
            ]:
                for label, model in models.items():
                    flux = np.concatenate(model.fluxes(theta))
                    residual = model.residuals(theta)
                    old_flux, old_residual = witness[f"{prefix}_{label}_flux"], witness[
                        f"{prefix}_{label}_residual"]
                    np.testing.assert_allclose(flux, old_flux, rtol=1e-10, atol=1e-10)
                    np.testing.assert_allclose(residual, old_residual, rtol=1e-10, atol=1e-7)
                    max_flux = max(max_flux, float(np.max(abs(flux - old_flux))))
                    max_residual = max(max_residual, float(np.max(abs(residual - old_residual))))
        model = models[f"contact_gauss_{cfg['fit_order']}"]
        fit_diffs = []
        for old in expected["point_refits"]:
            fit = least_squares(model.residuals, old["start_parameters"],
                                bounds=(model.lower, model.upper),
                                max_nfev=cfg["optimizer_max_nfev"], x_scale="jac")
            if bool(fit.success) != old["optimizer_success"]:
                raise ValueError("Optimizer termination changed")
            logp = model.log_prob(fit.x)
            if not np.isfinite(logp) or old["log_probability"] is None:
                raise ValueError("Point refit is not finite")
            delta = abs(logp - old["log_probability"])
            if delta > 1e-4:
                raise ValueError("Point-refit objective changed beyond replay tolerance")
            # Compare predicted exposures, rather than fragile boundary coordinates.
            flux_delta = float(np.max(abs(np.concatenate(model.fluxes(fit.x))
                                         - np.concatenate(model.fluxes(old["parameters"])))))
            if flux_delta > 1e-7:
                raise ValueError("Point-refit exposures changed beyond replay tolerance")
            fit_diffs.append({"absolute_log_probability_difference": delta,
                              "maximum_flux_difference_ppm": flux_delta * 1e6})
        certificates.append({"signal_id": sid, "status": "replay_passed",
                             "fixed_vectors": len(vectors) + 1,
                             "maximum_fixed_flux_difference_ppm": max_flux * 1e6,
                             "maximum_projected_residual_difference": max_residual,
                             "refits": fit_diffs, "scientific_promotions": 0})
    result = {"status": "replay_passed", "scope": manifest["scope"],
              "package_manifest_sha256": sha(ROOT / "files.json"), "signals": certificates,
              "scientific_promotions": 0}
    Path("replay-certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
