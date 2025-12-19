#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

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
    if (argc != 3) {
        fprintf(stderr, "Uso: %s <N> <K>\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);
    int K = atoi(argv[2]);

    if (N <= 0 || K <= 0) {
        fprintf(stderr, "N e K devem ser positivos\n");
        return 1;
    }

    uint64_t *v = (uint64_t *)malloc(N * sizeof(uint64_t));
    if (!v) {
        fprintf(stderr, "Erro ao alocar memória\n");
        return 1;
    }

    double start = get_time();

    for (int i = 0; i < N; i++) {
        v[i] = fib(i % K);
    }

    double end = get_time();
    double elapsed = end - start;

    uint64_t checksum = 0;
    for (int i = 0; i < N; i++) {
        checksum += v[i];
    }

    printf("A,seq,none,0,%d,%d,1,%.6f,%llu\n", N, K, elapsed, (unsigned long long)checksum);

    free(v);
    return 0;
}
