#include "priority_queue.h"

void swap_items(void **x, void **y)
{
  void *t = *x;
  *x = *y;
  *y = t;
}

void PQ_heapify(void **a, int n, int i, int (*cmp)(void *, void *))
{
  int l = 2*i+1;
  int r = 2*i+2;
  int smallest = i;
  if (l<n && cmp(a[l], a[i])) smallest = l;
  if (r<n && cmp(a[r], a[i])) smallest = r;
  if (smallest != i) {
    swap_items(&a[i], &a[smallest]);
    PQ_heapify(a, n, smallest, cmp);
  }
}

// int PQ_pop(void **a, int n)
// {
//   int min = a[0]->key;
//   a[0] = a[n-1];
//   PQ_min_heapify(a, n-1, 0);
//   return min;
// }
