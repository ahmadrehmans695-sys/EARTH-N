import csv
from pathlib import Path

import matplotlib.pyplot as plt


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "earthn_heatwave_experiment.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "earthn_resilience_curve.png"
)


# =========================================================
# LOAD EXPERIMENT DATA
# =========================================================

temperatures = []
grid_stress = []
system_service = []
critical_service = []

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8",
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        temperatures.append(
            float(row["temperature_c"])
        )

        grid_stress.append(
            float(row["grid_stress_percent"])
        )

        system_service.append(
            float(row["system_service_percent"])
        )

        critical_service.append(
            float(row["critical_service_percent"])
        )


# =========================================================
# CREATE FIGURE
# =========================================================

fig, ax1 = plt.subplots(
    figsize=(12, 7)
)


# =========================================================
# SERVICE CURVES
# =========================================================

ax1.plot(
    temperatures,
    system_service,
    marker="o",
    linewidth=2.5,
    label="System Service",
)

ax1.plot(
    temperatures,
    critical_service,
    marker="s",
    linewidth=2.5,
    label="Critical Service",
)

ax1.set_xlabel(
    "Heatwave Temperature Increase (°C)",
    fontsize=12,
)

ax1.set_ylabel(
    "Infrastructure Service (%)",
    fontsize=12,
)

ax1.set_ylim(
    0,
    110,
)

ax1.set_xlim(
    0,
    20,
)

ax1.grid(
    True,
    alpha=0.25,
)


# =========================================================
# GRID STRESS — SECOND AXIS
# =========================================================

ax2 = ax1.twinx()

ax2.plot(
    temperatures,
    grid_stress,
    linestyle="--",
    linewidth=2.5,
    label="Grid Stress",
)

ax2.axhline(
    100,
    linestyle=":",
    linewidth=2,
)

ax2.set_ylabel(
    "Grid Stress (%)",
    fontsize=12,
)

ax2.set_ylim(
    60,
    170,
)


# =========================================================
# FAILURE THRESHOLD
# =========================================================

ax1.axvline(
    6.25,
    linestyle=":",
    linewidth=2,
)

ax1.text(
    6.45,
    92,
    "Simulated failure threshold",
    rotation=90,
    verticalalignment="top",
    fontsize=10,
)


# =========================================================
# TITLE
# =========================================================

plt.title(
    "EARTH-N Resilience Curve Under Heatwave Stress",
    fontsize=16,
    fontweight="bold",
    pad=15,
)


# =========================================================
# COMBINED LEGEND
# =========================================================

lines_1, labels_1 = ax1.get_legend_handles_labels()

lines_2, labels_2 = ax2.get_legend_handles_labels()

ax1.legend(
    lines_1 + lines_2,
    labels_1 + labels_2,
    loc="lower left",
)


# =========================================================
# LAYOUT
# =========================================================

fig.tight_layout()


# =========================================================
# SAVE
# =========================================================

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)


print("=" * 70)
print("EARTH-N RESILIENCE CURVE")
print("=" * 70)
print()
print(f"Input:")
print(INPUT_FILE)
print()
print(f"Output:")
print(OUTPUT_FILE)
print()
print("Graph generated successfully.")
print("=" * 70)