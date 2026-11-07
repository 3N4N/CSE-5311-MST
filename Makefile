CC = gcc

EXE = prim

all: prim

prim: prim.c
	$(CC) -o prim prim.c

run: prim
	./prim

clean:
	rm -rf $(EXE)
