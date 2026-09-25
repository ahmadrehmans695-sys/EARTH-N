import sys
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"
RESULTS_DIR = PROJECT_ROOT / "results"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SIMULATION_DIR))

from city_model import create_earth_network
from cascade_engine import (
    simulate_cascade,
    calculate_system_service,
    calculate_critical_service
)

from disaster_engine import (
    apply_heatwave,
    calculate_grid_stress,
    trigger_grid_failure,
    apply_failure_severity
)


OUTPUT_FILE = RESULTS_DIR / "heatwave_severity_results.csv"


def run_heatwave(temperature_increase):

    network = create_earth_network()

    network.graph["base_electricity_demand"] = 300.0
    network.graph["grid_capacity"] = 400.0

    network = apply_heatwave(
        network,
        temperature_increase
    )

    grid_stress = calculate_grid_stress(network)

    failed_node, severity = trigger_grid_failure(
        network
    )

    if failed_node is None:

        return {
            "temperature_c": temperature_increase,
            "grid_stress_percent": grid_stress,
            "failure": "NO",
            "severity": severity,
            "system_service_percent": 100.0,
            "critical_service_percent": 100.0,
            "failed_node": "",
            "affected_nodes": 0
        }

    network = apply_failure_severity(
        network,
        failed_node,
        severity
    )

    simulation, affected = simulate_cascade(
        network,
        failed_node
    )

    system_service = calculate_system_service(
        simulation
    )

    critical_service = calculate_critical_service(
        simulation
    )

    return {
        "temperature_c": temperature_increase,
        "grid_stress_percent": grid_stress,
        "failure": "YES",
        "severity": severity,
        "system_service_percent": system_service * 100.0,
        "critical_service_percent": critical_service * 100.0,
        "failed_node": failed_node,
        "affected_nodes": len(affected)
    }


def save_results(results):

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "temperature_c",
        "grid_stress_percent",
        "failure",
        "severity",
        "system_service_percent",
        "critical_service_percent",
        "failed_node",
        "affected_nodes"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(results)


def run_heatwave_sweep():

    print("=" * 90)
    print(
        "EARTH-N — SEVERITY-AWARE "
        "HEATWAVE EXPERIMENT"
    )
    print("=" * 90)

    temperatures = [
        0,
        5,
        10,
        15,
        20
    ]

    results = []

    for temperature in temperatures:

        result = run_heatwave(
            temperature
        )

        results.append(result)

    save_results(results)

    print("\nRESULTS")
    print("-" * 90)

    print(
        f"{'Temp':>8} | "
        f"{'Grid Stress':>12} | "
        f"{'Failure':>10} | "
        f"{'Severity':>10} | "
        f"{'System':>10} | "
        f"{'Critical':>10}"
    )

    print("-" * 90)

    for result in results:

        print(
            f"{result['temperature_c']:>7}°C | "
            f"{result['grid_stress_percent']:>10.2f}% | "
            f"{result['failure']:>10} | "
            f"{result['severity']:>9.2f} | "
            f"{result['system_service_percent']:>8.2f}% | "
            f"{result['critical_service_percent']:>8.2f}%"
        )

    threshold = None

    for result in results:

        if result["failure"] == "YES":

            threshold = result["temperature_c"]

            break

    print("\nHEATWAVE FAILURE THRESHOLD")
    print("-" * 90)

    if threshold is not None:

        print(
            f"First tested temperature causing "
            f"grid failure: +{threshold}°C"
        )

    else:

        print(
            "No tested temperature caused grid failure."
        )

    print("\nRESULT FILE")
    print("-" * 90)

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print(
        "\nEARTH-N SEVERITY EXPERIMENT COMPLETE"
    )


if __name__ == "__main__":

    run_heatwave_sweep()