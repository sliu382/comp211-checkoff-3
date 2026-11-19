import csv
import random
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


RESULTS_DIR = Path(__file__).resolve().parent / "results"
FLAGS = ("-O0", "-O1", "-O2", "-O3")
IMPLEMENTATIONS = (*FLAGS, "Python")
COLORS = ("#326c96", "#21877a", "#7657a1", "#a85b27", "#48515d")


def read_summary():
    summary = defaultdict(dict)
    with (RESULTS_DIR / "summary.csv").open(newline="") as file:
        for row in csv.DictReader(file):
            summary[row["implementation"]][int(row["size"])] = row
    return summary


def plot_speedups(summary):
    sizes = sorted(summary["Python"])
    positions = range(len(sizes))
    bar_width = 0.19
    fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")

    for index, (flag, color) in enumerate(zip(FLAGS, COLORS)):
        offset = (index - (len(FLAGS) - 1) / 2) * bar_width
        speedups = [float(summary[flag][size]["speedup_vs_python"]) for size in sizes]
        bars = ax.bar(
            [position + offset for position in positions],
            speedups,
            width=bar_width,
            label=flag,
            color=color,
        )
        ax.bar_label(bars, fmt="%.1f×", padding=3, fontsize=9)

    ax.set_title("C speedup over Python by input size")
    ax.set_xlabel("Input size (integers)")
    ax.set_ylabel("Python median runtime / C median runtime (×)")
    ax.set_xticks(positions, [f"{size:,}" for size in sizes])
    ax.set_ylim(bottom=0)
    ax.margins(y=0.15)
    ax.axhline(1, color=COLORS[-1], linestyle="--", linewidth=0.9)
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncols=len(FLAGS), loc="upper center", bbox_to_anchor=(0.5, -0.13))

    fig.savefig(RESULTS_DIR / "speedup.png", dpi=180)
    plt.close(fig)


def plot_median_runtimes(summary):
    sizes = sorted(summary["Python"])
    fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")

    for implementation, color, marker, style in zip(
        IMPLEMENTATIONS, COLORS, ("o", "s", "D", "x", "^"), ("-", "-", "-", "--", "-")
    ):
        medians = [float(summary[implementation][size]["median_ms"]) for size in sizes]
        ax.plot(
            sizes,
            medians,
            label=implementation,
            color=color,
            marker=marker,
            linestyle=style,
            markerfacecolor="none",
        )

    ax.set_title("Median runtime by input size")
    ax.set_xlabel("Input size (integers)")
    ax.set_ylabel("Median runtime (ms)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(sizes, [f"{size:,}" for size in sizes])
    ax.grid(alpha=0.25)
    ax.legend()

    fig.savefig(RESULTS_DIR / "median_runtime.png", dpi=180)
    plt.close(fig)


def plot_runtimes():
    times = defaultdict(lambda: defaultdict(list))
    with (RESULTS_DIR / "raw_results.csv").open(newline="") as file:
        for row in csv.DictReader(file):
            times[int(row["size"])][row["implementation"]].append(float(row["time_ms"]))

    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharey=True, layout="constrained")
    fig.suptitle("Raw benchmark runtimes by input size")
    fig.supxlabel("Implementation · Each dot is one recorded trial")
    fig.supylabel("Runtime (ms) · Linear near zero, logarithmic above 0.001 ms")
    rng = random.Random(42)

    for ax, size in zip(axes.flat, sorted(times), strict=True):
        for position, (implementation, color) in enumerate(zip(IMPLEMENTATIONS, COLORS)):
            values = times[size][implementation]
            positions = [position + rng.uniform(-0.19, 0.19) for _ in values]
            ax.scatter(positions, values, s=18, color=color, alpha=0.65, edgecolors="none")

        ax.set_title(f"{size:,} integers")
        ax.set_xticks(range(len(IMPLEMENTATIONS)), IMPLEMENTATIONS)
        ax.set_xlim(-0.5, len(IMPLEMENTATIONS) - 0.5)
        ax.set_yscale("symlog", linthresh=0.001)
        ax.set_axisbelow(True)
        ax.grid(axis="y", alpha=0.25)

    fig.savefig(RESULTS_DIR / "runtimes.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    summary = read_summary()
    plot_speedups(summary)
    plot_median_runtimes(summary)
    plot_runtimes()
    print(f"Saved speedup.png, median_runtime.png, and runtimes.png in {RESULTS_DIR}")
