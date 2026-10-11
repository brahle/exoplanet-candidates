"""Conditional dark-occultor geometry, with exposure integration and saved chains.

This experimental model does not validate a host, clock, noise model or disposition.
Linear event baselines are integrated out under a common improper flat prior.
Noise hyperparameters are OOT estimates, not posterior-calibrated uncertainties.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np
from astropy.constants import G, M_sun, R_sun
from scipy.optimize import least_squares

PARAMETERS = [
    "anchor_shift_duration",
    "period_drift_duration",
    "radius_ratio",
    "impact_fraction",
    "log10_density_cgs",
    "limb_q1",
    "limb_q2",
]


def density_prior(star, cfg):
    """Explicit first-order, independent catalogue M/R error approximation."""
    mass, radius = star["parameters"]["mass_Msun"], star["parameters"]["radius_Rsun"]
    values = [mass.get("value"), radius.get("value"), mass.get("error"), radius.get("error")]
    if any(x is None or not math.isfinite(x) or x <= 0 for x in values):
        return None
    m, r, dm, dr = values
    rho = m * M_sun.cgs.value / (4 * np.pi * (r * R_sun.cgs.value) ** 3 / 3)
    sigma = np.sqrt((dm / m) ** 2 + (3 * dr / r) ** 2) / np.log(10)
    return {
        "mean_log10_cgs": float(np.log10(rho)),
        "sigma_log10_cgs": float(max(sigma, cfg["density_prior_log_sigma_floor"])),
        "scope": "Assumed catalogue aperture star; independent M/R first-order errors "
        "plus declared floor; not a host posterior",
    }


def orbit(period_d, radius_ratio, impact_fraction, log_density, eccentricity, omega_deg):
    a = (G.cgs.value * 10**log_density * (period_d * 86400) ** 2 / (3 * np.pi)) ** (1 / 3)
    b = (1 + radius_ratio) * impact_fraction
    cosine = b / a * (1 + eccentricity * np.sin(np.deg2rad(omega_deg))) / (1 - eccentricity**2)
    if period_d <= 0 or a * (1 - eccentricity) <= 1 + radius_ratio or not 0 <= cosine < 1:
        raise ValueError("Non-transiting or intersecting-orbit geometry")
    return float(a), float(b), float(np.rad2deg(np.arccos(cosine)))


def limb_coefficients(q1, q2):
    """Physical quadratic sampling transform; broad uniform q priors, no fixed K dwarf."""
    return [2 * np.sqrt(q1) * q2, np.sqrt(q1) * (1 - 2 * q2)]


@dataclass
class Whitening:
    """Exact stationary OU/AR1 whitening with actual irregular cadence gaps."""

    sigma: float
    transitions: np.ndarray

    def apply(self, values):
        v = np.asarray(values, float)
        w = v.copy() / self.sigma
        a = self.transitions
        if v.ndim == 1:
            w[1:] = (v[1:] - a * v[:-1]) / (self.sigma * np.sqrt(1 - a * a))
        else:
            w[1:] = (v[1:] - a[:, None] * v[:-1]) / (self.sigma * np.sqrt(1 - a * a)[:, None])
        return w


def whitening(t, sigma_white, rho, integration_d, mode):
    if sigma_white <= 0 or not 0 <= rho < 1 or np.any(np.diff(t) <= 0):
        raise ValueError("Invalid noise or cadence ordering")
    if mode == "white":
        return Whitening(sigma_white, np.zeros(len(t) - 1))
    if mode != "oot_ou":
        raise ValueError("Undeclared noise model")
    # Adjacent differences estimate sigma_white. OU marginal variance differs.
    sigma = sigma_white / np.sqrt(1 - rho)
    a = rho ** (np.diff(t) / integration_d)
    return Whitening(sigma, a)


class PhysicalLikelihood:
    def __init__(self, events, ephemeris, prior, scenario, cfg):
        import batman

        self.events, self.ephemeris = events, ephemeris
        self.prior, self.scenario, self.cfg = prior, scenario, cfg
        self.duration = ephemeris["duration_h"] / 24
        cycles = np.array([e["cycle"] for e in events])
        self.anchor_cycle = int(np.rint(np.median(cycles)))
        self.span_cycles = int(max(1, np.ptp(cycles)))
        self.anchor_btjd = (
            ephemeris["epoch_bjd_tdb"] - 2457000 + self.anchor_cycle * ephemeris["period_d"]
        )
        c = cfg["model"]
        self.lower = np.array(
            [
                -c["epoch_half_width_durations"],
                -c["accumulated_period_half_width_durations"],
                c["radius_ratio_bounds"][0],
                c["impact_fraction_bounds"][0],
                c["log_density_cgs_bounds"][0],
                c["limb_q_bounds"][0],
                c["limb_q_bounds"][0],
            ]
        )
        self.upper = np.array(
            [
                c["epoch_half_width_durations"],
                c["accumulated_period_half_width_durations"],
                c["radius_ratio_bounds"][1],
                c["impact_fraction_bounds"][1],
                c["log_density_cgs_bounds"][1],
                c["limb_q_bounds"][1],
                c["limb_q_bounds"][1],
            ]
        )
        self.pm = batman.TransitParams()
        self.pm.t0, self.pm.per, self.pm.rp = 0, ephemeris["period_d"], 0.03
        self.pm.a, self.pm.inc = 20, 89
        self.pm.ecc, self.pm.w = scenario["eccentricity"], scenario["omega_deg"]
        self.pm.u, self.pm.limb_dark = [0.4, 0.2], "quadratic"
        self.groups = []
        self.prepared = []
        for e in events:
            w = whitening(
                e["t"], e["sigma_white"], e["oot_rho"], e["integration_d"], scenario["noise"]
            )
            design = np.polynomial.polynomial.polyvander(
                (e["t"] - e["center_btjd"]) / self.duration, cfg["data"]["baseline_order"]
            )
            wd = w.apply(design)
            q, r = np.linalg.qr(wd, mode="reduced")
            if np.linalg.matrix_rank(r) != design.shape[1]:
                raise ValueError("Singular event baseline")
            wy = w.apply(e["y"])
            self.prepared.append((w, q, wy))
        # One exact batman vector per primary product/integration width; no folding/binning.
        for key in sorted({(e["filename"], e["integration_d"]) for e in events}):
            indices = [
                i for i, e in enumerate(events) if (e["filename"], e["integration_d"]) == key
            ]
            t = np.concatenate([events[i]["t"] for i in indices]) - self.anchor_btjd
            if np.any(np.diff(t) <= 0):
                raise ValueError("Duplicate or overlapping likelihood exposures")
            model = batman.TransitModel(
                self.pm, t, exp_time=key[1], supersample_factor=c["supersample_factor"], nthreads=1
            )
            self.groups.append((indices, model))
        self.n_residuals = sum(len(e["t"]) for e in events) + int(prior is not None)

    def unpack(self, theta):
        shift, drift, k, z, density, q1, q2 = theta
        per = self.ephemeris["period_d"] + drift * self.duration / self.span_cycles
        a, b, inc = orbit(
            per, k, z, density, self.scenario["eccentricity"], self.scenario["omega_deg"]
        )
        anchor = self.anchor_btjd + shift * self.duration
        # Transform to the original reference cycle, keeping period covariance.
        epoch = anchor - self.anchor_cycle * per
        return {
            "epoch_btjd": float(epoch),
            "period_d": float(per),
            "anchor_btjd": float(anchor),
            "radius_ratio": float(k),
            "impact_parameter": b,
            "a_over_rstar": a,
            "inclination_deg": inc,
            "log10_density_cgs": float(density),
            "limb_q1": float(q1),
            "limb_q2": float(q2),
        }

    def fluxes(self, theta):
        p = self.unpack(theta)
        self.pm.t0 = p["anchor_btjd"] - self.anchor_btjd
        self.pm.per, self.pm.rp = p["period_d"], p["radius_ratio"]
        self.pm.a, self.pm.inc = p["a_over_rstar"], p["inclination_deg"]
        self.pm.u = limb_coefficients(p["limb_q1"], p["limb_q2"])
        fluxes = [None] * len(self.events)
        for indices, model in self.groups:
            values = self.scenario["target_flux_fraction"] * (model.light_curve(self.pm) - 1)
            offset = 0
            for i in indices:
                n = len(self.events[i]["t"])
                fluxes[i] = values[offset : offset + n]
                offset += n
        return fluxes

    def residuals(self, theta):
        try:
            fluxes = self.fluxes(theta)
        except (ValueError, RuntimeError):
            return np.full(self.n_residuals, 1e8)
        parts = []
        for (w, q, wy), model in zip(self.prepared, fluxes, strict=True):
            residual = wy - w.apply(model)
            parts.append(residual - q @ (q.T @ residual))
        if self.prior is not None:
            parts.append(
                np.array(
                    [(theta[4] - self.prior["mean_log10_cgs"]) / self.prior["sigma_log10_cgs"]]
                )
            )
        return np.concatenate(parts)

    def log_prob(self, theta):
        if not np.all((theta > self.lower) & (theta < self.upper)):
            return -np.inf
        r = self.residuals(theta)
        return -0.5 * float(r @ r) if np.max(np.abs(r)) < 1e8 else -np.inf


def convergence(chains, acceptances, cfg):
    """Independent ensembles + IAT; never treat coupled walkers as independent chains."""
    import emcee

    tau = []
    for chain in chains:
        t = emcee.autocorr.integrated_time(chain, tol=0, quiet=True)
        tau.append(t)
    tau = np.asarray(tau)
    finite = bool(np.all(np.isfinite(tau)) and np.all(tau > 0))
    enough = finite and all(
        len(c) >= cfg["minimum_tau_multiples"] * np.max(t) for c, t in zip(chains, tau, strict=True)
    )
    draws = [c.reshape(-1, c.shape[-1]) for c in chains]
    pooled = np.concatenate(draws)
    spread = np.std(pooled, axis=0)
    medians = np.array([np.median(d, axis=0) for d in draws])
    discrepancy = np.ptp(medians, axis=0) / np.maximum(spread, np.finfo(float).tiny)
    accepted = bool(
        all(cfg["minimum_acceptance"] <= a <= cfg["maximum_acceptance"] for a in acceptances)
    )
    agreement = bool(np.all(discrepancy <= cfg["maximum_median_difference_std"]))
    return {
        "status": "conditional_sampling_checks_passed"
        if enough and accepted and agreement
        else "sampling_not_qualified",
        "autocorrelation_steps": [
            [float(v) if np.isfinite(v) else None for v in row] for row in tau
        ],
        "retained_steps_per_ensemble": [len(c) for c in chains],
        "acceptance_per_ensemble": acceptances,
        "independent_ensemble_median_difference_std": discrepancy.tolist(),
        "sufficient_tau_length": bool(enough),
        "ensemble_agreement": agreement,
        "acceptance_in_range": accepted,
        "independent_ensembles": len(chains),
        "limits": [
            "Heuristic sampling checks; no convergence guarantee or calibrated coverage",
            "No R-hat treating coupled ensemble walkers as independent chains",
        ],
    }


def sample(likelihood, cfg, identity, progress=None):
    import emcee

    c = cfg["sampler"]
    if c["ensembles"] < 2 or c["walkers"] < 2 * len(PARAMETERS) + 2:
        raise ValueError("Need independent ensembles and enough walkers")
    depth = likelihood.ephemeris.get("depth_ppm") or 1000
    k = np.sqrt(max(1e-6, depth * 1e-6) / likelihood.scenario["target_flux_fraction"])
    rho = likelihood.prior["mean_log10_cgs"] if likelihood.prior else 0
    optima = []
    for b in cfg["model"]["optimizer_impact_starts"]:
        start = np.array([0, 0, k, b, rho, 0.36, 0.35])
        start = np.clip(start, likelihood.lower + 1e-5, likelihood.upper - 1e-5)
        fit = least_squares(
            likelihood.residuals,
            start,
            bounds=(likelihood.lower, likelihood.upper),
            max_nfev=cfg["model"]["optimizer_max_nfev"],
        )
        if np.isfinite(likelihood.log_prob(fit.x)):
            optima.append((likelihood.log_prob(fit.x), fit.x))
    if not optima:
        raise ValueError("No finite physical-model initialization")
    optima.sort(key=lambda pair: pair[0], reverse=True)
    initial = optima[0][1]
    samplers = []
    width = likelihood.upper - likelihood.lower
    seeds = []
    for ensemble in range(c["ensembles"]):
        seed = int(
            hashlib.sha256(f"{c['random_seed']}:{identity}:{ensemble}".encode()).hexdigest()[:8], 16
        )
        seeds.append(seed)
        rng = np.random.default_rng(seed)
        # Independent ensembles alternate distinct finite optimization basins.
        origin = optima[min(ensemble, len(optima) - 1)][1]
        positions = []
        for _ in range(c["walkers"]):
            for _ in range(10000):
                p = (
                    origin
                    + rng.normal(size=len(PARAMETERS)) * width * c["initial_scatter_fraction"]
                )
                if np.isfinite(likelihood.log_prob(p)):
                    positions.append(p)
                    break
            else:
                raise ValueError("Cannot initialize a finite ensemble")
        sampler = emcee.EnsembleSampler(c["walkers"], len(PARAMETERS), likelihood.log_prob)
        sampler.random_state = np.random.RandomState(seed).get_state()
        sampler.run_mcmc(np.array(positions), c["burn_steps"], progress=False)
        sampler.reset()
        samplers.append(sampler)
    steps = 0
    while steps < c["max_steps"]:
        chunk = min(c["check_every_steps"], c["max_steps"] - steps)
        for sampler in samplers:
            sampler.run_mcmc(None, chunk, progress=False)
        steps += chunk
        diag = convergence(
            [s.get_chain() for s in samplers],
            [float(np.mean(s.acceptance_fraction)) for s in samplers],
            c,
        )
        if progress:
            progress(steps, diag)
        if diag["status"] == "conditional_sampling_checks_passed":
            break
    chains = np.array([s.get_chain() for s in samplers])
    flat = chains.reshape(-1, chains.shape[-1])
    derived = [likelihood.unpack(t) for t in flat]
    names = list(derived[0])
    values = np.array([[d[n] for n in names] for d in derived])
    quantiles = {n: np.percentile(values[:, i], [16, 50, 84]).tolist() for i, n in enumerate(names)}
    covariance = np.cov(
        values[:, [names.index("epoch_btjd"), names.index("period_d")]], rowvar=False
    )
    boundary = {
        n: float(
            np.mean(
                (flat[:, i] - likelihood.lower[i] < cfg["model"]["boundary_fraction"] * width[i])
                | (likelihood.upper[i] - flat[:, i] < cfg["model"]["boundary_fraction"] * width[i])
            )
        )
        for i, n in enumerate(PARAMETERS)
    }
    return {
        "parameter_names": PARAMETERS,
        "seeds": seeds,
        "sampling": diag,
        "physical_parameters_status": "conditional_sampling_diagnostics_only",
        "quantile_status": "retained_draws_16_50_84_unqualified"
        if diag["status"] != "conditional_sampling_checks_passed"
        else "conditional_draw_quantiles_sampling_checks_passed",
        "posterior_16_50_84": quantiles,
        "covariance_epoch_period_d2": covariance.tolist(),
        "covariance_reference": "Original seed reference cycle in BTJD; same retained draws",
        "anchor_cycle": likelihood.anchor_cycle,
        "anchor_btjd": likelihood.anchor_btjd,
        "grazing_draw_fraction": float(
            np.mean(
                values[:, names.index("impact_parameter")]
                > 1 - values[:, names.index("radius_ratio")]
            )
        ),
        "prior_boundary_draw_fractions": boundary,
        "best_initializer": initial.tolist(),
        "initializer_log_prob": float(optima[0][0]),
        "derived_radius_Re": None,
        "classification_promoted": False,
        "limits": [
            "Dark occultor with negligible mass; luminous/stellar companions not fitted",
            "Catalogue density, fixed dilution and eccentricity are conditional scenarios",
            "Broad physical limb-darkening priors; stellar-atmosphere constraints absent",
            "OU parameters estimated out of transit and held fixed; coverage uncalibrated",
            "Window/event selection and mission clock remain conditional",
            "No joint host-radius posterior, so no derived absolute occultor radius",
            "Sampling checks do not settle source, timing, reliability or novelty",
            "Scenario log probabilities have omitted normalization constants; no model odds/FPP",
        ],
    }, {
        "chains": chains,
        "log_prob": np.array([s.get_log_prob() for s in samplers]),
        "derived_parameter_names": np.array(names),
        "derived_draws": values,
        "parameter_names": np.array(PARAMETERS),
    }
