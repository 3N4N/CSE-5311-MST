CC = gcc

SRCS   = $(wildcard *.c)
OBJS   = $(patsubst %.c,%.o,$(SRCS))
DEPS   = $(OBJS:.o:=.d)

all: prim

prim: prim.o priority_queue.o
	$(CC) -o $@ $^

%.o: %.c
	$(CC) -g -o $@ $(CFLAGS) -c $<

%.o: %.c %.h
	$(CC) -g -o $@ $(CFLAGS) -c $<

run: prim
	./prim

clean:
	rm -rf prim *.o
