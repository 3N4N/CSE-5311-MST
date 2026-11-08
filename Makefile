CC = gcc

SRCS   = $(wildcard *.c)
OBJS   = $(patsubst %.c,%.o,$(SRCS))
DEPS   = $(OBJS:.o:=.d)

all: prim

prim: prim.o priority_queue.o
	$(CC) -o $@ $^

%.o: %.c
	$(CC) -o $@ $(CFLAGS) -c $<

%.o: %.c %.h
	$(CC) -o $@ $(CFLAGS) -c $<

run: prim
	./prim

clean:
	rm -rf prim *.o
