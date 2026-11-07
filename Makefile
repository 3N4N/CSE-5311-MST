CC = gcc

EXE = prim

all: prim

prim: prim.c
	$(CC) -o prim prim.c

clean:
	rm -rf $(EXE)
