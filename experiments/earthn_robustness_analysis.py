from pathlib import Path
import sys
import csv
import random


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SIMULATION_DIR = PROJECT_ROOT / "simulation"
AI_DIR = PROJECT_ROOT / "ai"
RESULTS_DIR = PROJECT_ROOT / "results"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SIMULATION_DIR))
sys.path.insert(0, str(AI_DIR))


# ============================================================
# IMPORTS
# ============================================================

from city_model import create_earth_network

from disaster_engine import simulate_heatwave

from cascade_engine import (
    simulate_cascade,
    calculate_system_service,
)

from intervention_engine import apply_intervention


# ============================================================
# CONFIGURATION
# ============================================================

NUMBER_OF_RUNS = 100

TEMPERATURES = [
    7,
    8,
    9,
    10,
    11,
    12,
]

RANDOM_SEED = 42

DEPENDENCY_VARIATION = 0.20


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_FILE = (
    RESULTS_DIR
    / "earthn_robustness_results.csv"
)


# ============================================================
# RANDOMIZE DEPENDENCIES
# ============================================================

def randomize_dependencies(
    network,
    rng
):
    """
    Randomly vary each dependency strength by ±20%.

    Values remain between 0 and 1.
    """

    for source, target, data in network.edges(
        data=True
    ):

        original = data.get(
            "dependency_strength",
            1.0
        )

        variation = rng.uniform(
            -DEPENDENCY_VARIATION,
            DEPENDENCY_VARIATION
        )

        randomized = (
            original
            * (1.0 + variation)
        )

        randomized = max(
            0.0,
            min(1.0, randomized)
        )

        data[
            "dependency_strength"
        ] = randomized


# ============================================================
# RUN ONE SCENARIO
# ============================================================

def run_scenario(
    temperature,
    rng
):

    # --------------------------------------------------------
    # BASELINE NETWORK
    # --------------------------------------------------------

    baseline_network = (
        create_earth_network()
    )

    randomize_dependencies(
        baseline_network,
        rng
    )

    disaster = simulate_heatwave(
        baseline_network,
        temperature_increase=temperature,
    )

    if not disaster[
        "failure_triggered"
    ]:

        return None

    failed_node = disaster[
        "failed_node"
    ]

    severity = disaster[
        "severity"
    ]

    # --------------------------------------------------------
    # BASELINE CASCADE
    # --------------------------------------------------------

    baseline_network.nodes[
        failed_node
    ][
        "failure_severity"
    ] = severity

    baseline_simulation, affected = (
        simulate_cascade(
            baseline_network,
            failed_node,
        )
    )

    baseline_service = (
        calculate_system_service(
            baseline_simulation
        )
    )

    # --------------------------------------------------------
    # TEST EARTH-N INTERVENTIONS
    # --------------------------------------------------------

    targets = [
        "Hospital",
        "Emergency_Center",
        "Industrial_Plant",
    ]

    intervention_results = {}

    for target in targets:

        test_network = (
            create_earth_network()
        )

        # Use the same randomized dependency
        # configuration as the baseline case.
        for source, destination, data in (
            baseline_network.edges(
                data=True
            )
        ):

            test_network.edges[
                source,
                destination
            ][
                "dependency_strength"
            ] = data[
                "dependency_strength"
            ]

        test_network.nodes[
            failed_node
        ][
            "failure_severity"
        ] = severity

        test_simulation, _ = (
            simulate_cascade(
                test_network,
                failed_node,
            )
        )

        test_simulation = (
            apply_intervention(
                test_simulation,
                target,
            )
        )

        service = (
            calculate_system_service(
                test_simulation
            )
        )

        intervention_results[
            target
        ] = service

    # --------------------------------------------------------
    # SELECT BEST INTERVENTION
    # --------------------------------------------------------

    selected_intervention = max(
        intervention_results,
        key=intervention_results.get,
    )

    earthn_service = (
        intervention_results[
            selected_intervention
        ]
    )

    improvement = (
        earthn_service
        - baseline_service
    )

    return {
        "temperature_c": temperature,
        "baseline_service_percent":
            baseline_service * 100,
        "earthn_service_percent":
            earthn_service * 100,
        "improvement_percentage_points":
            improvement * 100,
        "selected_intervention":
            selected_intervention,
        "affected_nodes":
            len(affected),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 90)
    print(
        "EARTH-N — RANDOMIZED ROBUSTNESS ANALYSIS"
    )
    print("=" * 90)

    rng = random.Random(
        RANDOM_SEED
    )

    all_results = []

    total_scenarios = (
        NUMBER_OF_RUNS
        * len(TEMPERATURES)
    )

    completed = 0

    for run_number in range(
        1,
        NUMBER_OF_RUNS + 1
    ):

        for temperature in TEMPERATURES:

            result = run_scenario(
                temperature,
                rng
            )

            if result is None:
                continue

            result[
                "run"
            ] = run_number

            all_results.append(
                result
            )

            completed += 1

    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    fieldnames = [
        "run",
        "temperature_c",
        "baseline_service_percent",
        "earthn_service_percent",
        "improvement_percentage_points",
        "selected_intervention",
        "affected_nodes",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            all_results
        )

    # --------------------------------------------------------
    # CALCULATE SUMMARY
    # --------------------------------------------------------

    improvements = [
        row[
            "improvement_percentage_points"
        ]
        for row in all_results
    ]

    mean_improvement = (
        sum(improvements)
        / len(improvements)
    )

    minimum_improvement = min(
        improvements
    )

    maximum_improvement = max(
        improvements
    )

    positive_results = [
        value
        for value in improvements
        if value > 0
    ]

    positive_rate = (
        len(positive_results)
        / len(improvements)
        * 100
    )

    # --------------------------------------------------------
    # INTERVENTION COUNTS
    # --------------------------------------------------------

    intervention_counts = {}

    for row in all_results:

        target = row[
            "selected_intervention"
        ]

        intervention_counts[
            target
        ] = (
            intervention_counts.get(
                target,
                0
            )
            + 1
        )

    # --------------------------------------------------------
    # OUTPUT SUMMARY
    # --------------------------------------------------------

    print()
    print("-" * 90)
    print("ROBUSTNESS SUMMARY")
    print("-" * 90)

    print(
        f"Runs: {NUMBER_OF_RUNS}"
    )

    print(
        f"Temperature scenarios per run: "
        f"{len(TEMPERATURES)}"
    )

    print(
        f"Total completed scenarios: "
        f"{completed}"
    )

    print(
        f"Dependency variation: "
        f"±{DEPENDENCY_VARIATION * 100:.0f}%"
    )

    print()
    print(
        f"Mean improvement: "
        f"{mean_improvement:.2f} pp"
    )

    print(
        f"Minimum improvement: "
        f"{minimum_improvement:.2f} pp"
    )

    print(
        f"Maximum improvement: "
        f"{maximum_improvement:.2f} pp"
    )

    print(
        f"Positive-improvement scenarios: "
        f"{positive_rate:.2f}%"
    )

    print()
    print("Selected intervention frequency:")

    for target, count in sorted(
        intervention_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        percentage = (
            count
            / len(all_results)
            * 100
        )

        print(
            f"  {target:20s} "
            f"{count:4d} "
            f"({percentage:6.2f}%)"
        )

    print()
    print("=" * 90)
    print("ROBUSTNESS ANALYSIS COMPLETE")
    print("=" * 90)

    print(
        f"\nResults saved to:\n"
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()