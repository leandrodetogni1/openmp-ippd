#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <omp.h>

uint64_t fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

double get_time() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char *argv[]) {
    if (argc != 6) {
        fprintf(stderr, "Uso: %s <N> <K> <variante> <chunk> <threads>\n", argv[0]);
        fprintf(stderr, "  variante: 1=static, 2=dynamic, 3=guided\n");
        return 1;
    }

    int N = atoi(argv[1]);
    int K = atoi(argv[2]);
    int variante = atoi(argv[3]);
    int chunk = atoi(argv[4]);
    int num_threads = atoi(argv[5]);

    if (N <= 0 || K <= 0 || variante < 1 || variante > 3 || num_threads <= 0) {
        fprintf(stderr, "Parâmetros inválidos\n");
        return 1;
    }

    omp_set_num_threads(num_threads);

    uint64_t *v = (uint64_t *)malloc(N * sizeof(uint64_t));
    if (!v) {
        fprintf(stderr, "Erro ao alocar memória\n");
        return 1;
    }

    const char *schedule_name;
    double start = get_time();

    switch (variante) {
        case 1:
            schedule_name = "static";
            #pragma omp parallel for schedule(static)
            for (int i = 0; i < N; i++) {
                v[i] = fib(i % K);
            }
            break;

        case 2:
            schedule_name = "dynamic";
            #pragma omp parallel for schedule(dynamic, chunk)
            for (int i = 0; i < N; i++) {
                v[i] = fib(i % K);
            }
            break;

        case 3:
            schedule_name = "guided";
            #pragma omp parallel for schedule(guided, chunk)
            for (int i = 0; i < N; i++) {
                v[i] = fib(i % K);
            }
            break;
    }

    double end = get_time();
    double elapsed = end - start;

    uint64_t checksum = 0;
    for (int i = 0; i < N; i++) {
        checksum += v[i];
    }

    printf("A,omp,%s,%d,%d,%d,%d,%.6f,%llu\n", 
           schedule_name, chunk, N, K, num_threads, elapsed, (unsigned long long)checksum);

    free(v);
    return 0;
}
