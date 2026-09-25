import sys
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"

RESULTS_DIR = PROJECT_ROOT / "results"

RESULTS_DIR.mkdir(
    exist_ok=True
)

sys.path.insert(
    0,
    str(SIMULATION_DIR)
)


# ============================================================
# EARTH-N MODULES
# ============================================================

from city_model import create_earth_network

from cascade_engine import (
    simulate_cascade
)


# ============================================================
# CREATE NETWORK
# ============================================================

network = create_earth_network()


# ============================================================
# SIMULATE GRID FAILURE
# ============================================================

failed_node = "GridStation"

simulation, affected_nodes = simulate_cascade(
    network,
    failed_node
)


# ============================================================
# NETWORK POSITIONS
# ============================================================

positions = {

    "PowerPlant": (0, 4),

    "GridStation": (2, 4),

    "Substation_A": (4, 5),

    "Substation_B": (4, 3),

    "WaterPlant": (0, 1),

    "WaterPump_A": (4, 1.5),

    "WaterPump_B": (4, 0),

    "Telecom_Tower_A": (6, 5.5),

    "Telecom_Tower_B": (6, 3),

    "Road_A": (6, 1),

    "Road_B": (6, -1),

    "Hospital": (9, 5),

    "Emergency_Center": (9, 3),

    "Industrial_Plant": (9, 0)
}


# ============================================================
# CREATE FIGURE
# ============================================================

plt.figure(
    figsize=(15, 9)
)


# ============================================================
# DRAW CONNECTIONS
# ============================================================

nx.draw_networkx_edges(
    simulation,
    positions,
    arrows=True,
    arrowsize=18,
    width=2,
    alpha=0.55
)


# ============================================================
# CLASSIFY NODES
# ============================================================

normal_nodes = []

failed_nodes = []

critical_nodes = []

critical_affected_nodes = []


for node in simulation.nodes():

    sector = simulation.nodes[node][
        "sector"
    ]

    service = simulation.nodes[node][
        "service_level"
    ]

    if node == failed_node:

        failed_nodes.append(node)

    elif sector == "critical":

        critical_nodes.append(node)

        if service < 1.0:

            critical_affected_nodes.append(
                node
            )

    elif service < 1.0:

        failed_nodes.append(node)

    else:

        normal_nodes.append(node)


# ============================================================
# DRAW NORMAL INFRASTRUCTURE
# ============================================================

if normal_nodes:

    nx.draw_networkx_nodes(
        simulation,
        positions,
        nodelist=normal_nodes,
        node_size=1600,
        alpha=0.9
    )


# ============================================================
# DRAW FAILED / AFFECTED INFRASTRUCTURE
# ============================================================

if failed_nodes:

    nx.draw_networkx_nodes(
        simulation,
        positions,
        nodelist=failed_nodes,
        node_size=1900,
        alpha=0.9
    )


# ============================================================
# DRAW CRITICAL FACILITIES
# ============================================================

if critical_nodes:

    nx.draw_networkx_nodes(
        simulation,
        positions,
        nodelist=critical_nodes,
        node_size=2200,
        node_shape="s",
        alpha=0.9
    )


# ============================================================
# LABEL NODES
# ============================================================

labels = {}

for node in simulation.nodes():

    labels[node] = node.replace(
        "_",
        "\n"
    )


nx.draw_networkx_labels(
    simulation,
    positions,
    labels=labels,
    font_size=8,
    font_weight="bold"
)


# ============================================================
# SERVICE LEVEL LABELS
# ============================================================

service_labels = {}

for node, data in simulation.nodes(
    data=True
):

    service = data["service_level"]

    service_labels[node] = (
        f"{service * 100:.0f}%"
    )


for node, position in positions.items():

    x, y = position

    plt.text(
        x,
        y - 0.45,
        service_labels[node],
        ha="center",
        fontsize=9,
        fontweight="bold"
    )


# ============================================================
# TITLE
# ============================================================

plt.title(
    "EARTH-N — Extreme Heatwave Cross-Sector Cascade",
    fontsize=18,
    fontweight="bold",
    pad=20
)


# ============================================================
# INFORMATION PANEL
# ============================================================

affected_count = len(
    affected_nodes
)

critical_affected_count = len(
    critical_affected_nodes
)


information = (
    "DISASTER CHAIN\n"
    "Extreme Heatwave\n"
    "↓\n"
    "Electricity Demand Increase\n"
    "↓\n"
    "GridStation Failure\n"
    "↓\n"
    "Cross-Sector Cascade\n"
    "↓\n"
    f"{affected_count} infrastructure nodes affected\n"
    "↓\n"
    f"{critical_affected_count} critical facilities affected"
)


plt.text(
    0.02,
    0.02,
    information,
    transform=plt.gca().transAxes,
    fontsize=10,
    verticalalignment="bottom",
    bbox=dict(
        boxstyle="round,pad=0.5",
        alpha=0.08
    )
)


# ============================================================
# LEGEND
# ============================================================

legend_text = (
    "Node labels show remaining service level"
)

plt.text(
    0.98,
    0.02,
    legend_text,
    transform=plt.gca().transAxes,
    ha="right",
    fontsize=9
)


# ============================================================
# FINAL FORMATTING
# ============================================================

plt.axis("off")

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

output_file = (
    RESULTS_DIR
    / "earthn_heatwave_cascade.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)


# ============================================================
# OUTPUT
# ============================================================

print("=" * 70)
print("EARTH-N — HEATWAVE CASCADE VISUALIZATION")
print("=" * 70)

print(
    f"\nInitial failure: {failed_node}"
)

print(
    f"Affected infrastructure: "
    f"{affected_count}"
)

print(
    f"Affected critical facilities: "
    f"{critical_affected_count}"
)

print(
    f"\nVisualization saved to:\n{output_file}"
)

print(
    "\nEARTH-N HEATWAVE CASCADE VISUALIZATION COMPLETE"
)


plt.show()