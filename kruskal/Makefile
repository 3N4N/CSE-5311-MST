CC = gcc
CFLAGS = -O2 -Wall -Wextra -std=c11

all: kruskal kruskal_vanilla

kruskal: kruskal.c
	$(CC) $(CFLAGS) -o $@ $<

kruskal_vanilla: kruskal.c
	$(CC) $(CFLAGS) -DVANILLA_SORT -o $@ $<

clean:
	rm -f kruskal kruskal_vanilla kruskal_path_halving

.PHONY: all clean
