import csv
import random
from pathlib import Path


# Configuration
OUTPUT_DIR = Path("data/synthetic2")
NODE_SIZES = [
    # 1_000,
    # 2_000,
    # 5_000,
    # 10_000,
    # 20_000,
    # 50_000,
    # 100_000,
    # 200_000,
    500_000,
    1_000_000,
]

WEIGHT_MIN = 1
WEIGHT_MAX = 1_000_000

SEED = 42


def generate_graph(num_nodes, target_edges, rng):
    """
    Generate a connected, undirected, simple weighted graph.

    Guarantees:
      - No self-loops.
      - No duplicate undirected edges.
      - Connected graph.
      - Exactly target_edges edges.
    """

    max_edges = num_nodes * (num_nodes - 1) // 2

    if target_edges < num_nodes - 1:
        raise ValueError("Not enough edges to guarantee connectivity.")

    if target_edges > max_edges:
        raise ValueError("Requested edge count exceeds simple graph limit.")

    edges = set()

    # Step 1: Generate a random spanning tree.
    # Each new vertex connects to an existing vertex.
    for v in range(1, num_nodes):
        u = rng.randrange(v)
        edges.add((u, v))

    # Step 2: Add random edges until target is reached.
    while len(edges) < target_edges:
        u = rng.randrange(num_nodes)
        v = rng.randrange(num_nodes)

        if u == v:
            continue

        # Canonical ordering prevents duplicate undirected edges.
        edge = (min(u, v), max(u, v))

        edges.add(edge)

    # Step 3: Assign random weights.
    weighted_edges = [
        (u, v, rng.randint(WEIGHT_MIN, WEIGHT_MAX))
        for u, v in edges
    ]

    rng.shuffle(weighted_edges)

    return weighted_edges


def save_graph(filepath, num_nodes, edges):
    """
    Save graph using:
        num_nodes,num_edges
        source,destination,weight
    """

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([num_nodes, len(edges)])
        writer.writerows(edges)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rng = random.Random(SEED)

    for num_nodes in NODE_SIZES:

        for degree_factor in (2, 4, 8, 16, 32):
            num_edges = degree_factor * num_nodes

            print(
                f"Generating V={num_nodes:,}, "
                f"E={num_edges:,}..."
            )

            edges = generate_graph(
                num_nodes,
                num_edges,
                rng
            )

            filename = (
                f"random_D{degree_factor}_V{num_nodes}.csv"
            )

            filepath = OUTPUT_DIR / filename

            save_graph(filepath, num_nodes, edges)

            print(f"Saved: {filepath}")

    print("\nAll graphs generated successfully.")


if __name__ == "__main__":
    main()
