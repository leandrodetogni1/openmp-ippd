#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <omp.h>

double get_time() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr, "Uso: %s <N> <B> <variante> <threads> [seed]\n", argv[0]);
        fprintf(stderr, "  variante: 1=critical, 2=atomic, 3=local\n");
        return 1;
    }

    int N = atoi(argv[1]);
    int B = atoi(argv[2]);
    int variante = atoi(argv[3]);
    int num_threads = atoi(argv[4]);
    unsigned int seed = (argc > 5) ? atoi(argv[5]) : 42;

    if (N <= 0 || B <= 0 || variante < 1 || variante > 3 || num_threads <= 0) {
        fprintf(stderr, "Parâmetros inválidos\n");
        return 1;
    }

    omp_set_num_threads(num_threads);

    int *A = (int *)malloc(N * sizeof(int));
    if (!A) {
        fprintf(stderr, "Erro ao alocar array A\n");
        return 1;
    }

    uint64_t *H = (uint64_t *)calloc(B, sizeof(uint64_t));
    if (!H) {
        fprintf(stderr, "Erro ao alocar histograma H\n");
        free(A);
        return 1;
    }

    srand(seed);
    for (int i = 0; i < N; i++) {
        A[i] = rand() % B;
    }

    const char *variant_name;
    double start = get_time();

    switch (variante) {
        case 1:
            variant_name = "critical";
            #pragma omp parallel for
            for (int i = 0; i < N; i++) {
                #pragma omp critical
                {
                    H[A[i]]++;
                }
            }
            break;

        case 2:
            variant_name = "atomic";
            #pragma omp parallel for
            for (int i = 0; i < N; i++) {
                #pragma omp atomic
                H[A[i]]++;
            }
            break;

        case 3:
            variant_name = "local";
            {
                uint64_t **H_local = (uint64_t **)malloc(num_threads * sizeof(uint64_t *));
                for (int t = 0; t < num_threads; t++) {
                    H_local[t] = (uint64_t *)calloc(B, sizeof(uint64_t));
                }

                #pragma omp parallel
                {
                    int tid = omp_get_thread_num();
                    #pragma omp for
                    for (int i = 0; i < N; i++) {
                        H_local[tid][A[i]]++;
                    }
                }

                #pragma omp parallel for
                for (int b = 0; b < B; b++) {
                    for (int t = 0; t < num_threads; t++) {
                        H[b] += H_local[t][b];
                    }
                }

                for (int t = 0; t < num_threads; t++) {
                    free(H_local[t]);
                }
                free(H_local);
            }
            break;
    }

    double end = get_time();
    double elapsed = end - start;

    uint64_t sum = 0;
    for (int i = 0; i < B; i++) {
        sum += H[i];
    }

    printf("B,%s,%d,%d,%d,%.6f,%llu\n", variant_name, N, B, num_threads, elapsed, (unsigned long long)sum);

    free(A);
    free(H);
    return 0;
}
