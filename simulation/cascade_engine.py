import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SIMULATION_DIR))

from city_model import create_earth_network


def simulate_cascade(G, failed_node):
    """
    Simulate infrastructure cascade after a failure.

    If a node has a failure_severity value, its remaining
    service is reduced accordingly.

    Downstream nodes receive service based on their strongest
    available dependency path.
    """

    simulation = G.copy()

    if failed_node not in simulation.nodes:
        return simulation, []

    # ---------------------------------------------------------
    # STEP 1 — Apply initial failure severity
    # ---------------------------------------------------------

    severity = simulation.nodes[failed_node].get(
        "failure_severity",
        1.0
    )

    # Convert severity into remaining service.
    #
    # severity 0.0 -> 100% service
    # severity 0.25 -> 75% service
    # severity 1.0 -> 0% service
    #
    # Anything above 1.0 is treated as complete failure.

    remaining_service = max(
        0.0,
        1.0 - min(severity, 1.0)
    )

    simulation.nodes[failed_node][
        "service_level"
    ] = remaining_service

    simulation.nodes[failed_node][
        "operational"
    ] = remaining_service > 0.0

    # ---------------------------------------------------------
    # STEP 2 — Propagate service loss
    # ---------------------------------------------------------

    affected = set()

    changed = True

    while changed:

        changed = False

        for node in simulation.nodes:

            if node == failed_node:
                continue

            predecessors = list(
                simulation.predecessors(node)
            )

            if not predecessors:
                continue

            candidate_services = []

            for parent in predecessors:

                parent_service = simulation.nodes[
                    parent
                ].get(
                    "service_level",
                    1.0
                )

                dependency_strength = (
                    simulation.edges[
                        parent,
                        node
                    ].get(
                        "dependency_strength",
                        1.0
                    )
                )

                effective_service = (
                    parent_service
                    * dependency_strength
                )

                candidate_services.append(
                    effective_service
                )

            if not candidate_services:
                continue

            new_service = max(
                candidate_services
            )

            old_service = simulation.nodes[
                node
            ].get(
                "service_level",
                1.0
            )

            # Only reduce service during cascade.
            if new_service < old_service:

                simulation.nodes[
                    node
                ]["service_level"] = new_service

                simulation.nodes[
                    node
                ]["operational"] = (
                    new_service > 0.0
                )

                affected.add(node)

                changed = True

    return simulation, sorted(affected)


def calculate_system_service(G):
    """
    Calculate average service level across
    all infrastructure nodes.
    """

    if len(G.nodes) == 0:
        return 0.0

    total_service = 0.0

    for node in G.nodes:

        total_service += G.nodes[
            node
        ].get(
            "service_level",
            1.0
        )

    return (
        total_service
        / len(G.nodes)
    )


def calculate_critical_service(G):
    """
    Calculate average service of critical facilities.
    """

    critical_nodes = [
        "Hospital",
        "Emergency_Center",
        "Industrial_Plant"
    ]

    values = []

    for node in critical_nodes:

        if node in G.nodes:

            values.append(
                G.nodes[node].get(
                    "service_level",
                    1.0
                )
            )

    if not values:
        return 0.0

    return sum(values) / len(values)


def main():

    print("=" * 80)
    print("EARTH-N — SEVERITY-AWARE CASCADE ENGINE")
    print("=" * 80)

    temperatures = [
        10,
        15,
        20
    ]

    for temperature in temperatures:

        print(
            f"\nHEATWAVE: +{temperature}°C"
        )

        # Build fresh network.
        network = create_earth_network()

        # Import heatwave functions.
        from disaster_engine import (
            apply_heatwave,
            calculate_grid_stress,
            trigger_grid_failure,
            apply_failure_severity
        )

        network.graph[
            "base_electricity_demand"
        ] = 300.0

        network.graph[
            "grid_capacity"
        ] = 400.0

        network = apply_heatwave(
            network,
            temperature
        )

        stress = calculate_grid_stress(
            network
        )

        failed_node, severity = (
            trigger_grid_failure(
                network
            )
        )

        if failed_node is None:

            print(
                f"Grid stress: {stress:.2f}%"
            )

            print(
                "No grid failure."
            )

            continue

        network = apply_failure_severity(
            network,
            failed_node,
            severity
        )

        simulation, affected = (
            simulate_cascade(
                network,
                failed_node
            )
        )

        system_service = (
            calculate_system_service(
                simulation
            )
        )

        critical_service = (
            calculate_critical_service(
                simulation
            )
        )

        print(
            f"Grid stress: {stress:.2f}%"
        )

        print(
            f"Failure severity: {severity:.2f}"
        )

        print(
            f"System service: "
            f"{system_service * 100:.2f}%"
        )

        print(
            f"Critical service: "
            f"{critical_service * 100:.2f}%"
        )

        print(
            f"Affected nodes: "
            f"{len(affected)}"
        )

    print(
        "\nEARTH-N SEVERITY-AWARE "
        "CASCADE COMPLETE"
    )


if __name__ == "__main__":
    main()