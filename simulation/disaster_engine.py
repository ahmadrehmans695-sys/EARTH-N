"""
EARTH-N Disaster Engine

Simulates heatwave-driven electricity demand stress
and determines whether the grid reaches failure.

This is a prototype research model using illustrative assumptions.
"""


def calculate_grid_stress(
    base_grid_stress=0.75,
    temperature_increase=0
):
    """
    Estimate grid stress caused by a temperature increase.

    Prototype assumption:
    electricity demand increases by 4% of base demand
    for every 1°C temperature increase.
    """

    demand_increase = 0.04 * temperature_increase

    grid_stress = base_grid_stress + demand_increase

    return grid_stress


def calculate_failure_severity(grid_stress):
    """
    Calculate grid failure severity.

    Failure occurs when grid stress exceeds 100%.

    Severity is based on overload above 100%.
    """

    failure_threshold = 1.0

    if grid_stress <= failure_threshold:
        return False, 0.0

    overload = grid_stress - failure_threshold

    # Prototype severity scale:
    # 20% overload = severity 1.0
    severity = overload / 0.20

    return True, severity


def determine_failed_node(graph):
    """
    Identify the primary grid node affected by the heatwave.

    For the current prototype, GridStation is the main
    transmission/distribution failure point.
    """

    if "GridStation" in graph.nodes:
        return "GridStation"

    return None


def simulate_heatwave(
    graph,
    temperature_increase=0
):
    """
    Run the complete heatwave scenario.

    Returns:
        grid_stress
        failure_triggered
        severity
        failed_node
        temperature_increase
    """

    grid_stress = calculate_grid_stress(
        base_grid_stress=0.75,
        temperature_increase=temperature_increase
    )

    failure_triggered, severity = calculate_failure_severity(
        grid_stress
    )

    failed_node = None

    if failure_triggered:
        failed_node = determine_failed_node(graph)

    return {
        "temperature_increase": temperature_increase,
        "grid_stress": grid_stress,
        "failure_triggered": failure_triggered,
        "severity": severity,
        "failed_node": failed_node,
    }


# ---------------------------------------------------------
# DIRECT TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print("EARTH-N Disaster Engine Test")
    print("-" * 40)

    for temperature in [0, 5, 10, 15, 20]:

        result = simulate_heatwave(
            graph=None,
            temperature_increase=temperature
        )

        print(
            f"+{temperature}°C | "
            f"Grid Stress: "
            f"{result['grid_stress'] * 100:.1f}% | "
            f"Failure: "
            f"{result['failure_triggered']} | "
            f"Severity: "
            f"{result['severity']:.2f}"
        )