CC = gcc
CFLAGS = -O2 -Wall -Wextra -std=c11

all: kruskal

kruskal: kruskal.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f kruskal kruskal_path_halving

.PHONY: all clean
