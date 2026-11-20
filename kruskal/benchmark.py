#!/usr/bin/env python3
"""Run each dataset three times, check forest results, and save averages."""

import argparse
import csv
from decimal import Decimal
from pathlib import Path
import subprocess


def main():
    folder = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path,
                        help="expected graph/results CSV (defaults to benchmark.csv)")
    args = parser.parse_args()
    binary = args.binary.resolve()

    baseline_path = args.baseline.resolve() if args.baseline else folder / "benchmark.csv"
    with baseline_path.open(newline="") as source:
        baseline = list(csv.DictReader(source))

    fields = list(baseline[0])
    raw_path = args.output.with_name(args.output.stem + "_runs.csv")
    raw_fields = ["dataset", "run", "vertices", "edges", "selected_edges",
                  "components", "total_weight", "algorithm_seconds",
                  "allocated_bytes"]
    with args.output.open("w", newline="") as average_file, \
            raw_path.open("w", newline="") as raw_file:
        averages = csv.DictWriter(average_file, fieldnames=fields)
        raw = csv.DictWriter(raw_file, fieldnames=raw_fields)
        averages.writeheader()
        raw.writeheader()
        for expected in baseline:
            name = expected["dataset"]
            if name.startswith("random_D"):
                dataset = folder.parent / "data" / "synthetic2" / name
            elif name == "USA-t.graph-undirected.csv":
                dataset = folder / name
            else:
                dataset = folder.parent / "data" / "dimacs9" / name
            samples = []
            for run in range(1, 4):
                result = subprocess.run([str(binary), str(dataset)],
                                        text=True, capture_output=True, check=True)
                values = dict(item.split("=", 1)
                              for item in result.stdout.split())
                for actual, reference in [("vertices", "vertices"),
                                          ("edges", "edges"),
                                          ("selected_edges", "forest_edges"),
                                          ("components", "components"),
                                          ("total_weight", "forest_weight")]:
                    if values[actual] != expected[reference]:
                        raise RuntimeError(f"{name}, run {run}: {actual} differs "
                                           "from baseline")
                if samples and values["allocated_bytes"] != samples[0]["allocated_bytes"]:
                    raise RuntimeError(f"{name}: inconsistent allocation sizes")
                samples.append(values)
                raw.writerow({"dataset": name, "run": run, **values})
                raw_file.flush()
                print(f"{name} run={run} {result.stdout.strip()}", flush=True)

            seconds = sum(Decimal(s["algorithm_seconds"]) for s in samples) / 3
            space = sum(Decimal(s["allocated_bytes"]) for s in samples) / 3
            row = dict(expected)
            row.update(runs=3, average_algorithm_time_seconds=f"{seconds:.9f}",
                       allocated_space_bytes=f"{space:.0f}",
                       allocated_space_mib=f"{space / (1024 * 1024):.3f}")
            averages.writerow(row)
            average_file.flush()


if __name__ == "__main__":
    main()
