#ifndef PRIORITY_QUEUE_H
#define PRIORITY_QUEUE_H

void swap_items(void **x, void **y);
void PQ_heapify(void **a, int n, int i, int (*comp)(void *, void *));
int PQ_pop(void **a, int n);

#endif  // PRIORITY_QUEUE_H
