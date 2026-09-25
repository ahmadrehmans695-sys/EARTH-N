from pathlib import Path
import sys

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"
AI_DIR = PROJECT_ROOT / "ai"
RESULTS_DIR = PROJECT_ROOT / "results"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SIMULATION_DIR))
sys.path.insert(0, str(AI_DIR))


# ============================================================
# EARTH-N ENGINE
# ============================================================

from city_model import create_earth_network

from disaster_engine import simulate_heatwave

from cascade_engine import (
    simulate_cascade,
    calculate_system_service,
    calculate_critical_service,
)

from intervention_engine import apply_intervention


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="EARTH-N | Infrastructure Intelligence",
    page_icon="🌍",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🌍 EARTH-N")

st.subheader(
    "Infrastructure Resilience Intelligence"
)

st.write(
    "A prototype intelligence layer for detecting, "
    "understanding, and responding to cascading "
    "infrastructure failures."
)


# ============================================================
# SIDEBAR — SCENARIO LABORATORY
# ============================================================

with st.sidebar:

    st.header("Scenario Laboratory")

    st.subheader("Scenario")

    temperature = st.slider(
        "Heatwave Temperature Increase",
        min_value=0,
        max_value=20,
        value=10,
        step=1,
    )

    st.write(
        f"Current scenario: **+{temperature}°C**"
    )

    st.divider()

    st.subheader("Prototype scope")

    st.write(
        """
        • Electricity  
        • Water  
        • Telecom  
        • Transport  
        • Critical facilities
        """
    )

    st.divider()

    st.caption(
        "Prototype model using illustrative "
        "infrastructure assumptions."
    )


# ============================================================
# RUN HEATWAVE
# ============================================================

network = create_earth_network()

heatwave_result = simulate_heatwave(
    network,
    temperature_increase=temperature,
)

grid_stress = heatwave_result["grid_stress"]
failure_triggered = heatwave_result["failure_triggered"]
severity = heatwave_result["severity"]
failed_node = heatwave_result["failed_node"]


# ============================================================
# BASELINE CASCADE
# ============================================================

baseline_network = create_earth_network()

if failure_triggered and failed_node:

    baseline_network.nodes[
        failed_node
    ]["failure_severity"] = severity

    baseline_simulation, baseline_affected = (
        simulate_cascade(
            baseline_network,
            failed_node,
        )
    )

else:

    baseline_simulation = baseline_network
    baseline_affected = []


baseline_service = calculate_system_service(
    baseline_simulation
)

critical_service = calculate_critical_service(
    baseline_simulation
)


# ============================================================
# EARTH-N INTERVENTION ENGINE
# ============================================================

intervention_targets = [
    "Hospital",
    "Emergency_Center",
    "Industrial_Plant",
]

intervention_results = []

if failure_triggered and failed_node:

    for target in intervention_targets:

        test_network = create_earth_network()

        test_network.nodes[
            failed_node
        ]["failure_severity"] = severity

        test_simulation, _ = simulate_cascade(
            test_network,
            failed_node,
        )

        protected_network = apply_intervention(
            test_simulation,
            target,
        )

        service = calculate_system_service(
            protected_network
        )

        intervention_results.append(
            {
                "target": target,
                "service": service,
            }
        )

    best_result = max(
        intervention_results,
        key=lambda item: item["service"],
    )

    selected_intervention = best_result[
        "target"
    ]

    earthn_service = best_result[
        "service"
    ]

else:

    selected_intervention = (
        "No intervention required"
    )

    earthn_service = baseline_service


improvement = (
    earthn_service -
    baseline_service
)


# ============================================================
# LIVE INFRASTRUCTURE STATUS
# ============================================================

st.header("Live Infrastructure Status")

st.write(
    "Current state of the simulated infrastructure network."
)

m1, m2, m3, m4 = st.columns(4)

with m1:

    st.metric(
        "Temperature",
        f"+{temperature} °C",
    )

with m2:

    st.metric(
        "Grid Stress",
        f"{grid_stress * 100:.1f}%",
    )

with m3:

    st.metric(
        "Baseline Service",
        f"{baseline_service * 100:.1f}%",
    )

with m4:

    st.metric(
        "Earth-N Service",
        f"{earthn_service * 100:.1f}%",
        delta=f"{improvement * 100:.1f} pp",
    )


