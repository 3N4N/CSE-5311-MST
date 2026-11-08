#include <stdio.h>
#include <limits.h>
#include "priority_queue.h"

void print_edges(int edges[][3], int n_edges)
{
  puts("S\tD\tW");
  for (int i = 0; i < n_edges; i++) {
    printf("%d\t%d\t%d\n", edges[i][0], edges[i][1], edges[i][2]);
  }
}

void swap_int(int *x, int *y)
{
  int t = *x;
  *x = *y;
  *y = t;
}

int is_smaller(void *a, void *b)
{
  const Node *x = a;
  const Node *y = b;

  if (x->key < y->key) return 1;
  return 0;
}

void prim(int edges[][3], int n_vertices, int n_edges, int root)
{
  root -= 1;

  Node PQ[n_vertices];
  int PQ_size = n_vertices;
  for (int i = 0; i < n_vertices; i++) {
    PQ[i].id = i+1;
    PQ[i].key = INT_MAX;
    PQ[i].parent = -1;
  }
  PQ[root].key = 0;
  PQ[root].parent = 0;

  while(PQ_size > 0) {
    Node *u = PQ_pop((void **)&PQ, PQ_size--, &is_smaller);
  }

}

int main()
{
  int n_vertices, n_edges, root;

  FILE *fp = fopen("input.txt", "r");
  if (fp == NULL) {
    perror("Couldn't open file");
    return 1;
  }
  fscanf(fp, "%d %d %d", &n_vertices, &n_edges, &root);

  if (n_vertices < 0 || n_edges < 0) {
    perror("Unsupported #vertices or #edges");
    return 1;
  }
  if (root < 1 || root > n_vertices) {
    perror("root node out of bound");
    return 1;
  }

  int edges[n_edges][3];

  for (int i = 0; i < n_edges; i++) {
    fscanf(fp, "%d %d %d", &edges[i][0], &edges[i][1], &edges[i][2]);
  }
  fclose(fp);
  print_edges(edges, n_edges);

  prim(edges, n_vertices, n_edges, 1);

  // int x = 100, y = 200;
  // printf("%d %d\n", x, y);
  // swap_int(&x, &y);
  // printf("%d %d\n", x, y);

  return 0;
}
