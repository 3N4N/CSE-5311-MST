#!/usr/bin/env python3
"""Plot array storage for both Kruskal variants with descriptive trends."""

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/cse5311-matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
BLUE = "#2864dc"
GREEN = "#0b8f76"


def read_benchmark(filename):
    with (ROOT / filename).open(newline="", encoding="utf-8") as source:
        return {row["dataset"]: row for row in csv.DictReader(source)}


def main():
    vanilla = read_benchmark("benchmark.csv")
    radix = read_benchmark("radix_sort_benchmark.csv")
    if vanilla.keys() != radix.keys():
        raise ValueError("Benchmark CSVs must contain the same datasets")
    names = sorted(vanilla, key=lambda name: int(vanilla[name]["edges"]))
    edges = np.array([int(vanilla[name]["edges"]) for name in names])
    fig, ax = plt.subplots(figsize=(12, 6.2), dpi=200)
    legend = []
    for rows, label, color in ((vanilla, "Vanilla Kruskal", BLUE),
                               (radix, "Radix-sort Kruskal", GREEN)):
        # Use exact byte counts rather than rounded MiB CSV values.
        storage = np.array([int(rows[name]["allocated_space_bytes"])
                            for name in names], dtype=float) / 2**20
        if np.any(storage <= 0) or np.any(edges <= 0):
            raise ValueError("Logarithmic plots require positive values")
        # A descriptive least-squares fit in log-log space, across all inputs.
        # Actual array storage depends on V as well as E; this fit is not
        # a formula for allocation or an asymptotic complexity estimate.
        slope, intercept = np.polyfit(np.log10(edges), np.log10(storage), 1)
        fit_edges = np.geomspace(edges.min(), edges.max(), 250)
        fit_storage = 10 ** intercept * fit_edges ** slope
        for marker, select in (
            ("o", [not name.startswith("random_D") for name in names]),
            ("^", ["_V500000" in name for name in names]),
            ("s", ["_V1000000" in name for name in names]),
        ):
            ax.scatter(edges[select], storage[select], color=color, marker=marker,
                       s=65, edgecolors="white", linewidths=.8, zorder=3)
        ax.plot(fit_edges, fit_storage, color=color, linestyle="--",
                linewidth=2.6, zorder=2)
        legend.append(Line2D([], [], color=color, marker="o", linestyle="None",
                             markersize=7, label=f"{label} · measured"))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of edges E (log scale)", labelpad=10)
    ax.set_ylabel("Explicit array storage (MiB, log scale)", labelpad=10)
    ax.set_title("Kruskal memory versus graph size", loc="left", pad=16,
                 fontsize=16, weight="bold", color="#17243b")
    ax.grid(which="major", color="#dfe5ee", linewidth=.8)
    ax.grid(which="minor", color="#eef1f6", linewidth=.5)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    algorithm_legend = ax.legend(handles=legend, loc="upper left", frameon=False,
                                 fontsize=9)
    ax.add_artist(algorithm_legend)
    ax.legend(handles=[Line2D([], [], color="#68788d", marker=marker,
                             linestyle="None", markersize=7, label=label)
                       for marker, label in (("o", "Road graphs"),
                                             ("^", "Synthetic · 500k vertices"),
                                             ("s", "Synthetic · 1M vertices"))],
              loc="lower right", frameon=False, fontsize=9)
    fig.text(.5, .025,
             f"{len(names)} datasets · explicit arrays, not process RSS · "
             "dashed lines: descriptive log-log fits; storage depends on E and V",
             ha="center", fontsize=9, color="#52627a")
    fig.tight_layout(rect=(0, .055, 1, 1))
    destination = ROOT / "memory_comparison.png"
    fig.savefig(destination, facecolor="white")
    plt.close(fig)
    print(f"Generated {destination}")


if __name__ == "__main__":
    main()
