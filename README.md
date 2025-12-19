# Trabalho Prático - OpenMP

| Nome             | Responsabilidade |
| ---------------- | ---------------- |
| Leandro De Togni | Tarefa A         |
| Fernando Penedo  | Tarefa B         |

### Comandos

```bash
# Compilar tudo
make all

# Compilar versão sequencial
make seq

# Compilar versão OpenMP
make omp

# Limpar
make clean
```

```bash
# Executa todos os experimentos e salva CSVs
make run
# ou
./run.sh
```

#### Tarefa A

```bash
# Versão sequencial
./bin/task-a-seq <N> <K>

# Versão OpenMP
./bin/task-a-omp <N> <K> <variante> <chunk> <threads>

# Exemplo:
./bin/task-a-seq 100000 20
./bin/task-a-omp 100000 20 2 16 4
```

#### Tarefa B

```bash
# Versão sequencial
./bin/task-b-seq <N> <B> [seed]

# Versão OpenMP
./bin/task-b-omp <N> <B> <variante> <threads> [seed]

# Exemplo:
./bin/task-b-seq 1000000 256 42
./bin/task-b-omp 1000000 256 3 8 42
```

## Gerar os gráficos

```bash
make plot

# ou
python3 plot.py
```

## Parâmetros

| Parâmetro                 | Valores                     |
| ------------------------- | --------------------------- |
| N (tamanho do array)      | 100.000, 500.000, 1.000.000 |
| K (Fibonacci máximo)      | 20, 24, 28                  |
| B (buckets do histograma) | 32, 256, 4.096              |
| Threads                   | 1, 2, 4, 8, 16              |
| Chunks (dynamic/guided)   | 1, 4, 16, 64                |
| Repetições por ponto      | 5                           |
