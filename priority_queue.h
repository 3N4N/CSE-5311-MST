#ifndef PRIORITY_QUEUE_H
#define PRIORITY_QUEUE_H

typedef struct {
  int id;
  int key;
  int parent;
} Node;

void swap_items(void **x, void **y);
void PQ_heapify(void **a, int n, int i, int (*)(void *, void *));
void* PQ_pop(void **a, int n, int (*comp)(void *, void *));

#endif  // PRIORITY_QUEUE_H
