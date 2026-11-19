
#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <time.h>

#define WARMUP_RUNS 2

int main(int argc, char *argv[]) {

    if (argc != 4) {
        fprintf(stderr,
                "Usage: %s <file> <size> <trials>\n",
                argv[0]);
        return 1;
    }

    char *filename = argv[1];
    size_t n = strtoull(argv[2], NULL, 10);
    int trials = atoi(argv[3]);

    // Allocate memory for the array.
    uint32_t *arr = malloc(n * sizeof(uint32_t));

    if (arr == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    // Read the input file.
    FILE *file = fopen(filename, "r");

    if (file == NULL) {
        perror("fopen");
        free(arr);
        return 1;
    }

    for (size_t i = 0; i < n; i++) {
        if (fscanf(file, "%" SCNu32, &arr[i]) != 1) {
            fprintf(stderr, "Invalid input data\n");
            fclose(file);
            free(arr);
            return 1;
        }
    }

    fclose(file);

    // File reading and allocation are complete.
    // Begin benchmarking.

    for (int trial = -WARMUP_RUNS;
         trial < trials;
         trial++) {

        uint64_t sum = 0;
        struct timespec start, end;

        clock_gettime(CLOCK_MONOTONIC, &start);

        // Compiler barrier.
        __asm__ __volatile__("" ::: "memory");

        // THE COMPUTATION WE ARE BENCHMARKING
        for (size_t i = 0; i < n; i++) {
            sum += arr[i];
        }

        // Keep the result and computation observable
        // to the compiler before stopping the timer.
        __asm__ __volatile__("" : : "g"(sum) : "memory");

        clock_gettime(CLOCK_MONOTONIC, &end);

        int64_t elapsed_ns =
            (end.tv_sec - start.tv_sec) * INT64_C(1000000000)
            + (end.tv_nsec - start.tv_nsec);

        // Do not record warm-up runs.
        if (trial >= 0) {
            printf("%" PRIu64 ",%" PRId64 "\n",
                   sum, elapsed_ns);
        }
    }

    free(arr);

    return 0;
}
