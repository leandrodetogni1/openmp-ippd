#!/bin/bash
set -e

RUNS=3                    
SEED=42                       

N_VALUES=(100000 500000 1000000)
K_VALUES=(20 24 28)
B_VALUES=(32 256 4096)
THREADS=(1 2 4 8 16)
CHUNKS=(1 4 16 64)

BIN="bin"
RESULTS="results"

CSV_A="$RESULTS/task-a.csv"
CSV_B="$RESULTS/task-b.csv"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Trabalho Prático de OpenMP ${NC}"

if [ ! -f "$BIN/task-a-seq" ] || [ ! -f "$BIN/task-a-omp" ] || \
   [ ! -f "$BIN/task-b-seq" ] || [ ! -f "$BIN/task-b-omp" ]; then
    echo -e "${YELLOW}Compilando...${NC}"
    make all
fi

mkdir -p "$RESULTS"

echo -e "\n${YELLOW}TAREFA A${NC}"

echo "task,variant,schedule,chunk,N,K,threads,run,time,checksum" > "$CSV_A"

echo -e "${GREEN}Executando versão sequencial...${NC}"
for N in "${N_VALUES[@]}"; do
    for K in "${K_VALUES[@]}"; do
        echo -n "  N=$N, K=$K: "
        for run in $(seq 1 $RUNS); do
            result=$($BIN/task-a-seq $N $K)
            time=$(echo "$result" | cut -d',' -f8)
            checksum=$(echo "$result" | cut -d',' -f9)
            echo "A,seq,none,0,$N,$K,1,$run,$time,$checksum" >> "$CSV_A"
            echo -n "."
        done
        echo " OK"
    done
done

echo -e "${GREEN}Executando versões paralelas...${NC}"
for N in "${N_VALUES[@]}"; do
    for K in "${K_VALUES[@]}"; do
        for t in "${THREADS[@]}"; do
            echo -n "  N=$N, K=$K, threads=$t, static: "
            for run in $(seq 1 $RUNS); do
                result=$($BIN/task-a-omp $N $K 1 0 $t)
                time=$(echo "$result" | cut -d',' -f8)
                checksum=$(echo "$result" | cut -d',' -f9)
                echo "A,omp,static,0,$N,$K,$t,$run,$time,$checksum" >> "$CSV_A"
                echo -n "."
            done
            echo " OK"

            for chunk in "${CHUNKS[@]}"; do
                echo -n "  N=$N, K=$K, threads=$t, dynamic,$chunk: "
                for run in $(seq 1 $RUNS); do
                    result=$($BIN/task-a-omp $N $K 2 $chunk $t)
                    time=$(echo "$result" | cut -d',' -f8)
                    checksum=$(echo "$result" | cut -d',' -f9)
                    echo "A,omp,dynamic,$chunk,$N,$K,$t,$run,$time,$checksum" >> "$CSV_A"
                    echo -n "."
                done
                echo " OK"
            done

            for chunk in "${CHUNKS[@]}"; do
                echo -n "  N=$N, K=$K, threads=$t, guided,$chunk: "
                for run in $(seq 1 $RUNS); do
                    result=$($BIN/task-a-omp $N $K 3 $chunk $t)
                    time=$(echo "$result" | cut -d',' -f8)
                    checksum=$(echo "$result" | cut -d',' -f9)
                    echo "A,omp,guided,$chunk,$N,$K,$t,$run,$time,$checksum" >> "$CSV_A"
                    echo -n "."
                done
                echo " OK"
            done
        done
    done
done

echo -e "\n${YELLOW}TAREFA B${NC}"

echo "task,variant,N,B,threads,run,time,checksum" > "$CSV_B"

echo -e "${GREEN}Executando versão sequencial...${NC}"
for N in "${N_VALUES[@]}"; do
    for B in "${B_VALUES[@]}"; do
        echo -n "  N=$N, B=$B: "
        for run in $(seq 1 $RUNS); do
            result=$($BIN/task-b-seq $N $B $SEED)
            time=$(echo "$result" | cut -d',' -f6)
            checksum=$(echo "$result" | cut -d',' -f7)
            echo "B,seq,$N,$B,1,$run,$time,$checksum" >> "$CSV_B"
            echo -n "."
        done
        echo " OK"
    done
done

echo -e "${GREEN}Executando versões paralelas...${NC}"

VARIANTS=("critical" "atomic" "local")

for N in "${N_VALUES[@]}"; do
    for B in "${B_VALUES[@]}"; do
        for t in "${THREADS[@]}"; do
            for v in 1 2 3; do
                vname=${VARIANTS[$((v-1))]}
                echo -n "  N=$N, B=$B, threads=$t, $vname: "
                for run in $(seq 1 $RUNS); do
                    result=$($BIN/task-b-omp $N $B $v $t $SEED)
                    time=$(echo "$result" | cut -d',' -f6)
                    checksum=$(echo "$result" | cut -d',' -f7)
                    echo "B,$vname,$N,$B,$t,$run,$time,$checksum" >> "$CSV_B"
                    echo -n "."
                done
                echo " OK"
            done
        done
    done
done

echo -e "Concluido e resultados salvos"
