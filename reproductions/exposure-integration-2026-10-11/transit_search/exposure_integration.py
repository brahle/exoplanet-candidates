"""Separate circular-orbit contact-panel exposure integration experiment.

The instantaneous quadratic batman kernel is shared with the original model.
Only the exposure averaging rule differs. Refinement agreement is empirical,
not a rigorous error bound, posterior calibration or astrophysical validation.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from .vetting.physical import PhysicalLikelihood, limb_coefficients


def circular_contacts(period, a, b, k):
    """Contact offsets from inferior conjunction for a detached circular orbit."""
    if not all(np.isfinite([period, a, b, k])) or not (
        period > 0 and 0 < k < 1 and 0 <= b < 1 + k < a
    ):
        raise ValueError("Unsupported circular contact geometry")
    half = []
    for radius in (1 + k, 1 - k):
        if radius > b:
            half.append(
                period / (2 * np.pi) * np.arcsin(np.sqrt((radius**2 - b**2) / (a**2 - b**2)))
            )
    return np.sort(np.concatenate([-np.asarray(half), half]))


@lru_cache(maxsize=16)
def rule(order):
    if type(order) is not int or not 2 <= order <= 256:
        raise ValueError("Unsupported Gauss-Legendre order")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    nodes.flags.writeable = weights.flags.writeable = False
    return nodes, weights


def panel_average(evaluate, times, width, period, center, contacts, order):
    """Average each exposure over panels split at its nearby transit contacts.

    Times and center share a relative time origin. Exposure widths must be less
    than half a period, so a single nearest conjunction supplies all contacts.
    Empty panels contribute zero; each nonempty panel is quadrature-integrated.
    """
    t, contacts = np.asarray(times, float), np.asarray(contacts, float)
    if not (
        t.ndim == contacts.ndim == 1
        and len(t) > 0
        and np.all(np.isfinite(t))
        and np.all(np.isfinite(contacts))
        and np.isfinite(center)
        and np.isfinite(width)
        and np.isfinite(period)
        and period > 0
        and 0 < width < period / 2
        and np.all(np.abs(contacts) < period / 4)
    ):
        raise ValueError("Invalid exposure/contact/time input")
    nodes, weights = rule(order)
    # Keep arithmetic relative to each exposure, not absolute BJD timestamps.
    conjunction = center + np.rint((t - center) / period) * period
    inside = np.clip(conjunction[:, None] - t[:, None] + contacts, -width / 2, width / 2)
    edges = np.sort(
        np.column_stack([np.full(len(t), -width / 2), inside, np.full(len(t), width / 2)]), axis=1
    )
    lengths = np.diff(edges, axis=1)
    row, panel = np.nonzero(lengths > 0)
    half = lengths[row, panel] / 2
    middle = (edges[row, panel] + edges[row, panel + 1]) / 2
    samples = (t[row, None] + middle[:, None] + half[:, None] * nodes).ravel()
    values = np.asarray(evaluate(np.ascontiguousarray(samples)), float)
    if values.shape != samples.shape or not np.all(np.isfinite(values)):
        raise ValueError("Invalid instantaneous model evaluations")
    integral = (values.reshape(-1, order) @ weights) * half / width
    return np.bincount(row, weights=integral, minlength=len(t))


class ContactIntegratedLikelihood(PhysicalLikelihood):
    """Original data, priors, noise and baseline; different exposure integration."""

    def __init__(self, original, order):
        if original.scenario["eccentricity"] != 0:
            raise ValueError("Contact integration experiment supports circular orbits only")
        rule(order)
        super().__init__(
            original.events, original.ephemeris, original.prior, original.scenario, original.cfg
        )
        self.order = order

    def fluxes(self, theta):
        import batman

        p = self.unpack(theta)
        self.pm.t0 = p["anchor_btjd"] - self.anchor_btjd
        self.pm.per, self.pm.rp = p["period_d"], p["radius_ratio"]
        self.pm.a, self.pm.inc = p["a_over_rstar"], p["inclination_deg"]
        self.pm.u = limb_coefficients(p["limb_q1"], p["limb_q2"])
        contacts = circular_contacts(self.pm.per, self.pm.a, p["impact_parameter"], self.pm.rp)
        fluxes = [None] * len(self.events)
        for indices, _ in self.groups:
            t = np.concatenate([self.events[i]["t"] for i in indices]) - self.anchor_btjd
            width = self.events[indices[0]]["integration_d"]

            def evaluate(nodes):
                instant = batman.TransitModel(self.pm, nodes, supersample_factor=1, nthreads=1)
                return self.scenario["target_flux_fraction"] * (instant.light_curve(self.pm) - 1)

            values = panel_average(
                evaluate, t, width, self.pm.per, self.pm.t0, contacts, self.order
            )
            offset = 0
            for i in indices:
                n = len(self.events[i]["t"])
                fluxes[i] = values[offset : offset + n]
                offset += n
        return fluxes
