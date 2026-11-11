#ifndef PRIORITY_QUEUE_H
#define PRIORITY_QUEUE_H

void swap_items(void **x, void **y);
void PQ_heapify(void **a, int n, int i, int (*)(void *, void *), void (*)(void **, void **));
void PQ_build(void **a, int n, int (*cmp)(void *, void *), void (*)(void **, void **));
void PQ_decrease_key(void **a, int i, int (*cmp)(void *, void *), void (*)(void **, void **));
void* PQ_pop(void **a, int n, int (*comp)(void *, void *), void (*)(void **, void **));

#endif  // PRIORITY_QUEUE_H
