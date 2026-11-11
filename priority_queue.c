#include "priority_queue.h"
#include <stdio.h>

// void swap_items(void **x, void **y)
// {
//   void *t = *x;
//   *x = *y;
//   *y = t;
// }

void PQ_heapify(void **a, int n, int i,
    int (*cmp)(void *, void *),
    void (*swap_items)(void **, void **))
{
  int l = 2*i+1;
  int r = 2*i+2;
  int smallest = i;
  // puts("PQ_heapify: 1");
  if (l<n && cmp(a[l], a[smallest])) smallest = l;
  // puts("PQ_heapify: 2");
  if (r<n && cmp(a[r], a[smallest])) smallest = r;
  // puts("PQ_heapify: 3");
  if (smallest != i) {
    swap_items(&a[i], &a[smallest]);
    PQ_heapify(a, n, smallest, cmp, swap_items);
  }
}

void PQ_build(void **a, int n, int (*cmp)(void *, void *),
    void (*swap_items)(void **, void **))
{
  for (int i = n/2 - 1; i >= 0; i--) {
    PQ_heapify(a, n, i, cmp, swap_items);
  }
}

void PQ_decrease_key(void **a, int i,
    int (*cmp)(void *, void *),
    void (*swap_items)(void **, void **))
{
  while (i > 0 && cmp(a[i], a[(i-1)/2])) {
    swap_items(&a[i], &a[(i-1)/2]);
    i = (i-1)/2;
  }
}

void* PQ_pop(void **a, int n,
    int (*cmp)(void *, void *),
    void (*swap_items)(void **, void **))
{
  // puts("PQ_pop: 1");
  // printf("%p\n", ((Node*)a));
  // printf("%d: %d\n", ((Node *)a)[0].key, ((Node *)a)[0].parent);
  void* result = a[0];
  // printf("1 %d: %d\n", ((Node *) result)->key, ((Node *) result)->parent);
  swap_items(&a[0], &a[n-1]);
  // printf("%d: %d\n", ((Node *)a)[0].key, ((Node *)a)[0].parent);
  // puts("PQ_pop: 2");
  PQ_heapify(a, n-1, 0, cmp, swap_items);
  // puts("PQ_pop: 3");
  return result;
}
