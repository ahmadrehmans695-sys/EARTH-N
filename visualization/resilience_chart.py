import sys
from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results"

RESULTS_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# EARTH-N CRI RESULTS
# ============================================================

scenarios = [
    "No Intervention",
    "Hospital",
    "Emergency Center",
    "Industrial Plant"
]

cri_values = [
    59.46,
    65.86,
    79.12,
    63.98
]


# ============================================================
# CREATE FIGURE
# ============================================================

plt.figure(
    figsize=(10, 6)
)


# ============================================================
# CREATE BAR CHART
# ============================================================

bars = plt.bar(
    scenarios,
    cri_values
)


# ============================================================
# LABEL VALUES
# ============================================================

for bar, value in zip(
    bars,
    cri_values
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1,
        f"{value:.2f}",
        ha="center",
        va="bottom",
        fontsize=11
    )


# ============================================================
# CHART INFORMATION
# ============================================================

plt.title(
    "EARTH-N Cascading Resilience Index",
    fontsize=16
)

plt.ylabel(
    "CRI Score",
    fontsize=12
)

plt.xlabel(
    "Intervention Scenario",
    fontsize=12
)

plt.ylim(
    0,
    100
)

plt.grid(
    axis="y",
    alpha=0.25
)

plt.xticks(
    rotation=15
)

plt.tight_layout()


# ============================================================
# SAVE FIGURE
# ============================================================

output_file = (
    RESULTS_DIR
    / "earthn_cri_comparison.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("=" * 70)
print("EARTH-N — RESILIENCE VISUALIZATION")
print("=" * 70)

print(
    f"\nChart saved to:\n{output_file}"
)

print(
    "\nEARTH-N VISUALIZATION COMPLETE"
)


plt.show()