# Single-threaded Kruskal implementation

The `kruskal` executable uses union by rank, full path compression, and a
stable four-pass radix sort for signed 32-bit integer weights. It runs in one
thread. The CSV reader accepts integer weights written in decimal notation,
such as `5062.0`, and rejects fractional weights.

Build from the repository root:

```sh
make -C kruskal
```

Run the program on a dataset:

```sh
./kruskal/kruskal kruskal/USA-t.graph-undirected.csv
```

Run three benchmarks per dataset and save averages and individual runs:

```sh
python3 kruskal/benchmark.py --binary kruskal/kruskal --output kruskal/radix_sort_benchmark.csv
```

The benchmark runs all five datasets sequentially, in separate processes,
three times each. It checks every run's forest weight, component count,
selected-edge count, vertex count, and edge count against `benchmark.csv`.
Disconnected datasets produce minimum spanning forests.

The old `path_halving_benchmark.csv` and
`radix_sort_path_halving_benchmark.csv` files are retained as historical
measurements of earlier variants. The current implementation uses full path
compression.

## Measurement definitions

- Time is elapsed wall time measured using `CLOCK_MONOTONIC`, covering edge
  sorting and the Kruskal edge scan. Input parsing and disjoint-set
  initialization occur before timing starts. Radix buffer allocation and
  deallocation are included in sorting time.
- Space is peak explicit array storage, in bytes and MiB (1,048,576 bytes).
  It includes the edge list, parent array, rank array, radix edge buffer, and
  256-entry `size_t` histogram. This is not process peak RSS: allocator
  overhead and library buffers are excluded.
- Array sizes are deterministic for a dataset, so each of its three runs uses
  the same reported space; the CSV records their mean.

With this build's 12-byte edges, 4-byte parents, and 1-byte ranks, base array
storage is `12 * edges + 5 * vertices` bytes. For at least two edges, radix
sort adds `12 * edges + 256 * sizeof(size_t)` bytes at its peak.
