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

from decision_engine import analyze_scenario


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
    "AI-Powered Infrastructure Resilience & Decision Intelligence"
)

st.write(
    "An infrastructure intelligence layer for detecting, "
    "understanding, and responding to cascading infrastructure failures."
)

st.caption(
    "Current prototype: simulation-based decision support. "
    "Future versions can integrate real infrastructure, environmental, "
    "IoT/SCADA and historical data with advanced AI."
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

failure_triggered = heatwave_result[
    "failure_triggered"
]

severity = heatwave_result["severity"]

failed_node = heatwave_result[
    "failed_node"
]


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

        critical_service_result = (
            calculate_critical_service(
                protected_network
            )
        )

        intervention_results.append(
            {
                "target": target,
                "service": service,
                "critical_service":
                    critical_service_result,
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

    earthn_critical_service = best_result[
        "critical_service"
    ]

else:

    selected_intervention = (
        "No intervention required"
    )

    earthn_service = baseline_service

    earthn_critical_service = critical_service


improvement = (
    earthn_service
    - baseline_service
)


# ============================================================
# PREPARE DATA FOR AI DECISION ENGINE
# ============================================================

decision_intervention_rows = []

for result in intervention_results:

    decision_intervention_rows.append(
        {
            "Intervention":
                result["target"].replace(
                    "_",
                    " ",
                ),
            "System Service (%)":
                result["service"] * 100,
            "Critical Service (%)":
                result["critical_service"] * 100,
            "Improvement (pp)":
                (
                    result["service"]
                    - baseline_service
                ) * 100,
        }
    )


decision_intervention_df = pd.DataFrame(
    decision_intervention_rows
)


# ============================================================
# AI DECISION MAKER
# ============================================================

decision = analyze_scenario(
    temperature_increase=temperature,
    grid_stress=grid_stress,
    failure_triggered=failure_triggered,
    failed_node=failed_node,
    severity=severity,
    affected_nodes=baseline_affected,
    baseline_service=baseline_service * 100,
    earthn_service=earthn_service * 100,
    selected_intervention=(
        selected_intervention.replace(
            "_",
            " ",
        )
    ),
    intervention_df=decision_intervention_df,
)


# ============================================================
# LIVE INFRASTRUCTURE STATUS
# ============================================================

st.header(
    "Live Infrastructure Status"
)

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
        delta=(
            f"{improvement * 100:.1f} pp"
        ),
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
# INFRASTRUCTURE DEPENDENCY NETWORK
# ============================================================

st.divider()

st.header(
    "Infrastructure Dependency Network"
)

st.write(
    "EARTH-N represents infrastructure as an interconnected "
    "dependency network. The graph shows how disruption can "
    "propagate between infrastructure systems."
)


def build_network_graph(
    graph,
    failed_node=None,
    intervention=None,
):

    lines = []

    lines.append(
        "digraph EARTH_N {"
    )

    lines.append(
        'graph [rankdir=LR, '
        'bgcolor="transparent", '
        'nodesep=0.5, '
        'ranksep=0.8];'
    )

    lines.append(
        'node [shape=box, '
        'style="rounded,filled", '
        'fontname="Arial", '
        'fontsize=10, '
        'margin="0.15,0.10"];'
    )

    lines.append(
        'edge [color="#7A7A7A", '
        'penwidth=1.5, '
        'arrowsize=0.7];'
    )


    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    for node in graph.nodes:

        label = node.replace(
            "_",
            "\\n",
        )

        if node == failed_node:

            lines.append(
                f'"{node}" '
                f'[label="{label}", '
                'fillcolor="#F8D7DA", '
                'color="#C62828", '
                'penwidth=3];'
            )

        elif (
            intervention
            and node.replace(
                "_",
                " ",
            )
            == intervention
        ):

            lines.append(
                f'"{node}" '
                f'[label="{label}", '
                'fillcolor="#DFF3E4", '
                'color="#2E7D32", '
                'penwidth=3];'
            )

        else:

            lines.append(
                f'"{node}" '
                f'[label="{label}", '
                'fillcolor="#F5F7FA", '
                'color="#667085"];'
            )


    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    for source, target, data in graph.edges(
        data=True
    ):

        strength = data.get(
            "dependency_strength",
            1.0,
        )

        penwidth = (
            1.0
            + strength * 1.5
        )

        lines.append(
            f'"{source}" -> "{target}" '
            f'[penwidth={penwidth:.2f}];'
        )


    lines.append("}")

    return "\n".join(lines)


graph_source = build_network_graph(
    network,
    failed_node=(
        failed_node
        if failure_triggered
        else None
    ),
    intervention=(
        selected_intervention.replace(
            "_",
            " ",
        )
        if failure_triggered
        else None
    ),
)


st.graphviz_chart(
    graph_source,
    width='stretch',
)


if failure_triggered:

    st.info(
        "🔴 Red node = simulated failure   |   "
        "🟢 Green node = selected intervention"
    )

else:

    st.info(
        "No primary infrastructure failure is "
        "currently triggered."
    )


with st.expander(
    "View infrastructure dependency data"
):

    dependency_rows = []

    for source, target, data in network.edges(
        data=True
    ):

        dependency_rows.append(
            {
                "Source":
                    source.replace(
                        "_",
                        " ",
                    ),
                "Dependent":
                    target.replace(
                        "_",
                        " ",
                    ),
                "Dependency Strength":
                    data.get(
                        "dependency_strength",
                        1.0,
                    ),
            }
        )


    dependency_df = pd.DataFrame(
        dependency_rows
    )

    st.dataframe(
        dependency_df,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# CASCADE ANALYSIS
# ============================================================

st.divider()

st.header(
    "Cascade Analysis"
)

st.write(
    "Detection and propagation of infrastructure "
    "service loss."
)


c1, c2, c3, c4 = st.columns(4)


with c1:

    if failure_triggered:

        st.error(
            f"Grid failure detected — "
            f"{failed_node}"
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
# AI DECISION MAKER
# ============================================================

st.divider()

st.header(
    "🤖 AI Decision Maker"
)

st.write(
    "The decision-support layer analyzes the simulated "
    "infrastructure state and explains the intervention "
    "selected by the EARTH-N engine."
)


d1, d2, d3 = st.columns(3)


with d1:

    st.metric(
        "Risk Level",
        decision["risk_level"],
    )


with d2:

    st.metric(
        "Recommended Action",
        decision[
            "recommended_intervention"
        ],
    )


with d3:

    st.metric(
        "Decision Support",
        decision["confidence"],
    )


st.subheader(
    "Situation Assessment"
)

st.info(
    decision["decision_statement"]
)


st.subheader(
    "Why this intervention?"
)

st.write(
    decision["explanation"]
)


st.subheader(
    "Infrastructure Impact"
)

st.write(
    decision["failure_summary"]
)

st.write(
    f"**Affected infrastructure:** "
    f"{decision['affected_count']} nodes"
)

st.write(
    f"**Affected nodes:** "
    f"{decision['affected_summary']}"
)

if decision["critical_warning"]:

    st.warning(
        decision["critical_warning"]
    )


with st.expander(
    "View AI decision analysis"
):

    st.write(
        "**Risk classification:** "
        f"{decision['risk_level']}"
    )

    st.write(
        "**Grid stress:** "
        f"{decision['grid_stress']:.1f}%"
    )

    st.write(
        "**Baseline service:** "
        f"{decision['baseline_service']:.1f}%"
    )

    st.write(
        "**EARTH-N service:** "
        f"{decision['earthn_service']:.1f}%"
    )

    st.write(
        "**Simulated improvement:** "
        f"+{decision['improvement']:.1f} percentage points"
    )

    st.write(
        "**Decision support level:** "
        f"{decision['confidence']}"
    )

    st.caption(
        "Current decision engine is explainable and "
        "rule-based. It is not a trained machine-learning "
        "model yet."
    )


# ============================================================
# INTERVENTION ENGINE
# ============================================================

st.divider()

st.header(
    "Earth-N Intervention Engine"
)

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

        intervention_df[
            "critical_service"
        ] = (
            intervention_df[
                "critical_service"
            ] * 100
        ).round(1)

        intervention_df = (
            intervention_df.rename(
                columns={
                    "target":
                        "Protection Target",
                    "service":
                        "System Service (%)",
                    "critical_service":
                        "Critical Service (%)",
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

st.divider()

st.header(
    "Experimental Evidence"
)

st.write(
    "Baseline system service compared with the "
    "Earth-N coordinated intervention across "
    "the complete heatwave experiment."
)


experiment_file = (
    RESULTS_DIR
    / "earthn_baseline_vs_intervention.csv"
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

st.divider()

st.header(
    "Affected Infrastructure"
)


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
# FUTURE AI ROADMAP
# ============================================================

st.divider()

st.header(
    "EARTH-N Intelligence Roadmap"
)

roadmap1, roadmap2, roadmap3, roadmap4 = st.columns(4)


with roadmap1:

    st.subheader("Current")

    st.write(
        "Simulation + explainable "
        "decision engine"
    )


with roadmap2:

    st.subheader("Next")

    st.write(
        "Real infrastructure and "
        "environmental data"
    )


with roadmap3:

    st.subheader("AI")

    st.write(
        "ML / GNN-based prediction "
        "and optimization"
    )


with roadmap4:

    st.subheader("Future")

    st.write(
        "System-level resilience "
        "decision intelligence"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "EARTH-N — AI-Powered Infrastructure Resilience "
    "& Decision Intelligence"
)

st.caption(
    "Research prototype using illustrative "
    "infrastructure assumptions. Results are "
    "simulations and are not real-world "
    "operational predictions."
)
