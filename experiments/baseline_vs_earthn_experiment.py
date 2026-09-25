import sys
from pathlib import Path
import csv


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SIMULATION_DIR = PROJECT_ROOT / "simulation"
AI_DIR = PROJECT_ROOT / "ai"

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
# OUTPUT
# =========================================================

RESULTS_DIR = PROJECT_ROOT / "results"

RESULTS_DIR.mkdir(
    exist_ok=True
)

OUTPUT_FILE = (
    RESULTS_DIR
    / "earthn_baseline_vs_intervention.csv"
)


# =========================================================
# RUN ONE SCENARIO
# =========================================================

def run_scenario(temperature):

    # -----------------------------------------------------
    # CREATE FRESH NETWORK
    # -----------------------------------------------------

    network = create_earth_network()

    # -----------------------------------------------------
    # HEATWAVE
    # -----------------------------------------------------

    disaster = simulate_heatwave(
        network,
        temperature_increase=temperature,
    )

    grid_stress = disaster["grid_stress"]

    failure = disaster["failure_triggered"]

    severity = disaster["severity"]

    failed_node = disaster["failed_node"]

    # -----------------------------------------------------
    # NO FAILURE
    # -----------------------------------------------------

    if not failure:

        system_service = calculate_system_service(
            network
        )

        critical_service = calculate_critical_service(
            network
        )

        return {
            "temperature_c": temperature,
            "grid_stress_percent": grid_stress * 100,
            "failure": "NO",
            "severity": 0.0,
            "baseline_system_service_percent":
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
    # APPLY FAILURE SEVERITY
    # -----------------------------------------------------

    network.nodes[failed_node][
        "failure_severity"
    ] = severity

    # -----------------------------------------------------
    # BASELINE CASCADE
    # -----------------------------------------------------

    baseline_network, affected = simulate_cascade(
        network,
        failed_node,
    )

    baseline_system_service = calculate_system_service(
        baseline_network
    )

    baseline_critical_service = calculate_critical_service(
        baseline_network
    )

    # -----------------------------------------------------
    # INTERVENTION TARGETS
    # -----------------------------------------------------

    targets = [
        "Hospital",
        "Emergency_Center",
        "Industrial_Plant",
    ]

    intervention_results = {}

    # -----------------------------------------------------
    # TEST EACH INTERVENTION
    # -----------------------------------------------------

    for target in targets:

        test_network = create_earth_network()

        test_network.nodes[failed_node][
            "failure_severity"
        ] = severity

        test_simulation, test_affected = simulate_cascade(
            test_network,
            failed_node,
        )

        test_simulation = apply_intervention(
            test_simulation,
            target,
        )

        service = calculate_system_service(
            test_simulation
        )

        intervention_results[target] = service

    # -----------------------------------------------------
    # EXTRACT RESULTS
    # -----------------------------------------------------

    hospital_service = intervention_results[
        "Hospital"
    ]

    emergency_service = intervention_results[
        "Emergency_Center"
    ]

    industrial_service = intervention_results[
        "Industrial_Plant"
    ]

    # -----------------------------------------------------
    # SELECT INTERVENTION
    # -----------------------------------------------------

    selected_intervention = max(
        intervention_results,
        key=intervention_results.get,
    )

    earthn_service = intervention_results[
        selected_intervention
    ]

    improvement = (
        earthn_service
        - baseline_system_service
    )

    # -----------------------------------------------------
    # RETURN RESULTS
    # -----------------------------------------------------

    return {
        "temperature_c": temperature,
        "grid_stress_percent":
            grid_stress * 100,
        "failure": "YES",
        "severity": severity,
        "baseline_system_service_percent":
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
# MAIN EXPERIMENT
# =========================================================

def main():

    print("=" * 90)
    print("EARTH-N — BASELINE VS COORDINATED INTERVENTION")
    print("=" * 90)

    results = []

    for temperature in range(0, 21):

        result = run_scenario(
            temperature
        )

        results.append(result)

        print(
            f"+{temperature:2d}°C | "
            f"Stress: "
            f"{result['grid_stress_percent']:6.1f}% | "
            f"Failure: "
            f"{result['failure']:3s} | "
            f"Baseline: "
            f"{result['baseline_system_service_percent']:6.1f}% | "
            f"Earth-N: "
            f"{result['earthn_service_percent']:6.1f}% | "
            f"Improvement: "
            f"{result['improvement_percentage_points']:6.1f}"
        )

    # =====================================================
    # SAVE CSV
    # =====================================================

    fieldnames = [
        "temperature_c",
        "grid_stress_percent",
        "failure",
        "severity",
        "baseline_system_service_percent",
        "baseline_critical_service_percent",
        "hospital_service_percent",
        "emergency_center_service_percent",
        "industrial_plant_service_percent",
        "selected_intervention",
        "earthn_service_percent",
        "improvement_percentage_points",
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

        writer.writerows(results)

    # =====================================================
    # SUMMARY
    # =====================================================

    failure_results = [
        row
        for row in results
        if row["failure"] == "YES"
    ]

    if failure_results:

        average_improvement = (
            sum(
                row[
                    "improvement_percentage_points"
                ]
                for row in failure_results
            )
            / len(failure_results)
        )

        print()
        print(
            "Average simulated improvement "
            "after failure: "
            f"{average_improvement:.2f} "
            "percentage points"
        )

    print()
    print("=" * 90)
    print("EXPERIMENT COMPLETE")
    print("=" * 90)
    print()
    print(
        f"Results saved to:\n{OUTPUT_FILE}"
    )
    print()
    print("=" * 90)


if __name__ == "__main__":
    main()