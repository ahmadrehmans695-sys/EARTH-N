from pathlib import Path
import sys
import csv


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SIMULATION_DIR = PROJECT_ROOT / "simulation"
AI_DIR = PROJECT_ROOT / "ai"
RESULTS_DIR = PROJECT_ROOT / "results"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SIMULATION_DIR))
sys.path.insert(0, str(AI_DIR))


# =========================================================
# IMPORTS
# =========================================================

from city_model import create_earth_network

from disaster_engine import simulate_heatwave

from cascade_engine import (
    simulate_cascade,
    calculate_system_service,
    calculate_critical_service,
)

from intervention_engine import apply_intervention


# =========================================================
# SENSITIVITY CONDITIONS
# =========================================================

DEPENDENCY_SCENARIOS = {
    "Lower": {
        "scale": 0.80,
        "description": "20% weaker dependencies",
    },
    "Base": {
        "scale": 1.00,
        "description": "Original dependency strengths",
    },
    "Higher": {
        "scale": 1.20,
        "description": "20% stronger dependencies",
    },
}


# =========================================================
# OUTPUT FILES
# =========================================================

DETAILED_FILE = (
    RESULTS_DIR
    / "earthn_sensitivity_results.csv"
)

SUMMARY_FILE = (
    RESULTS_DIR
    / "earthn_sensitivity_summary.csv"
)


# =========================================================
# SCALE DEPENDENCY STRENGTHS
# =========================================================

def scale_dependencies(
    network,
    scale
):
    """
    Scale dependency strengths for sensitivity testing.

    Values are kept between 0 and 1.
    """

    for source, target, data in network.edges(
        data=True
    ):

        original = data.get(
            "dependency_strength",
            1.0
        )

        scaled = original * scale

        scaled = max(
            0.0,
            min(1.0, scaled)
        )

        data[
            "dependency_strength"
        ] = scaled


# =========================================================
# CREATE NETWORK FOR A SCENARIO
# =========================================================

def create_scenario_network(
    dependency_scale
):
    """
    Create a fresh EARTH-N network and apply
    the selected dependency scaling.
    """

    network = create_earth_network()

    scale_dependencies(
        network,
        dependency_scale
    )

    return network


# =========================================================
# RUN ONE TEMPERATURE
# =========================================================

