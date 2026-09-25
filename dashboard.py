import sys
from pathlib import Path

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent
SIMULATION_DIR = PROJECT_ROOT / "simulation"
AI_DIR = PROJECT_ROOT / "ai"

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
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EARTH-N",
    page_icon="🌍",
    layout="wide",
)


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #777;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 650;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .recommendation {
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #333;
        background-color: #f7f7f7;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MAIN SIMULATION
# =========================================================

def run_simulation(temperature):

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

    failure_triggered = disaster["failure_triggered"]

    failed_node = disaster["failed_node"]

    severity = disaster["severity"]

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
            "network": network,
            "simulation": network,
            "grid_stress": grid_stress,
            "failed_node": None,
            "severity": 0.0,
            "affected": [],
            "system_service": system_service,
            "critical_service": critical_service,
            "interventions": {},
            "recommendation": None,
        }

    # -----------------------------------------------------
    # APPLY FAILURE SEVERITY
    #
    # cascade_engine.py reads this value directly
    # from the failed node.
    # -----------------------------------------------------

    network.nodes[failed_node][
        "failure_severity"
    ] = severity

    # -----------------------------------------------------
    # RUN CASCADE
    # -----------------------------------------------------

    simulation, affected = simulate_cascade(
        network,
        failed_node,
    )

    # -----------------------------------------------------
    # BASELINE
    # -----------------------------------------------------

    system_service = calculate_system_service(
        simulation
    )

    critical_service = calculate_critical_service(
        simulation
    )

    # -----------------------------------------------------
    # INTERVENTION ANALYSIS
    # -----------------------------------------------------

    intervention_targets = [
        "Hospital",
        "Emergency_Center",
        "Industrial_Plant",
    ]

    intervention_results = {}

    for target in intervention_targets:

        # Fresh network
        test_network = create_earth_network()

        # Apply same failure severity
        test_network.nodes[failed_node][
            "failure_severity"
        ] = severity

        # Run same cascade
        test_simulation, test_affected = simulate_cascade(
            test_network,
            failed_node,
        )

        # Apply intervention
        test_simulation = apply_intervention(
            test_simulation,
            target,
        )

        # Calculate resulting system service
        intervention_service = calculate_system_service(
            test_simulation
        )

        improvement = (
            intervention_service
            - system_service
        )

        intervention_results[target] = {
            "service": intervention_service,
            "improvement": improvement,
        }

    # -----------------------------------------------------
    # SELECT RECOMMENDATION
    # -----------------------------------------------------

    recommendation = max(
        intervention_results,
        key=lambda target:
        intervention_results[target]["service"],
    )

    return {
        "network": network,
        "simulation": simulation,
        "grid_stress": grid_stress,
        "failed_node": failed_node,
        "severity": severity,
        "affected": affected,
        "system_service": system_service,
        "critical_service": critical_service,
        "interventions": intervention_results,
        "recommendation": recommendation,
    }


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Scenario Control")

temperature = st.sidebar.slider(
    "Heatwave temperature increase",
    min_value=0,
    max_value=20,
    value=5,
    step=1,
)

st.sidebar.caption(
    "Prototype scenario: electricity demand increases with temperature."
)

st.sidebar.markdown("---")

st.sidebar.write(
    f"**Current scenario:** +{temperature} °C"
)


# =========================================================
# RUN SIMULATION
# =========================================================

result = run_simulation(
    temperature
)

network = result["network"]

simulation = result["simulation"]

grid_stress = result["grid_stress"]

failed_node = result["failed_node"]

severity = result["severity"]

system_service = result["system_service"]

critical_service = result["critical_service"]

interventions = result["interventions"]

recommendation = result["recommendation"]


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">EARTH-N</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Earth Neural Network — Infrastructure Resilience Intelligence'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# INFRASTRUCTURE STATUS
# =========================================================

st.markdown(
    '<div class="section-title">Infrastructure Status</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Temperature Increase",
        f"+{temperature} °C",
    )


