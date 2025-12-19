#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

double get_time() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Uso: %s <N> <B> [seed]\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);
    int B = atoi(argv[2]);
    unsigned int seed = (argc > 3) ? atoi(argv[3]) : 42;

    if (N <= 0 || B <= 0) {
        fprintf(stderr, "N e B devem ser positivos\n");
        return 1;
    }

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

    double start = get_time();

    for (int i = 0; i < N; i++) {
        H[A[i]]++;
    }

    double end = get_time();
    double elapsed = end - start;

    uint64_t sum = 0;
    for (int i = 0; i < B; i++) {
        sum += H[i];
    }

    printf("B,seq,%d,%d,1,%.6f,%llu\n", N, B, elapsed, (unsigned long long)sum);

    free(A);
    free(H);
    return 0;
}
