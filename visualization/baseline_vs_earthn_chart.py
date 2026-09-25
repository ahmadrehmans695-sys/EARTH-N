import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_FILE = (
    RESULTS_DIR
    / "earthn_baseline_vs_intervention.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR
    / "earthn_baseline_vs_intervention.png"
)


# =========================================================
# LOAD DATA
# =========================================================

if not INPUT_FILE.exists():

    print("ERROR")
    print("-" * 60)
    print(f"Input file not found:")
    print(INPUT_FILE)
    print()
    print(
        "Run Step 35 first."
    )

    sys.exit(1)


data = pd.read_csv(
    INPUT_FILE
)


# =========================================================
# PREPARE DATA
# =========================================================

temperature = data[
    "temperature_c"
]

baseline = data[
    "baseline_system_service_percent"
]

earthn = data[
    "earthn_service_percent"
]

failure = data[
    "failure"
]


# =========================================================
# CREATE FIGURE
# =========================================================

fig, ax = plt.subplots(
    figsize=(12, 7)
)


# =========================================================
# PLOT BASELINE
# =========================================================

ax.plot(
    temperature,
    baseline,
    marker="o",
    linewidth=2.5,
    markersize=5,
    label="Baseline",
)


# =========================================================
# PLOT EARTH-N
# =========================================================

ax.plot(
    temperature,
    earthn,
    marker="o",
    linewidth=2.5,
    markersize=5,
    label="Earth-N Coordinated Intervention",
)


# =========================================================
# FIND FAILURE THRESHOLD
# =========================================================

failure_rows = data[
    data["failure"] == "YES"
]

if not failure_rows.empty:

    first_failure_temperature = (
        failure_rows.iloc[0]["temperature_c"]
    )

    ax.axvline(
        first_failure_temperature,
        linestyle="--",
        linewidth=1.8,
        label="Simulated Grid Failure Threshold",
    )


# =========================================================
# LABELS
# =========================================================

ax.set_title(
    "EARTH-N: Baseline vs Coordinated Intervention",
    fontsize=16,
    fontweight="bold",
    pad=15,
)

ax.set_xlabel(
    "Heatwave Temperature Increase (°C)",
    fontsize=12,
)

ax.set_ylabel(
    "System Service (%)",
    fontsize=12,
)


# =========================================================
# AXIS LIMITS
# =========================================================

ax.set_xlim(
    temperature.min(),
    temperature.max(),
)

ax.set_ylim(
    45,
    105,
)


# =========================================================
# GRID
# =========================================================

ax.grid(
    True,
    linestyle="--",
    alpha=0.35,
)


# =========================================================
# LEGEND
# =========================================================

ax.legend(
    loc="lower left",
    fontsize=10,
)


# =========================================================
# LAYOUT
# =========================================================

plt.tight_layout()


# =========================================================
# SAVE
# =========================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight",
)


plt.close()


# =========================================================
# OUTPUT
# =========================================================

print("=" * 70)
print("EARTH-N — BASELINE VS EARTH-N CHART")
print("=" * 70)

print()
print(
    f"Input:\n{INPUT_FILE}"
)

print()
print(
    f"Output:\n{OUTPUT_FILE}"
)

print()
print(
    "Chart generated successfully."
)

print("=" * 70)