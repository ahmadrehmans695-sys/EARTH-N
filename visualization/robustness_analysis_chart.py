from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_FILE = (
    RESULTS_DIR
    / "earthn_robustness_results.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR
    / "earthn_robustness_chart.png"
)


# ============================================================
# LOAD RESULTS
# ============================================================

df = pd.read_csv(
    INPUT_FILE
)


# ============================================================
# CALCULATE STATISTICS BY TEMPERATURE
# ============================================================

summary = (
    df
    .groupby("temperature_c")[
        "improvement_percentage_points"
    ]
    .agg(
        mean="mean",
        minimum="min",
        maximum="max",
    )
    .reset_index()
)


# ============================================================
# CREATE FIGURE
# ============================================================

plt.figure(
    figsize=(10, 6)
)


# ============================================================
# MEAN IMPROVEMENT
# ============================================================

plt.plot(
    summary["temperature_c"],
    summary["mean"],
    marker="o",
    linewidth=2,
    label="Mean Earth-N improvement",
)


# ============================================================
# ROBUSTNESS RANGE
# ============================================================

plt.fill_between(
    summary["temperature_c"],
    summary["minimum"],
    summary["maximum"],
    alpha=0.20,
    label="Observed range across randomized runs",
)


# ============================================================
# AXIS LABELS
# ============================================================

plt.xlabel(
    "Heatwave Temperature Increase (°C)"
)

plt.ylabel(
    "Earth-N Improvement (Percentage Points)"
)

plt.title(
    "EARTH-N Randomized Robustness Analysis"
)


# ============================================================
# GRID AND LEGEND
# ============================================================

plt.grid(
    True,
    alpha=0.3
)

plt.legend()


# ============================================================
# LAYOUT
# ============================================================

plt.tight_layout()


# ============================================================
# SAVE HIGH-RESOLUTION FIGURE
# ============================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=600,
    bbox_inches="tight"
)


plt.close()


# ============================================================
# CONFIRMATION
# ============================================================

print("=" * 70)
print(
    "EARTH-N RANDOMIZED ROBUSTNESS VISUALIZATION"
)
print("=" * 70)

print(
    f"\nInput:\n{INPUT_FILE}"
)

print(
    f"\nOutput:\n{OUTPUT_FILE}"
)

print(
    "\nVisualization created successfully."
)