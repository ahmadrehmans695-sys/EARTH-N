import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"

sys.path.insert(0, str(SIMULATION_DIR))

from city_model import create_earth_network
from cascade_engine import simulate_cascade, calculate_system_service


def apply_intervention(G, target_node):
    """
    Simulate emergency protection of a critical facility.

    The intervention restores the selected facility and
    its direct upstream dependencies.
    """

    if target_node not in G.nodes:
        return G

    # Restore the selected critical facility.
    G.nodes[target_node]["service_level"] = 1.0

    # Restore direct upstream dependencies.
    for parent in G.predecessors(target_node):

        G.nodes[parent]["service_level"] = max(
            G.nodes[parent]["service_level"],
            1.0
        )

    return G


def evaluate_intervention(network, failed_node, target_node):
    """
    Test one possible intervention.

    Returns the resulting system service.
    """

    simulation, affected = simulate_cascade(
        network,
        failed_node
    )

    simulation = apply_intervention(
        simulation,
        target_node
    )

    system_service = calculate_system_service(
        simulation
    )

    return system_service, affected


def run_intervention_analysis():

    print("=" * 70)
    print("EARTH-N — INTERVENTION ANALYSIS")
    print("=" * 70)

    network = create_earth_network()

    failed_node = "GridStation"

    print("\nINITIAL FAILURE")
    print("-" * 70)
    print(f"Failed infrastructure: {failed_node}")

    # -------------------------------------------------
    # BASELINE
    # -------------------------------------------------

    baseline, affected = simulate_cascade(
        network,
        failed_node
    )

    baseline_service = calculate_system_service(
        baseline
    )

    print("\nBASELINE")
    print("-" * 70)

    print(
        f"System service without intervention: "
        f"{baseline_service * 100:.2f}%"
    )

    # -------------------------------------------------
    # TEST INTERVENTIONS
    # -------------------------------------------------

    intervention_targets = [
        "Hospital",
        "Emergency_Center",
        "Industrial_Plant"
    ]

    results = []

    print("\nTESTING POSSIBLE INTERVENTIONS")
    print("-" * 70)

    for target in intervention_targets:

        test_network = create_earth_network()

        service, affected = evaluate_intervention(
            test_network,
            failed_node,
            target
        )

        results.append(
            (target, service)
        )

        print(
            f"{target:20} | "
            f"System service: "
            f"{service * 100:6.2f}%"
        )

    # -------------------------------------------------
    # SELECT BEST SYSTEM-SERVICE INTERVENTION
    # -------------------------------------------------

    best_target, best_service = max(
        results,
        key=lambda item: item[1]
    )

    improvement = (
        best_service - baseline_service
    )

    print("\nEARTH-N RECOMMENDATION")
    print("-" * 70)

    print(
        f"Selected intervention: {best_target}"
    )

    print(
        f"Resulting system service: "
        f"{best_service * 100:.2f}%"
    )

    print(
        f"Improvement over baseline: "
        f"{improvement * 100:.2f}%"
    )

    print("\nEARTH-N INTERVENTION ANALYSIS COMPLETE")


if __name__ == "__main__":
    run_intervention_analysis()