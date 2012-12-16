RTFLAGS = 
# RTFLAGS = -DTAGGING

CC = gcc
CFLAGS = -m32 $(RTFLAGS)

# debugging support
# CFLAGS = -g -m32 $(RTFLAGS)

RUNTIME = hashtable.o hashtable_itr.o hashtable_utility.o runtime.o -lm

# GC = gc/lib/libgc.a

runtime: $(RUNTIME)
	@true

test: test1 test2 test3 test4 test5

test1: $(RUNTIME) test1.o
	@$(CC) $(CFLAGS) -o test1 $(RUNTIME) test1.o $(GC)
	@./test1 > test1.out
	@if cmp test1.out test1.expected; then echo test1 ok ; else echo test1 failed ; fi

test2: $(RUNTIME) test2.o
	@$(CC) $(CFLAGS) -o test2 $(RUNTIME) test2.o $(GC)
	@echo 1 | ./test2 > test2.out
	@if cmp test2.out test2.expected; then echo test2 ok ; else echo test2 failed ; fi

test3: $(RUNTIME) test3.o
	@$(CC) $(CFLAGS) -o test3 $(RUNTIME) test3.o $(GC)
	@echo 1 | ./test3 > test3.out
	@if cmp test3.out test3.expected; then echo test3 ok ; else echo test3 failed ; fi

test4: $(RUNTIME) test4.o
	@$(CC) $(CFLAGS) -o test4 $(RUNTIME) test4.o $(GC)
	@./test4 > test4.out
	@if cmp test4.out test4.expected; then echo test4 ok ; else echo test4 failed ; fi

test5: $(RUNTIME) test5.o
	@$(CC) $(CFLAGS) -o test5 $(RUNTIME) test5.o $(GC)
	@./test5 > test5.out
	@if cmp test5.out test5.expected; then echo test5 ok ; else echo test5 failed ; fi

retest: test-clean test

test-clean:
	-rm -f test*.o
	-rm -f test*.out
	-rm -f test[0-9] test[0-9][0-9] test[0-9][0-9][0-9]

clean: test-clean
	-rm -f hashtable.o hashtable_itr.o hashtable_utility.o runtime.o
	-rm -rf *.dSYM

.c.o:
	$(CC) $(CFLAGS) -c $< -o $@
