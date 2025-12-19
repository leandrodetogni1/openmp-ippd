# Reproducibilidade

## Versão do compilador

Foi utilizado a versão 15.2.0 do compilador

## Flags

```makefile
CC = gcc
CFLAGS = -Wall -Wextra -O2
OMP_FLAGS = -fopenmp
```

## Parâmetros dos Experimentos

| Parâmetro          | Valores                     |
| ------------------ | --------------------------- |
| N                  | 100.000, 500.000, 1.000.000 |
| K                  | 20, 24, 28                  |
| B                  | 32, 256, 4.096              |
| Threads            | 1, 2, 4, 8, 16              |
| Chunks             | 1, 4, 16, 64                |
| Repetições         | 5                           |
| Semente (Tarefa B) | 42                          |

## Semente do Gerador Aleatório

Para garantir reprodutibilidade, a Tarefa B usa semente fixa:

```c
unsigned int seed = 42;
srand(seed);
```