def run_scenario(
    temperature,
    dependency_scale
):

    # -----------------------------------------------------
    # CREATE FRESH NETWORK
    # -----------------------------------------------------

    network = create_scenario_network(
        dependency_scale
    )

    # -----------------------------------------------------
    # HEATWAVE
    # -----------------------------------------------------

    disaster = simulate_heatwave(
        network,
        temperature_increase=temperature,
    )

    grid_stress = disaster[
        "grid_stress"
    ]

    failure = disaster[
        "failure_triggered"
    ]

    severity = disaster[
        "severity"
    ]

    failed_node = disaster[
        "failed_node"
    ]

    # -----------------------------------------------------
    # NO FAILURE
    # -----------------------------------------------------

    if not failure:

        system_service = (
            calculate_system_service(
                network
            )
        )

        critical_service = (
            calculate_critical_service(
                network
            )
        )

        return {
            "temperature_c": temperature,

            "grid_stress_percent":
                grid_stress * 100,

            "failure": "NO",

            "severity": 0.0,

            "baseline_service_percent":
                system_service * 100,

            "baseline_critical_service_percent":
                critical_service * 100,

            "hospital_service_percent":
                system_service * 100,

            "emergency_center_service_percent":
                system_service * 100,

            "industrial_plant_service_percent":
                system_service * 100,

            "selected_intervention": "",

            "earthn_service_percent":
                system_service * 100,

            "improvement_percentage_points":
                0.0,
        }

    # -----------------------------------------------------
    # BASELINE
    # -----------------------------------------------------

    baseline_network = (
        create_scenario_network(
            dependency_scale
        )
    )

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

    baseline_system_service = (
        calculate_system_service(
            baseline_simulation
        )
    )

    baseline_critical_service = (
        calculate_critical_service(
            baseline_simulation
        )
    )

    # -----------------------------------------------------
    # TEST INTERVENTIONS
    # -----------------------------------------------------

    targets = [
        "Hospital",
        "Emergency_Center",
        "Industrial_Plant",
    ]

    intervention_results = {}

    for target in targets:

        # IMPORTANT:
        # Each intervention starts from a fresh
        # scenario network, just like the validated
        # baseline-vs-Earth-N experiment.

        test_network = (
            create_scenario_network(
                dependency_scale
            )
        )

        test_network.nodes[
            failed_node
        ][
            "failure_severity"
        ] = severity

        test_simulation, test_affected = (
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

    # -----------------------------------------------------
    # SELECT INTERVENTION
    # -----------------------------------------------------

    selected_intervention = max(
        intervention_results,
        key=intervention_results.get,
    )

    earthn_service = (
        intervention_results[
            selected_intervention
        ]
    )

    # -----------------------------------------------------
    # INDIVIDUAL INTERVENTION RESULTS
    # -----------------------------------------------------

    hospital_service = (
        intervention_results[
            "Hospital"
        ]
    )

    emergency_service = (
        intervention_results[
            "Emergency_Center"
        ]
    )

    industrial_service = (
        intervention_results[
            "Industrial_Plant"
        ]
    )

    # -----------------------------------------------------
    # IMPROVEMENT
    # -----------------------------------------------------

    improvement = (
        earthn_service
        - baseline_system_service
    )

    # -----------------------------------------------------
    # RETURN
    # -----------------------------------------------------

    return {
        "temperature_c": temperature,

        "grid_stress_percent":
            grid_stress * 100,

        "failure": "YES",

        "severity": severity,

        "baseline_service_percent":
            baseline_system_service * 100,

        "baseline_critical_service_percent":
            baseline_critical_service * 100,

        "hospital_service_percent":
            hospital_service * 100,

        "emergency_center_service_percent":
            emergency_service * 100,

        "industrial_plant_service_percent":
            industrial_service * 100,

        "selected_intervention":
            selected_intervention,

        "earthn_service_percent":
            earthn_service * 100,

        "improvement_percentage_points":
            improvement * 100,
    }


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 90)
    print(
        "EARTH-N — DEPENDENCY SENSITIVITY ANALYSIS"
    )
    print("=" * 90)

    all_results = []

    # -----------------------------------------------------
    # RUN ALL CONDITIONS
    # -----------------------------------------------------

    for scenario_name, scenario_info in (
        DEPENDENCY_SCENARIOS.items()
    ):

        scale = scenario_info[
            "scale"
        ]

        print()
        print(
            f"Running: {scenario_name} "
            f"({scenario_info['description']})"
        )

        for temperature in range(0, 21):

            result = run_scenario(
                temperature,
                scale
            )

            result[
                "dependency_scenario"
            ] = scenario_name

            result[
                "dependency_scale"
            ] = scale

            all_results.append(
                result
            )

    # -----------------------------------------------------
    # SAVE DETAILED RESULTS
    # -----------------------------------------------------

    fieldnames = [
        "temperature_c",
        "grid_stress_percent",
        "failure",
        "severity",
        "baseline_service_percent",
        "baseline_critical_service_percent",
        "hospital_service_percent",
        "emergency_center_service_percent",
        "industrial_plant_service_percent",
        "selected_intervention",
        "earthn_service_percent",
        "improvement_percentage_points",
        "dependency_scenario",
        "dependency_scale",
    ]

    with open(
        DETAILED_FILE,
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

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    summary_rows = []

    for scenario_name in (
        DEPENDENCY_SCENARIOS.keys()
    ):

        rows = [
            row
            for row in all_results
            if (
                row[
                    "dependency_scenario"
                ]
                == scenario_name
                and row[
                    "failure"
                ]
                == "YES"
            )
        ]

        if not rows:
            continue

        improvements = [
            row[
                "improvement_percentage_points"
            ]
            for row in rows
        ]

        baselines = [
            row[
                "baseline_service_percent"
            ]
            for row in rows
        ]

        earthn_values = [
            row[
                "earthn_service_percent"
            ]
            for row in rows
        ]

        summary_rows.append(
            {
                "dependency_scenario":
                    scenario_name,

                "dependency_scale":
                    DEPENDENCY_SCENARIOS[
                        scenario_name
                    ]["scale"],

                "failure_scenarios":
                    len(rows),

                "mean_baseline_service_percent":
                    sum(baselines)
                    / len(baselines),

                "mean_earthn_service_percent":
                    sum(earthn_values)
                    / len(earthn_values),

                "mean_improvement_percentage_points":
                    sum(improvements)
                    / len(improvements),

                "minimum_improvement_percentage_points":
                    min(improvements),

                "maximum_improvement_percentage_points":
                    max(improvements),
            }
        )

    # -----------------------------------------------------
    # SAVE SUMMARY
    # -----------------------------------------------------

    with open(
        SUMMARY_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "dependency_scenario",
            "dependency_scale",
            "failure_scenarios",
            "mean_baseline_service_percent",
            "mean_earthn_service_percent",
            "mean_improvement_percentage_points",
            "minimum_improvement_percentage_points",
            "maximum_improvement_percentage_points",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            summary_rows
        )

    # -----------------------------------------------------
    # PRINT SUMMARY
    # -----------------------------------------------------

    print()
    print("-" * 90)
    print(
        "FAILURE-SCENARIO SENSITIVITY SUMMARY"
    )
    print("-" * 90)

    for row in summary_rows:

        print(
            f"{row['dependency_scenario']:8s} | "
            f"Scale: {row['dependency_scale']:.2f} | "
            f"Baseline: "
            f"{row['mean_baseline_service_percent']:.2f}% | "
            f"Earth-N: "
            f"{row['mean_earthn_service_percent']:.2f}% | "
            f"Mean improvement: "
            f"{row['mean_improvement_percentage_points']:.2f} pp | "
            f"Range: "
            f"{row['minimum_improvement_percentage_points']:.2f}–"
            f"{row['maximum_improvement_percentage_points']:.2f} pp"
        )

    # -----------------------------------------------------
    # FILES
    # -----------------------------------------------------

    print()
    print("=" * 90)
    print("FILES CREATED")
    print("=" * 90)

    print(
        f"Detailed results:\n{DETAILED_FILE}"
    )

    print(
        f"\nSummary:\n{SUMMARY_FILE}"
    )

    print()
    print(
        "Sensitivity analysis completed successfully."
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()