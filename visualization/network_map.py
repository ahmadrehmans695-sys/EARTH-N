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
# EARTH-N MODEL
# ============================================================

from city_model import create_earth_network


# ============================================================
# CREATE NETWORK
# ============================================================

G = create_earth_network()


# ============================================================
# NODE GROUPS
# ============================================================

sector_groups = {}

for node, data in G.nodes(data=True):

    sector = data["sector"]

    if sector not in sector_groups:

        sector_groups[sector] = []

    sector_groups[sector].append(node)


# ============================================================
# NETWORK LAYOUT
# ============================================================

positions = {

    # --------------------------------------------------------
    # ELECTRICITY
    # --------------------------------------------------------

    "PowerPlant": (0, 4),

    "GridStation": (2, 4),

    "Substation_A": (4, 5),

    "Substation_B": (4, 3),

    # --------------------------------------------------------
    # WATER
    # --------------------------------------------------------

    "WaterPlant": (0, 1),

    "WaterPump_A": (4, 1.5),

    "WaterPump_B": (4, 0),

    # --------------------------------------------------------
    # TELECOM
    # --------------------------------------------------------

    "Telecom_Tower_A": (6, 5.5),

    "Telecom_Tower_B": (6, 3),

    # --------------------------------------------------------
    # TRANSPORT
    # --------------------------------------------------------

    "Road_A": (6, 1),

    "Road_B": (6, -1),

    # --------------------------------------------------------
    # CRITICAL FACILITIES
    # --------------------------------------------------------

    "Hospital": (9, 5),

    "Emergency_Center": (9, 3),

    "Industrial_Plant": (9, 0)
}


# ============================================================
# DRAW NETWORK
# ============================================================

plt.figure(
    figsize=(15, 9)
)

nx.draw_networkx_edges(
    G,
    positions,
    arrows=True,
    arrowsize=18,
    width=1.8,
    alpha=0.65
)


# ============================================================
# DRAW NODES
# ============================================================

sector_sizes = {
    "electricity": 1700,
    "water": 1500,
    "telecom": 1500,
    "transport": 1500,
    "critical": 2100
}


for sector, nodes in sector_groups.items():

    nx.draw_networkx_nodes(
        G,
        positions,
        nodelist=nodes,
        node_size=sector_sizes.get(
            sector,
            1500
        ),
        alpha=0.9
    )


# ============================================================
# NODE LABELS
# ============================================================

labels = {}

for node in G.nodes():

    labels[node] = node.replace(
        "_",
        "\n"
    )


nx.draw_networkx_labels(
    G,
    positions,
    labels=labels,
    font_size=8,
    font_weight="bold"
)


# ============================================================
# EDGE DEPENDENCY LABELS
# ============================================================

edge_labels = {}

for source, target, data in G.edges(
    data=True
):

    strength = data.get(
        "dependency_strength",
        1.0
    )

    edge_labels[
        (source, target)
    ] = f"{strength:.1f}"


nx.draw_networkx_edge_labels(
    G,
    positions,
    edge_labels=edge_labels,
    font_size=7
)


# ============================================================
# TITLE
# ============================================================

plt.title(
    "EARTH-N — Interconnected Infrastructure Network",
    fontsize=18,
    fontweight="bold",
    pad=20
)


plt.axis("off")

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

output_file = (
    RESULTS_DIR
    / "earthn_network_map.png"
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
print("EARTH-N — INFRASTRUCTURE NETWORK VISUALIZATION")
print("=" * 70)

print(
    f"\nNetwork map saved to:\n{output_file}"
)

print(
    "\nEARTH-N NETWORK VISUALIZATION COMPLETE"
)


plt.show()