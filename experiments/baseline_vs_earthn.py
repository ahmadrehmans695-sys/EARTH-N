import sys
from pathlib import Path

# Add the simulation folder to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"

sys.path.insert(0, str(SIMULATION_DIR))

from city_model import create_earth_network
from cascade_engine import simulate_failure


def calculate_risk(G, affected_nodes):
    """
    Calculate a simple infrastructure risk score.

    Higher importance = higher consequence if affected.
    """

    total_importance = sum(
        G.nodes[node]["importance"]
        for node in affected_nodes
    )

    return total_importance


def earthn_intervention(G, affected_nodes):
    """
    Simulate a coordinated Earth-N intervention.

    Earth-N protects the highest-importance
    critical facilities first.
    """

    critical_nodes = [
        node
        for node in affected_nodes
        if G.nodes[node]["sector"] == "critical"
    ]

    critical_nodes.sort(
        key=lambda node: G.nodes[node]["importance"],
        reverse=True
    )

    # Protect the two highest-priority critical facilities.
    protected = critical_nodes[:2]

    remaining_affected = [
        node
        for node in affected_nodes
        if node not in protected
    ]

    return protected, remaining_affected


def run_experiment():
    network = create_earth_network()

    failed_node = "GridStation"

    # -------------------------------------------------
    # BASELINE
    # -------------------------------------------------

    _, baseline_affected = simulate_failure(
        network,
        failed_node
    )

    baseline_risk = calculate_risk(
        network,
        baseline_affected
    )

    # -------------------------------------------------
    # EARTH-N
    # -------------------------------------------------

    protected, earthn_affected = earthn_intervention(
        network,
        baseline_affected
    )

    earthn_risk = calculate_risk(
        network,
        earthn_affected
    )

    # -------------------------------------------------
    # RESULTS
    # -------------------------------------------------

    risk_reduction = (
        (baseline_risk - earthn_risk)
        / baseline_risk
        * 100
    )

    print("=" * 60)
    print("EARTH-N — BASELINE VS COORDINATED RESPONSE")
    print("=" * 60)

    print(f"\nInitial failure: {failed_node}")

    print("\nBASELINE")
    print("-" * 60)
    print(f"Affected infrastructure: {len(baseline_affected)}")
    print(f"Risk score: {baseline_risk}")

    print("\nEARTH-N COORDINATED RESPONSE")
    print("-" * 60)
    print(f"Protected facilities: {len(protected)}")

    for node in protected:
        print(f"✓ Protected: {node}")

    print(f"\nRemaining affected infrastructure: {len(earthn_affected)}")
    print(f"Risk score: {earthn_risk}")

    print("\nRESULT")
    print("-" * 60)
    print(f"Risk reduction: {risk_reduction:.2f}%")

    print("\nEARTH-N EXPERIMENT COMPLETE")


if __name__ == "__main__":
    run_experiment()