#!/usr/bin/env python3
"""Create runtime speedup and memory overhead bars for all benchmark inputs."""

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/cse5311-matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
GREEN = "#0b8f76"
INK = "#17243b"


def read_rows(filename):
    with (ROOT / filename).open(newline="", encoding="utf-8") as source:
        return {row["dataset"]: row for row in csv.DictReader(source)}


def label(name):
    if name == "USA-t.graph-undirected.csv":
        return "USA-t"
    if name.startswith("USA-road-d."):
        return name.removeprefix("USA-road-d.").removesuffix(".gr-undirected.csv")
    _, density, vertices = name.removesuffix(".csv").split("_")
    count = int(vertices[1:])
    return f"Synthetic {density} · {count:,} V"


def draw_bars(names, values, title, xlabel, filename):
    fig, ax = plt.subplots(figsize=(12, 8.7), dpi=200)
    bars = ax.barh([label(name) for name in names], values, color=GREEN, height=.62)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.17)
    ax.set_xlabel(xlabel, labelpad=12, color=INK)
    ax.set_title(title, loc="left", fontsize=15, weight="bold", color=INK, pad=15)
    ax.grid(axis="x", color="#dfe5ee", linewidth=.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#dfe5ee")
    ax.tick_params(axis="both", labelcolor="#52627a")
    ax.tick_params(axis="y", length=0, pad=8, labelsize=9)
    for bar, value in zip(bars, values):
        ax.text(value + max(values) * .012, bar.get_y() + bar.get_height() / 2,
                f"{value:.2f}×", va="center", weight="bold", fontsize=9, color=INK)
    # Separate the original road inputs from the synthetic inputs.
    road_count = sum(not name.startswith("random_D") for name in names)
    if 0 < road_count < len(names):
        ax.axhline(road_count - .5, color="#dfe5ee", linewidth=1)
    fig.tight_layout()
    destination = ROOT / filename
    fig.savefig(destination, facecolor="white")
    plt.close(fig)
    print(f"Generated {destination} ({len(names)} datasets)")


def main():
    vanilla = read_rows("benchmark.csv")
    radix = read_rows("radix_sort_benchmark.csv")
    if vanilla.keys() != radix.keys():
        raise ValueError("Benchmark files must contain the same datasets")
    roads = [name for name in vanilla if not name.startswith("random_D")]
    synthetic = sorted(
        (name for name in vanilla if name.startswith("random_D")),
        key=lambda name: (int(name.split("_")[1][1:]), int(vanilla[name]["vertices"])),
    )
    names = roads + synthetic
    speedups = []
    memory_ratios = []
    for name in names:
        for field in ("vertices", "edges", "forest_weight", "components"):
            if vanilla[name][field] != radix[name][field]:
                raise ValueError(f"Mismatched {field}: {name}")
        speedups.append(float(vanilla[name]["average_algorithm_time_seconds"])
                        / float(radix[name]["average_algorithm_time_seconds"]))
        memory_ratios.append(int(radix[name]["allocated_space_bytes"])
                             / int(vanilla[name]["allocated_space_bytes"]))
    draw_bars(names, speedups, "Runtime speedup · all 15 datasets",
              "Vanilla time ÷ radix time (higher is faster)", "speedup_comparison.png")
    draw_bars(names, memory_ratios, "Memory overhead · all 15 datasets",
              "Radix array storage ÷ vanilla array storage (higher uses more memory)",
              "memory_ratio_comparison.png")


if __name__ == "__main__":
    main()
