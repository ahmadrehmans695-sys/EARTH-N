import sys
from pathlib import Path
import csv


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"

sys.path.insert(0, str(SIMULATION_DIR))


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


# =========================================================
# OUTPUT
# =========================================================

RESULTS_DIR = PROJECT_ROOT / "results"

RESULTS_DIR.mkdir(
    exist_ok=True
)

OUTPUT_FILE = (
    RESULTS_DIR /
    "earthn_heatwave_experiment.csv"
)


# =========================================================
# RUN ONE SCENARIO
# =========================================================

def run_scenario(temperature):

    # Create fresh infrastructure network
    network = create_earth_network()

    # Simulate heatwave
    disaster = simulate_heatwave(
        network,
        temperature_increase=temperature,
    )

    grid_stress = disaster["grid_stress"]

    failure_triggered = disaster[
        "failure_triggered"
    ]

    severity = disaster["severity"]

    failed_node = disaster["failed_node"]

    # -----------------------------------------------------
    # NO FAILURE
    # -----------------------------------------------------

    if not failure_triggered:

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
            "system_service_percent":
                system_service * 100,
            "critical_service_percent":
                critical_service * 100,
            "failed_node": "",
            "affected_nodes": 0,
        }

    # -----------------------------------------------------
    # APPLY FAILURE SEVERITY
    # -----------------------------------------------------

    network.nodes[failed_node][
        "failure_severity"
    ] = severity

    # -----------------------------------------------------
    # CASCADE
    # -----------------------------------------------------

    simulation, affected = simulate_cascade(
        network,
        failed_node,
    )

    # -----------------------------------------------------
    # SERVICE
    # -----------------------------------------------------

    system_service = calculate_system_service(
        simulation
    )

    critical_service = calculate_critical_service(
        simulation
    )

    # -----------------------------------------------------
    # RETURN RESULTS
    # -----------------------------------------------------

    return {
        "temperature_c": temperature,
        "grid_stress_percent": grid_stress * 100,
        "failure": "YES",
        "severity": severity,
        "system_service_percent":
            system_service * 100,
        "critical_service_percent":
            critical_service * 100,
        "failed_node": failed_node,
        "affected_nodes": len(affected),
    }


# =========================================================
# MAIN EXPERIMENT
# =========================================================

def main():

    print("=" * 80)
    print("EARTH-N — HEATWAVE RESILIENCE EXPERIMENT")
    print("=" * 80)

    results = []

    # Test every 1°C from 0°C to 20°C
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
            f"Severity: "
            f"{result['severity']:5.2f} | "
            f"System: "
            f"{result['system_service_percent']:6.1f}% | "
            f"Critical: "
            f"{result['critical_service_percent']:6.1f}%"
        )

    # =====================================================
    # SAVE CSV
    # =====================================================

    fieldnames = [
        "temperature_c",
        "grid_stress_percent",
        "failure",
        "severity",
        "system_service_percent",
        "critical_service_percent",
        "failed_node",
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
            results
        )

    print("\n" + "=" * 80)

    print(
        "Experiment complete."
    )

    print(
        f"Results saved to:\n{OUTPUT_FILE}"
    )

    print("=" * 80)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()