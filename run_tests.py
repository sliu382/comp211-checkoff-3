import subprocess
import statistics
import random
import csv
import sys
from pathlib import Path

# EXPERIMENT SETTINGS

SIZES = [10_000, 100_000, 1_000_000, 10_000_000]
FLAGS = ["-O0", "-O1", "-O2", "-O3"]

TRIALS = 30
ROUNDS = 3
TRIALS_PER_ROUND = TRIALS // ROUNDS

assert TRIALS % ROUNDS == 0

PROJECT_DIR = Path(__file__).resolve().parent
BIN_DIR = PROJECT_DIR / "bin"
RESULTS_DIR = PROJECT_DIR / "results"
data_files = {n: PROJECT_DIR / "data" / f"numbers_{n:_}.txt" for n in SIZES}

BIN_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# STEP 1: GENERATE DATA IF NEEDED

if not all(path.is_file() for path in data_files.values()):
    subprocess.run([sys.executable, PROJECT_DIR / "generate_data.py"], check=True)

# STEP 2: COMPILE ALL C EXECUTABLES

executables = {flag: BIN_DIR / f"bench_{flag.lstrip('-')}" for flag in FLAGS}

for flag, executable in executables.items():
    subprocess.run(
        ["gcc", flag, PROJECT_DIR / "sum_numbers.c", "-o", executable], check=True
    )

    print(f"Compiled C with {flag}")

# STEP 3: PREPARE ALL TEST CONFIGURATIONS

implementations = FLAGS + ["Python"]

configurations = [
    (n, implementation) for n in SIZES for implementation in implementations
]

all_results = []
expected_sums = {}

# STEP 4: RUN ALL BENCHMARKS

rng = random.Random(42)

for round_number in range(ROUNDS):
    # Reduce systematic bias from execution order.
    rng.shuffle(configurations)

    for n, implementation in configurations:
        filename = data_files[n]

        print(f"Round {round_number + 1}/{ROUNDS}: {implementation}, N={n:,}")

        if implementation == "Python":
            command = [
                sys.executable,
                PROJECT_DIR / "sum_numbers.py",
                filename,
                str(n),
                str(TRIALS_PER_ROUND),
            ]

        else:
            command = [
                executables[implementation], filename, str(n), str(TRIALS_PER_ROUND)
            ]

        # Run the benchmark and capture its output.
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        lines = result.stdout.strip().splitlines()

        if len(lines) != TRIALS_PER_ROUND:
            raise ValueError("Incorrect number of results")

        for i, line in enumerate(lines):
            total, elapsed_ns = map(int, line.split(","))

            # Verify that every implementation produces
            # an identical sum for the same input file.
            if n not in expected_sums:
                expected_sums[n] = total

            if total != expected_sums[n]:
                raise ValueError(f"Incorrect sum for {implementation}, N={n}")

            all_results.append(
                {
                    "size": n,
                    "implementation": implementation,
                    "trial": round_number * TRIALS_PER_ROUND + i + 1,
                    "sum": total,
                    "time_ns": elapsed_ns,
                    "time_ms": elapsed_ns / 1_000_000,
                }
            )

# STEP 5: SAVE RAW RESULTS

with (RESULTS_DIR / "raw_results.csv").open("w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["size", "implementation", "trial", "sum", "time_ns", "time_ms"],
    )

    writer.writeheader()
    writer.writerows(all_results)

# STEP 6: CALCULATE STATISTICS

summary = []

for n in SIZES:
    python_times = [
        row["time_ms"]
        for row in all_results
        if row["size"] == n and row["implementation"] == "Python"
    ]

    python_median = statistics.median(python_times)

    for implementation in implementations:
        times = [
            row["time_ms"]
            for row in all_results
            if row["size"] == n and row["implementation"] == implementation
        ]

        median = statistics.median(times)

        summary.append(
            {
                "size": n,
                "implementation": implementation,
                "trials": len(times),
                "mean_ms": statistics.mean(times),
                "median_ms": median,
                "std_dev_ms": statistics.stdev(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "ns_per_integer": median * 1_000_000 / n,
                "speedup_vs_python": python_median / median,
            }
        )

# STEP 7: SAVE SUMMARY STATISTICS

with (RESULTS_DIR / "summary.csv").open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(summary[0].keys()))

    writer.writeheader()
    writer.writerows(summary)

# STEP 8: PRINT RESULTS

print("\nBENCHMARK RESULTS")
print("-" * 65)

print(f"{'Input Size':>12} {'Implementation':>15} {'Median (ms)':>15} {'Speedup':>12}")

for row in summary:
    print(
        f"{row['size']:>12,} "
        f"{row['implementation']:>15} "
        f"{row['median_ms']:>15.6f} "
        f"{row['speedup_vs_python']:>11.2f}x"
    )

print(f"\nCompleted {len(all_results)} benchmark trials.")
print("Results saved to results/raw_results.csv")
print("Summary saved to results/summary.csv")
