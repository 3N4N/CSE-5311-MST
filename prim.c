#include <stdio.h>
#include <limits.h>

void print_edges(int edges[][3], int n_edges)
{
  puts("S\tD\tW");
  for (int i = 0; i < n_edges; i++) {
    printf("%d\t%d\t%d\n", edges[i][0], edges[i][1], edges[i][2]);
  }
}

void prim(int edges[][3], int n_vertices, int n_edges, int root)
{
  int key[n_vertices];
  int parent[n_vertices];
  for (int i = 0; i < n_vertices; i++) {
    key[i] = INT_MAX;
    parent[i] = -1;
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

  return 0;
}
