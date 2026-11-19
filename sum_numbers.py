import sys
import time

WARMUP_RUNS = 2

filename = sys.argv[1]
n = int(sys.argv[2])
trials = int(sys.argv[3])

# Read input data before benchmarking.
with open(filename, "r") as file:
    arr = [int(line) for line in file]

if len(arr) != n:
    raise ValueError("Incorrect number of integers")


def calculate_sum(arr):
    total = 0

    for value in arr:
        total += value

    return total


for trial in range(-WARMUP_RUNS, trials):
    start = time.perf_counter_ns()

    # THE COMPUTATION WE ARE BENCHMARKING
    total = calculate_sum(arr)

    end = time.perf_counter_ns()

    elapsed_ns = end - start

    # Do not record warm-up runs.
    if trial >= 0:
        print(f"{total},{elapsed_ns}")
