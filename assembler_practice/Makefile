## Lothar Rubusch
## Simon Maurer
## Yosafat Praquive Triana
SRC = f
CC = gcc
FLAGS += -S -m32
RM = rm -f

all: $(SRC).s

$(SRC).s: $(SRC).c
	$(CC) $(FLAGS) $<
	$(CC) -O $(FLAGS) $< -o $(SRC).O.s

clean:
	$(RM) $(SRC).s $(SRC).O.s *~


.PHONY: clean all
