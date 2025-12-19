
# se for rodar no mac, trocar por gcc-15 ao inves de gcc
CC = gcc-15

# flags para habilitar os warnings e mostrar bugs, e a -02 é para otimizações
CFLAGS = -Wall -Wextra -O2
OMP_FLAGS = -fopenmp

SRC_SEQ = src/seq
SRC_OMP = src/omp
BIN = bin

SEQ_TARGETS = $(BIN)/task-a-seq $(BIN)/task-b-seq
OMP_TARGETS = $(BIN)/task-a-omp $(BIN)/task-b-omp

.PHONY: all seq omp clean run plot help

all: seq omp

$(BIN):
	mkdir -p $(BIN)

seq: $(SEQ_TARGETS)

$(BIN)/task-a-seq: $(SRC_SEQ)/task-a.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $<

$(BIN)/task-b-seq: $(SRC_SEQ)/task-b.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $<

omp: $(OMP_TARGETS)

$(BIN)/task-a-omp: $(SRC_OMP)/task-a.c | $(BIN)
	$(CC) $(CFLAGS) $(OMP_FLAGS) -o $@ $<

$(BIN)/task-b-omp: $(SRC_OMP)/task-b.c | $(BIN)
	$(CC) $(CFLAGS) $(OMP_FLAGS) -o $@ $<

run: all
	@echo "Rodando código"
	@chmod +x run.sh
	@./run.sh

plot:
	@echo "Gerando gráficos"
	@python3 plot.py