with col2:

    st.metric(
        "Grid Stress",
        f"{grid_stress * 100:.1f}%",
    )


with col3:

    st.metric(
        "System Service",
        f"{system_service * 100:.1f}%",
    )


with col4:

    st.metric(
        "Critical Service",
        f"{critical_service * 100:.1f}%",
    )


# =========================================================
# CASCADE STATUS
# =========================================================

st.markdown(
    '<div class="section-title">Cascade Status</div>',
    unsafe_allow_html=True,
)

if failed_node is None:

    st.success(
        "No grid failure detected."
    )

else:

    st.error(
        f"Grid failure detected: {failed_node}"
    )

    st.write(
        f"Failure severity: **{severity:.2f}**"
    )


# =========================================================
# EARTH-N INTERVENTION INTELLIGENCE
# =========================================================

if failed_node is not None:

    st.markdown(
        '<div class="section-title">'
        'Earth-N Intervention Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Earth-N evaluates possible emergency "
        "protection actions and estimates their "
        "effect on total infrastructure service."
    )

    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    if recommendation is not None:

        selected = interventions[
            recommendation
        ]

        st.markdown(
            f"""
            <div class="recommendation">

            <h3>Earth-N Protection Recommendation</h3>

            <h2>
            {recommendation.replace("_", " ")}
            </h2>

            <p>
            Baseline system service:
            <b>{system_service * 100:.1f}%</b>
            </p>

            <p>
            Estimated service after intervention:
            <b>{selected["service"] * 100:.1f}%</b>
            </p>

            <p>
            Estimated improvement:
            <b>+{selected["improvement"] * 100:.1f}
            percentage points</b>
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------
    # INTERVENTION COMPARISON
    # -----------------------------------------------------

    st.markdown(
        "### Intervention Scenarios"
    )

    cols = st.columns(3)

    for index, target in enumerate(
        interventions
    ):

        data = interventions[target]

        with cols[index]:

            st.metric(
                target.replace("_", " "),
                f"{data['service'] * 100:.1f}%",
            )

            st.caption(
                f"Improvement: "
                f"+{data['improvement'] * 100:.1f} points"
            )


# =========================================================
# INFRASTRUCTURE NETWORK
# =========================================================

st.markdown(
    '<div class="section-title">Infrastructure Network</div>',
    unsafe_allow_html=True,
)

fig, ax = plt.subplots(
    figsize=(12, 7)
)

position = nx.spring_layout(
    simulation,
    seed=42,
    k=1.5,
)

node_values = [
    simulation.nodes[node].get(
        "service_level",
        1.0,
    )
    for node in simulation.nodes
]

nx.draw_networkx_nodes(
    simulation,
    position,
    node_size=900,
    node_color=node_values,
    cmap="RdYlGn",
    vmin=0,
    vmax=1,
    ax=ax,
)

nx.draw_networkx_edges(
    simulation,
    position,
    arrows=True,
    arrowsize=15,
    width=1.5,
    alpha=0.6,
    ax=ax,
)

nx.draw_networkx_labels(
    simulation,
    position,
    font_size=8,
    ax=ax,
)

ax.set_axis_off()

st.pyplot(
    fig,
    use_container_width=True,
)

plt.close(fig)


# =========================================================
# AFFECTED INFRASTRUCTURE
# =========================================================

st.markdown(
    '<div class="section-title">Affected Infrastructure</div>',
    unsafe_allow_html=True,
)

affected_display = []

for node in simulation.nodes:

    service = simulation.nodes[node].get(
        "service_level",
        1.0,
    )

    if service < 1.0:

        affected_display.append(
            (node, service)
        )


if affected_display:

    for node, service in affected_display:

        st.write(
            f"**{node}** — "
            f"{service * 100:.1f}% service"
        )

else:

    st.success(
        "No infrastructure affected."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "EARTH-N prototype — computer-based infrastructure resilience simulation."
)

st.caption(
    "Current model uses illustrative assumptions "
    "for research and demonstration."
)