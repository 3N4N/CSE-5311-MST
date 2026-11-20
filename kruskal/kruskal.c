#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct {
    int u;
    int v;
    int weight;
} Edge;

typedef struct {
    int *parent;
    unsigned char *rank;
} DisjointSet;

_Static_assert(INT_MIN == INT32_MIN && INT_MAX == INT32_MAX,
               "Radix sort requires 32-bit int weights");

/* Stable LSD radix sort: four byte passes, with signed weights in order. */
static int radix_sort(Edge *edges, size_t count)
{
    if (count < 2) return 0;

    Edge *buffer = malloc(count * sizeof *buffer);
    if (buffer == NULL) return -1;

    Edge *source = edges;
    Edge *destination = buffer;
    size_t offsets[256];
    for (unsigned int shift = 0; shift < 32; shift += 8) {
        memset(offsets, 0, sizeof offsets);
        for (size_t i = 0; i < count; i++) {
            uint32_t key = (uint32_t)source[i].weight ^ UINT32_C(0x80000000);
            offsets[(key >> shift) & 255]++;
        }

        size_t position = 0;
        for (size_t bucket = 0; bucket < 256; bucket++) {
            size_t frequency = offsets[bucket];
            offsets[bucket] = position;
            position += frequency;
        }

        for (size_t i = 0; i < count; i++) {
            uint32_t key = (uint32_t)source[i].weight ^ UINT32_C(0x80000000);
            destination[offsets[(key >> shift) & 255]++] = source[i];
        }
        Edge *temporary = source;
        source = destination;
        destination = temporary;
    }
    /* Four swaps leave the sorted result in the original edges array. */
    free(buffer);
    return 0;
}
static int find_root(DisjointSet *set, int vertex)
{
    int root = vertex;
    while (set->parent[root] != root) root = set->parent[root];
    while (set->parent[vertex] != vertex) {
        int next = set->parent[vertex];
        set->parent[vertex] = root;
        vertex = next;
    }
    return root;
}

static int join_sets(DisjointSet *set, int a, int b)
{
    int root_a = find_root(set, a);
    int root_b = find_root(set, b);
    if (root_a == root_b) return 0;

    if (set->rank[root_a] < set->rank[root_b]) {
        set->parent[root_a] = root_b;
    } else if (set->rank[root_a] > set->rank[root_b]) {
        set->parent[root_b] = root_a;
    } else {
        set->parent[root_b] = root_a;
        set->rank[root_a]++;
    }
    return 1;
}

static double seconds_between(struct timespec start, struct timespec end)
{
    return (double)(end.tv_sec - start.tv_sec)
        + (double)(end.tv_nsec - start.tv_nsec) / 1000000000.0;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <edge-list.csv>\n", argv[0]);
        return 2;
    }

    FILE *input = fopen(argv[1], "r");
    if (input == NULL) {
        perror("Could not open input file");
        return 1;
    }

    int vertex_count, edge_count;
    if (fscanf(input, "%d,%d", &vertex_count, &edge_count) != 2
            || vertex_count < 0 || edge_count < 0) {
        fprintf(stderr, "Invalid graph header in %s\n", argv[1]);
        fclose(input);
        return 1;
    }

    Edge *edges = malloc((size_t)edge_count * sizeof *edges);
    int *parent = malloc((size_t)vertex_count * sizeof *parent);
    unsigned char *rank = calloc((size_t)vertex_count, sizeof *rank);
    if ((edge_count > 0 && edges == NULL)
            || (vertex_count > 0 && (parent == NULL || rank == NULL))) {
        perror("Could not allocate graph memory");
        fclose(input);
        free(edges);
        free(parent);
        free(rank);
        return 1;
    }

    for (int i = 0; i < edge_count; i++) {
        double weight;
        if (fscanf(input, "%d,%d,%lf", &edges[i].u, &edges[i].v,
                    &weight) != 3
                || edges[i].u < 0 || edges[i].u >= vertex_count
                || edges[i].v < 0 || edges[i].v >= vertex_count
                || !isfinite(weight) || weight < INT_MIN || weight > INT_MAX
                || weight != (double)(int)weight) {
            fprintf(stderr, "Invalid edge at row %d in %s\n", i + 2, argv[1]);
            fclose(input);
            free(edges);
            free(parent);
            free(rank);
            return 1;
        }
        edges[i].weight = (int)weight;
    }
    fclose(input);

    DisjointSet set = {parent, rank};
    for (int i = 0; i < vertex_count; i++) set.parent[i] = i;

    struct timespec start, finish;
    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) {
        perror("clock_gettime");
        free(edges);
        free(parent);
        free(rank);
        return 1;
    }

    if (radix_sort(edges, (size_t)edge_count) != 0) {
        perror("Could not allocate radix sort buffer");
        free(edges);
        free(parent);
        free(rank);
        return 1;
    }
    int components = vertex_count;
    int selected_edges = 0;
    int64_t total_weight = 0;
    for (int i = 0; i < edge_count && selected_edges < vertex_count - 1; i++) {
        if (join_sets(&set, edges[i].u, edges[i].v)) {
            selected_edges++;
            components--;
            total_weight += edges[i].weight;
        }
    }

    if (clock_gettime(CLOCK_MONOTONIC, &finish) != 0) {
        perror("clock_gettime");
        free(edges);
        free(parent);
        free(rank);
        return 1;
    }

    uint64_t allocated_bytes = (uint64_t)(size_t)edge_count * sizeof *edges
        + (uint64_t)(size_t)vertex_count * sizeof *parent
        + (uint64_t)(size_t)vertex_count * sizeof *rank;
    /* Count peak explicit array storage, including radix sort's workspace. */
    if (edge_count >= 2) {
        allocated_bytes += (uint64_t)(size_t)edge_count * sizeof *edges
            + 256 * sizeof(size_t);
    }
    printf("vertices=%d edges=%d selected_edges=%d components=%d ",
            vertex_count, edge_count, selected_edges, components);
    printf("total_weight=%" PRId64 " algorithm_seconds=%.9f allocated_bytes=%" PRIu64 "\n",
            total_weight, seconds_between(start, finish), allocated_bytes);

    free(edges);
    free(parent);
    free(rank);
    return 0;
}
