#include <stdio.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>
#include "node.h"
#include "priority_queue.h"

# define FILE_PATH_MAXLEN 1024

void print_edges(int edges[][3], int n_edges)
{
  puts("S\tD\tW");
  for (int i = 0; i < n_edges; i++) {
    printf("%d\t%d\t%d\n", edges[i][0], edges[i][1], edges[i][2]);
  }
}

void swap_nodes(void **a, void **b)
{
  void *t = *a; *a = *b; *b = t;
  Node *x = *a;
  Node *y = *b;
  int t_pos = x->pos;
  x->pos = y->pos;
  y->pos = t_pos;
}

int is_smaller(void *a, void *b)
{
  const Node *x = a;
  const Node *y = b;

  if (x->key < y->key) return 1;
  return 0;
}

void print_mst(Node nodes[], int n_vertices, int root, int print_edges) {
  long long total = 0;
  puts("\nMST edges:");
  puts("S\tD\tW");
  for (int i = 0; i < n_vertices; i++) {
    if (i == root) continue;
    if (nodes[i].parent == -1) {
      if (print_edges)
        printf("vertex %d is unreachable\n", nodes[i].id);
      continue;
    }
    if (print_edges)
      printf("%d\t%d\t%d\n", nodes[i].parent, nodes[i].id, nodes[i].key);
    total += nodes[i].key;
  }
  printf("Total weight: %lld\n", total);
}

// Edge (u, v, w) was found from the popped vertex u: if it is a cheaper way
// to reach v, update v's key and parent and move v up in the heap.
static void relax(Node *nodes, Node **PQ, int PQ_size, int *in_pq,
    int u, int v, int w, int use_pos)
{
  if (in_pq[v] && w < nodes[v].key) {
    nodes[v].key = w;
    nodes[v].parent = u;

    if (use_pos) {
      PQ_decrease_key((void **)PQ, nodes[v].pos, &is_smaller, &swap_nodes);
    } else {
      for (int j = 0; j < PQ_size; j++) {
        if (PQ[j] == &nodes[v]) {
          PQ_decrease_key((void **)PQ, j, &is_smaller, &swap_nodes);
          break;
        }
      }
    }
  }
}

// Node ids run from 0 to n_vertices-1; the node with id x is nodes[x].
// use_adj: 1 = find neighbors with an adjacency list, 0 = scan all edges.
void prim(int edges[][3], int n_vertices, int n_edges, int root, int use_pos, int use_adj)
{
  Node *nodes = malloc(n_vertices * sizeof *nodes);
  Node **PQ = malloc(n_vertices * sizeof *PQ);
  int *in_pq = malloc(n_vertices * sizeof *in_pq);
  if (nodes == NULL || PQ == NULL || in_pq == NULL) {
    perror("Couldn't allocate memory for prim");
    exit(1);
  }
  int PQ_size = n_vertices;
  for (int i = 0; i < n_vertices; i++) {
    nodes[i].id = i;
    nodes[i].key = INT_MAX;
    nodes[i].parent = -1;
    nodes[i].pos = i;
    PQ[i] = &nodes[i];
    in_pq[i] = 1;
  }
  nodes[root].key = 0;
  PQ_build((void **)PQ, PQ_size, &is_smaller, &swap_nodes);

  int *adj_start = NULL, *adj_to = NULL, *adj_w = NULL;
  if (use_adj) {
    adj_start = calloc(n_vertices + 1, sizeof *adj_start);
    adj_to = malloc(2 * (size_t)n_edges * sizeof *adj_to);
    adj_w = malloc(2 * (size_t)n_edges * sizeof *adj_w);
    if (adj_start == NULL || adj_to == NULL || adj_w == NULL) {
      perror("Couldn't allocate memory for adjacency list");
      exit(1);
    }
    for (int i = 0; i < n_edges; i++) {
      adj_start[edges[i][0] + 1]++;
      adj_start[edges[i][1] + 1]++;
    }
    for (int u = 0; u < n_vertices; u++) {
      adj_start[u+1] += adj_start[u];
    }
    for (int i = 0; i < n_edges; i++) {
      int a = edges[i][0], b = edges[i][1], w = edges[i][2];
      int k = adj_start[a]++;
      adj_to[k] = b; adj_w[k] = w;
      k = adj_start[b]++;
      adj_to[k] = a; adj_w[k] = w;
    }
    // undo the shift
    for (int u = n_vertices; u > 0; u--) {
      adj_start[u] = adj_start[u-1];
    }
    adj_start[0] = 0;
  }

  while(PQ_size > 0) {
    Node *u = PQ_pop((void **)PQ, PQ_size--, &is_smaller, &swap_nodes);
    in_pq[u->id] = 0;
    if (u->key == INT_MAX) continue;  // unreachable from root

    if (use_adj) {
      for (int k = adj_start[u->id]; k < adj_start[u->id + 1]; k++) {
        relax(nodes, PQ, PQ_size, in_pq, u->id, adj_to[k], adj_w[k], use_pos);
      }
    } else {
      for (int i = 0; i < n_edges; i++) {
        int v;
        if (edges[i][0] == u->id)       v = edges[i][1];
        else if (edges[i][1] == u->id)  v = edges[i][0];
        else continue;
        relax(nodes, PQ, PQ_size, in_pq, u->id, v, edges[i][2], use_pos);
      }
    }
  }

  print_mst(nodes, n_vertices, root, 0);

  free(nodes);
  free(PQ);
  free(in_pq);
  free(adj_start);
  free(adj_to);
  free(adj_w);
}

