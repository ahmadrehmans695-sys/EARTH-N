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
    / "earthn_sensitivity_results.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR
    / "earthn_dependency_sensitivity.png"
)


# ============================================================
# LOAD RESULTS
# ============================================================

df = pd.read_csv(
    INPUT_FILE
)


# ============================================================
# KEEP FAILURE SCENARIOS
# ============================================================

failure_df = df[
    df["failure"] == "YES"
].copy()


# ============================================================
# CREATE FIGURE
# ============================================================

plt.figure(
    figsize=(10, 6)
)


# ============================================================
# PLOT EACH DEPENDENCY CONDITION
# ============================================================

scenarios = [
    "Lower",
    "Base",
    "Higher",
]


for scenario in scenarios:

    scenario_df = failure_df[
        failure_df[
            "dependency_scenario"
        ]
        == scenario
    ]

    plt.plot(
        scenario_df["temperature_c"],
        scenario_df[
            "improvement_percentage_points"
        ],
        marker="o",
        linewidth=2,
        label=scenario,
    )


# ============================================================
# LABELS
# ============================================================

plt.xlabel(
    "Heatwave Temperature Increase (°C)"
)

plt.ylabel(
    "Earth-N Improvement (Percentage Points)"
)

plt.title(
    "EARTH-N Sensitivity to Infrastructure Dependency Strength"
)


# ============================================================
# GRID / LEGEND
# ============================================================

plt.grid(
    True,
    alpha=0.3
)

plt.legend(
    title="Dependency Condition"
)


# ============================================================
# LAYOUT
# ============================================================

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=600,
    bbox_inches="tight"
)


plt.close()


print("=" * 70)
print("EARTH-N DEPENDENCY SENSITIVITY VISUALIZATION")
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