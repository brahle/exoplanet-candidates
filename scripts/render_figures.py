"""Render hash-bound saved plot vectors; no search, detrending or transit fit.

Standalone usage: python figure_render.py /path/to/evidence/figures
Requires NumPy and Matplotlib. Produces PNG overview and chronological event pages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def bins(x, y, width, lo, hi, minimum=2):
    """Display-only unweighted means; scatter/sqrt(N) is not calibrated uncertainty."""
    edges = np.arange(lo, hi + width * 0.5, width)
    groups = np.searchsorted(edges, x, side="right") - 1
    rows = []
    for i in range(len(edges) - 1):
        m = groups == i
        n = int(m.sum())
        if n >= minimum:
            rows.append(
                (
                    float(np.mean(x[m])),
                    float(np.mean(y[m])),
                    float(np.std(y[m], ddof=1) / np.sqrt(n)) if n > 1 else float("nan"),
                    n,
                )
            )
    return np.asarray(rows, float).reshape(-1, 4)


def read_payload(folder):
    meta = load(folder / "plot-context.json")
    if sha256_file(folder / "plot-data.npz") != meta["plot_data_sha256"]:
        raise ValueError("Plot vectors changed")
    with np.load(folder / "plot-data.npz", allow_pickle=False) as data:
        timelines, events = [], []
        for row in meta["timeline_rows"]:
            p = row["prefix"]
            timelines.append(
                {
                    "sector": row["sector"],
                    "author": row["author"],
                    "time": data[p + "_time"].copy(),
                    "flux": data[p + "_flux"].copy(),
                    "baselines": [
                        (
                            data[f"{p}_baseline_{i}_time"].copy(),
                            data[f"{p}_baseline_{i}_flux"].copy(),
                        )
                        for i in range(row["baselines"])
                    ],
                }
            )
        for row in meta["numeric_events"]:
            events.append(
                {k: row[k] for k in ("sector", "cycle", "center")}
                | {k: data[row["prefix"] + "_" + k].copy() for k in ("offset_h", "flux", "model")}
            )
        pg = (
            {k: data["periodogram_" + k].copy() for k in ("period", "power")}
            if "periodogram_period" in data
            else None
        )
    return {"metadata": meta, "timelines": timelines, "events": events, "periodogram": pg}


def gap_line(x, y, width):
    """Do not connect display means across missing bins."""
    breaks = np.flatnonzero(np.diff(x) > 1.7 * width) + 1
    return np.insert(x, breaks, np.nan), np.insert(y, breaks, np.nan)


def event_stack(ax, events, duration, width, half, title):
    all_flux = np.concatenate([r["flux"] for r in events])
    spacing = max(np.std(all_flux) * 3, np.ptp(np.percentile(all_flux, [10, 90])) * 1.5, 1e-5)
    for i, row in enumerate(events):
        ax.plot(row["offset_h"], row["flux"] - i * spacing, ".", color="#8594a9", alpha=0.18, ms=1)
        b = bins(row["offset_h"], row["flux"], max(width, 0.5), -half, half, minimum=1)
        if len(b):
            bx, by = gap_line(b[:, 0], b[:, 1] - i * spacing, max(width, 0.5))
            ax.plot(
                bx,
                by,
                ".-",
                color=plt.get_cmap("tab20")(i % 20),
                lw=0.8,
                ms=3,
            )
        ax.text(
            1.01,
            (1 - i * spacing),
            f"S{row['sector']} n={row['cycle']}\n{row['center']:.3f}",
            transform=ax.get_yaxis_transform(),
            va="center",
            fontsize=7,
        )
    ax.axvspan(-duration / 2, duration / 2, color="#d33c36", alpha=0.08)
    ax.set_ylim(
        float(np.min(all_flux)) - (len(events) - 1) * spacing - spacing / 2,
        float(np.max(all_flux)) + spacing / 2,
    )
    ax.set(
        xlim=(-half, half),
        xlabel="Hours from predicted midpoint",
        ylabel="Normalized flux + vertical offsets",
        title=title,
    )


def render(folder):
    payload = read_payload(folder)
    meta, events = payload["metadata"], payload["events"]
    if not events:
        raise ValueError("No saved numeric event profiles")
    ep = meta["ephemeris"]
    period, epoch, duration = [ep[k]["value"] for k in ("period_d", "epoch_btjd", "duration_h")]
    width = meta["display"]["bin_width_h"]
    half = min(4 * duration, period * 24 * 0.4)
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.grid": True,
            "grid.alpha": 0.2,
            "font.family": "DejaVu Sans",
        }
    )
    fig = plt.figure(figsize=(18, 14))
    grid = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1], hspace=0.42, wspace=0.32)
    rawax = fig.add_subplot(grid[0, :])
    ticks, labels, shift = [], [], 0.0
    segments = sorted(payload["timelines"], key=lambda s: s["time"][0])
    for i, segment in enumerate(segments):
        t, f = segment["time"], segment["flux"]
        x = t - t[0] + shift
        rawax.plot(
            x,
            f,
            ".",
            color="#8594a9",
            ms=1,
            alpha=0.35,
            label="Saved normalized cadences" if i == 0 else None,
        )
        for j, (bt, bf) in enumerate(segment["baselines"]):
            rawax.plot(
                bt - t[0] + shift,
                bf,
                color="#c94741",
                lw=1,
                label=meta["trend_label"] if i == 0 and j == 0 else None,
            )
        first, last = int(np.ceil((t[0] - epoch) / period)), int(np.floor((t[-1] - epoch) / period))
        for n in range(first, last + 1):
            rawax.axvline(
                epoch + n * period - t[0] + shift, color="#5677af", ls="--", lw=0.45, alpha=0.5
            )
        ticks.append(shift + (t[-1] - t[0]) / 2)
        labels.append(f"S{segment['sector']} {segment['author']}\n{t[0]:.0f}–{t[-1]:.0f}")
        shift += t[-1] - t[0] + 2
    rawax.set_xticks(ticks, labels, fontsize=8)
    rawax.set(
        ylabel="Normalized flux",
        xlabel="BTJD sector ranges; gaps between sectors compressed",
        title=f"{meta['candidate_id']} · provisional signal · P={period:.8f} d · "
        f"T0={epoch:.5f} BTJD (TDB)\n"
        "Saved light curves and baseline diagnostics; dashed lines = predicted midpoints",
    )
    rawax.legend(fontsize=9, loc="upper right")
    pgax = fig.add_subplot(grid[1, 0])
    pg = payload["periodogram"]
    if pg is None:
        pgax.text(0.5, 0.5, meta["periodogram"]["reason"], ha="center", transform=pgax.transAxes)
    else:
        pgax.plot(pg["period"], pg["power"], color="#3463ba", lw=0.65)
        for p, color, label in (
            (period, "#c94741", "Dossier P"),
            (period / 2, "#c99624", "P/2"),
            (period * 2, "#8594a9", "2P"),
        ):
            if pg["period"].min() <= p <= pg["period"].max():
                pgax.axvline(p, color=color, ls="--", lw=1, label=label)
        peak = int(np.argmax(pg["power"]))
        pgax.axvline(
            pg["period"][peak], color="#a53c37", lw=0.6, label=f"Peak {pg['period'][peak]:.5f} d"
        )
        pgax.legend(fontsize=8)
    sectors = ", ".join("S" + str(s) for s in meta["periodogram"].get("sectors", []))
    pgax.set(
        xlabel="Period [days]",
        ylabel="BLS likelihood power",
        title=f"{meta['periodogram'].get('title', 'Recorded BLS search')} · {sectors}\n"
        "Search clock/preprocessing scope differs from fold",
    )
    folded = fig.add_subplot(grid[1, 1])
    x = np.concatenate([r["offset_h"] for r in events])
    y = np.concatenate([r["flux"] for r in events])
    folded.plot(x, y, ".", ms=1.5, alpha=0.25, color="#8594a9", label="Saved event cadences")
    b = bins(x, y, width, -half, half)
    if len(b):
        folded.errorbar(
            b[:, 0],
            b[:, 1],
            b[:, 2],
            fmt="o",
            color="#15263b",
            ms=3,
            lw=0.7,
            label=f"Means ({width * 60:.1f} min); white SE",
        )
    modeled = [r for r in events if len(r["model"]) == len(r["offset_h"])]
    if modeled:
        mb = bins(
            np.concatenate([r["offset_h"] for r in modeled]),
            np.concatenate([r["model"] for r in modeled]),
            width,
            -half,
            half,
        )
        folded.plot(
            mb[:, 0], mb[:, 1], "-", color="#c94741", lw=2, label="Mean saved profile models"
        )
    if len(b):
        lo, hi = np.min(b[:, 1] - 2 * b[:, 2]), np.max(b[:, 1] + 2 * b[:, 2])
        margin = max((hi - lo) * 0.25, 1e-5)
        folded.set_ylim(lo - margin, hi + margin)
        clipped = int(np.sum((y < lo - margin) | (y > hi + margin)))
        folded.text(
            0.02,
            0.95,
            f"Zoom: {clipped} raw points off-scale",
            fontsize=8,
            va="top",
            transform=folded.transAxes,
        )
    folded.set(
        xlim=(-half, half),
        xlabel="Hours from predicted midpoint",
        ylabel="Baseline-corrected flux",
        title=f"Folded signed profiles · {len(events)} events\n"
        f"Duration {duration:.2f} ± {ep['duration_h']['error']:.2f} h (conditional)",
    )
    folded.legend(fontsize=8, loc="lower right")
    parity = fig.add_subplot(grid[2, 0])
    for remainder, color, label, marker in (
        (1, "#3463ba", "Odd cycles", "o"),
        (0, "#d18428", "Even cycles", "s"),
    ):
        rows = [r for r in events if r["cycle"] % 2 == remainder]
        if rows:
            b = bins(
                np.concatenate([r["offset_h"] for r in rows]),
                np.concatenate([r["flux"] for r in rows]),
                width,
                -half,
                half,
            )
            if len(b):
                parity.errorbar(
                    b[:, 0],
                    b[:, 1],
                    b[:, 2],
                    fmt=marker + "-",
                    color=color,
                    ms=3,
                    lw=0.7,
                    label=f"{label} ({len(rows)} events)",
                )
    parity.set(
        xlim=(-half, half),
        xlabel="Hours from predicted midpoint",
        ylabel="Baseline-corrected flux",
        title="Odd / even comparison\nDisplay-bin white SE; no classification inferred",
    )
    parity.legend(fontsize=8)
    stack = fig.add_subplot(grid[2, 1])
    event_stack(
        stack,
        events[:12],
        duration,
        width,
        half,
        f"Individual events · first {min(12, len(events))} / {len(events)} chronological\n"
        "All profiles in event pages; failures in context",
    )
    counts = meta["event_outcome_counts"]
    fig.text(
        0.06,
        0.025,
        textwrap.fill(meta["method"], 140)
        + "\n"
        + " | ".join(f"{k}: {v}" for k, v in counts.items())
        + "\n"
        + meta["limits"][0]
        + " Bin errors and duration errors are conditional; no planet probability.",
        fontsize=9,
    )
    fig.subplots_adjust(left=0.065, right=0.91, top=0.95, bottom=0.1)
    fig.savefig(folder / "diagnostic.png", dpi=meta["display"]["dpi"])
    plt.close(fig)
    images = ["diagnostic.png"]
    if len(events) > 12:
        for page, start in enumerate(range(0, len(events), 24), 1):
            fig, ax = plt.subplots(figsize=(12, 12))
            event_stack(
                ax,
                events[start : start + 24],
                duration,
                width,
                half,
                f"{meta['candidate_id']} · events {start + 1}–"
                f"{min(start + 24, len(events))} / {len(events)}",
            )
            fig.subplots_adjust(left=0.1, right=0.8, top=0.94, bottom=0.09)
            fig.text(
                0.1,
                0.035,
                "All saved numeric profiles, chronological; missing bins remain gaps.\n"
                "Vertical offsets only; negative depths retained. BTJD (TDB) labels at right.",
                fontsize=9,
            )
            name = f"events-{page:02d}.png"
            fig.savefig(folder / name, dpi=meta["display"]["dpi"])
            plt.close(fig)
            images.append(name)
    return images


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    for image in render(args.folder):
        print(image)


if __name__ == "__main__":
    main()