int main(int argc, char* argv[])
{
  int n_vertices, n_edges, root, use_pos, use_adj, graph_unweighted;

  use_pos = argc > 1 ? *argv[1] - '0' : 1;
  graph_unweighted = 0; // argc > 2 ? *argv[2] - '0' : 0;
  use_adj = argc > 3 ? *argv[3] - '0' : 1;
  printf("Use Pos? %d\n", use_pos);
  printf("Use adjacency list? %d\n", use_adj);
  printf("Unweighted? %d\n", graph_unweighted);

  char filepath[FILE_PATH_MAXLEN];
  if (argc > 2) {
    strncpy(filepath, argv[2], FILE_PATH_MAXLEN);
  } else {
    strncpy(filepath, "./data/graph.txt", sizeof(filepath) - 1);
  }
  printf("Input graph: %s\n", filepath);
  // return 0;

  FILE *fp = fopen(filepath, "r");
  if (fp == NULL) {
    perror("Couldn't open file");
    return 1;
  }
  fscanf(fp, "%d,%d", &n_vertices, &n_edges);
  printf("%d,%d\n", n_vertices, n_edges);

  if (n_vertices < 0 || n_edges < 0) {
    perror("Unsupported #vertices or #edges");
    return 1;
  }

  int (*edges)[3] = malloc(n_edges * sizeof *edges);
  if (edges == NULL) {
    perror("Couldn't allocate memory for edges");
    return 1;
  }
  // return 0;

  if (graph_unweighted) {
    srand(7796);
    for (int i = 0; i < n_edges; i++) {
      fscanf(fp, "%d,%d", &edges[i][0], &edges[i][1]);
      edges[i][2] = rand() % 100;
      // printf("%d,%d,%d\n", edges[i][0], edges[i][1], edges[i][2]);
    }
  } else {
    for (int i = 0; i < n_edges; i++) {
      fscanf(fp, "%d,%d,%d", &edges[i][0], &edges[i][1], &edges[i][2]);
      // printf("%d,%d,%d\n", edges[i][0], edges[i][1], edges[i][2]);
    }
  }

  fclose(fp);

  root = 0;
  if (root < 0 || root >= n_vertices) {
    fprintf(stderr, "root node out of bound\n");
    return 1;
  }

  prim(edges, n_vertices, n_edges, root, use_pos, use_adj);
  // print_edges(edges, n_edges);

  free(edges);
  return 0;
}