if failure_triggered:

    st.warning(
        f"Grid stress exceeded the simulated "
        f"failure threshold. "
        f"Earth-N simulated improvement: "
        f"+{improvement * 100:.1f} percentage points."
    )

else:

    st.success(
        "No infrastructure cascade was triggered "
        "under the current scenario."
    )


# ============================================================
# CASCADE ANALYSIS
# ============================================================

st.header("Cascade Analysis")

st.write(
    "Detection and propagation of infrastructure "
    "service loss."
)

c1, c2, c3, c4 = st.columns(4)

with c1:

    if failure_triggered:

        st.error(
            f"Grid failure detected — {failed_node}"
        )

    else:

        st.success(
            "No grid failure detected"
        )


with c2:

    st.metric(
        "Failure Severity",
        f"{severity:.2f}",
    )


with c3:

    st.metric(
        "Critical Service",
        f"{critical_service * 100:.1f}%",
    )


with c4:

    st.metric(
        "Affected Infrastructure",
        len(baseline_affected),
    )


# ============================================================
# INTERVENTION ENGINE
# ============================================================

st.header("Earth-N Intervention Engine")

st.write(
    "Earth-N evaluates multiple protection targets "
    "and identifies the intervention producing the "
    "highest simulated system service."
)

if failure_triggered:

    st.success(
        f"Selected intervention: "
        f"**{selected_intervention.replace('_', ' ')}**"
    )

    st.write(
        f"Simulated improvement: "
        f"**+{improvement * 100:.1f} percentage points**"
    )

    if intervention_results:

        intervention_df = pd.DataFrame(
            intervention_results
        )

        intervention_df[
            "target"
        ] = intervention_df[
            "target"
        ].str.replace(
            "_",
            " ",
        )

        intervention_df[
            "service"
        ] = (
            intervention_df[
                "service"
            ] * 100
        ).round(1)

        intervention_df = (
            intervention_df.rename(
                columns={
                    "target":
                        "Protection Target",
                    "service":
                        "System Service (%)",
                }
            )
        )

        st.dataframe(
            intervention_df,
            width="stretch",
            hide_index=True,
        )

else:

    st.info(
        "No intervention is required because "
        "the network has not entered a failure state."
    )


# ============================================================
# EXPERIMENTAL EVIDENCE
# ============================================================

st.header("Experimental Evidence")

st.write(
    "Baseline system service compared with the "
    "Earth-N coordinated intervention across "
    "the complete heatwave experiment."
)

experiment_file = (
    RESULTS_DIR /
    "earthn_baseline_vs_intervention.csv"
)

if experiment_file.exists():

    experiment_df = pd.read_csv(
        experiment_file
    )

    chart_columns = [
        "baseline_service_percent",
        "earthn_service_percent",
    ]

    if all(
        column in experiment_df.columns
        for column in chart_columns
    ):

        chart_df = experiment_df.set_index(
            "temperature_c"
        )[chart_columns]

        chart_df = chart_df.rename(
            columns={
                "baseline_service_percent":
                    "Baseline",
                "earthn_service_percent":
                    "Earth-N",
            }
        )

        st.line_chart(
            chart_df,
            width="stretch",
        )

        failure_results = (
            experiment_df[
                experiment_df["failure"] == "YES"
            ]
        )

        if not failure_results.empty:

            average_improvement = (
                failure_results[
                    "improvement_percentage_points"
                ].mean()
            )

            st.metric(
                "Average Simulated Improvement",
                f"+{average_improvement:.2f} pp",
            )

else:

    st.warning(
        "Experimental results file not found."
    )


# ============================================================
# AFFECTED INFRASTRUCTURE
# ============================================================

st.header("Affected Infrastructure")

if failure_triggered and baseline_affected:

    affected_rows = []

    for node in baseline_affected:

        service = (
            baseline_simulation.nodes[
                node
            ].get(
                "service_level",
                1.0,
            )
        )

        affected_rows.append(
            {
                "Infrastructure":
                    node.replace(
                        "_",
                        " ",
                    ),
                "Remaining Service":
                    f"{service * 100:.1f}%",
            }
        )

    affected_df = pd.DataFrame(
        affected_rows
    )

    st.dataframe(
        affected_df,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No infrastructure nodes are affected."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "EARTH-N — Infrastructure Resilience Intelligence"
)

st.caption(
    "Research prototype using illustrative "
    "infrastructure assumptions. Results are "
    "simulations and are not real-world "
    "operational predictions."
)