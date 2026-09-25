import sys
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SIMULATION_DIR))


# ============================================================
# EARTH-N MODULES
# ============================================================

from city_model import create_earth_network

from cascade_engine import (
    simulate_cascade,
    calculate_system_service
)

from ai.intervention_engine import (
    apply_intervention
)


# ============================================================
# CRITICAL INFRASTRUCTURE
# ============================================================

CRITICAL_FACILITIES = [
    "Hospital",
    "Emergency_Center",
    "Industrial_Plant"
]


# ============================================================
# SIMULATED INTERVENTION COSTS
# ============================================================

INTERVENTION_COSTS = {
    "Hospital": 30,
    "Emergency_Center": 20,
    "Industrial_Plant": 40
}


# ============================================================
# CRITICAL SERVICE CALCULATION
# ============================================================

def calculate_critical_service(G):
    """
    Calculate the average service level of
    critical infrastructure.
    """

    service_levels = []

    for node in CRITICAL_FACILITIES:

        if node in G.nodes:

            service_levels.append(
                G.nodes[node]["service_level"]
            )

    if not service_levels:
        return 0.0

    return sum(service_levels) / len(service_levels)


# ============================================================
# CASCADING RESILIENCE INDEX
# ============================================================

def calculate_cri(
    system_service,
    critical_service,
    intervention_cost
):
    """
    Calculate the Cascading Resilience Index (CRI).

    Prototype weighting:

        50% = Overall system service
        40% = Critical infrastructure service
        10% = Intervention cost efficiency

    Higher CRI represents better simulated resilience.
    """

    cost_score = max(
        0,
        1 - (intervention_cost / 100)
    )

    cri = (
        0.50 * system_service
        + 0.40 * critical_service
        + 0.10 * cost_score
    )

    return cri


# ============================================================
# SCENARIO EVALUATION
# ============================================================

def evaluate_scenario(
    target_node=None
):
    """
    Simulate a GridStation failure and optionally
    apply an Earth-N intervention.
    """

    # --------------------------------------------------------
    # CREATE FRESH NETWORK
    # --------------------------------------------------------

    network = create_earth_network()

    # --------------------------------------------------------
    # INITIAL FAILURE
    # --------------------------------------------------------

    failed_node = "GridStation"

    simulation, affected = simulate_cascade(
        network,
        failed_node
    )

    # --------------------------------------------------------
    # INTERVENTION COST
    # --------------------------------------------------------

    intervention_cost = 0

    # --------------------------------------------------------
    # APPLY INTERVENTION
    # --------------------------------------------------------

    if target_node:

        intervention_cost = INTERVENTION_COSTS[
            target_node
        ]

        simulation = apply_intervention(
            simulation,
            target_node
        )

    # --------------------------------------------------------
    # CALCULATE PERFORMANCE
    # --------------------------------------------------------

    system_service = calculate_system_service(
        simulation
    )

    critical_service = calculate_critical_service(
        simulation
    )

    # --------------------------------------------------------
    # CALCULATE CRI
    # --------------------------------------------------------

    cri = calculate_cri(
        system_service,
        critical_service,
        intervention_cost
    )

    return (
        system_service,
        critical_service,
        intervention_cost,
        cri
    )


# ============================================================
# MAIN RESILIENCE ANALYSIS
# ============================================================

def run_resilience_analysis():

    print("=" * 70)
    print("EARTH-N — CASCADING RESILIENCE INDEX")
    print("=" * 70)

    # --------------------------------------------------------
    # SCENARIOS
    # --------------------------------------------------------

    scenarios = [
        None,
        "Hospital",
        "Emergency_Center",
        "Industrial_Plant"
    ]

    results = []

    # --------------------------------------------------------
    # EVALUATE EACH SCENARIO
    # --------------------------------------------------------

    for scenario in scenarios:

        (
            system_service,
            critical_service,
            cost,
            cri
        ) = evaluate_scenario(
            scenario
        )

        if scenario is None:

            name = "No Intervention"

        else:

            name = scenario

        results.append(
            (
                name,
                system_service,
                critical_service,
                cost,
                cri
            )
        )

    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    print("\nSCENARIO RESULTS")
    print("-" * 70)

    for (
        name,
        system_service,
        critical_service,
        cost,
        cri
    ) in results:

        print(
            f"{name:20} | "
            f"System: {system_service * 100:6.2f}% | "
            f"Critical: {critical_service * 100:6.2f}% | "
            f"Cost: {cost:5.1f} | "
            f"CRI: {cri * 100:6.2f}"
        )

    # --------------------------------------------------------
    # FIND HIGHEST CRI
    # --------------------------------------------------------

    best = max(
        results,
        key=lambda item: item[4]
    )

    print("\nHIGHEST CRI SCENARIO")
    print("-" * 70)

    print(
        f"Scenario: {best[0]}"
    )

    print(
        f"CRI: {best[4] * 100:.2f}"
    )

    # --------------------------------------------------------
    # RESEARCH NOTE
    # --------------------------------------------------------

    print(
        "\nNOTE: CRI is a prototype research metric "
        "for the Earth-N simulation."
    )

    print(
        "\nEARTH-N RESILIENCE ANALYSIS COMPLETE"
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_resilience_analysis()