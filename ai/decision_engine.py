"""
EARTH-N AI Decision Engine

Explainable decision-support layer for the EARTH-N
infrastructure resilience prototype.

Current version:
- Rule-based
- Explainable
- Uses simulation outputs
- No external AI/API dependency

Future versions can replace or augment this engine
with machine learning, graph neural networks,
optimization, or LLM-based reasoning.
"""


# ============================================================
# DECISION ENGINE
# ============================================================

def analyze_scenario(
    temperature_increase,
    grid_stress,
    failure_triggered,
    failed_node,
    severity,
    affected_nodes,
    baseline_service,
    earthn_service,
    selected_intervention,
    intervention_df,
):
    """
    Analyze an EARTH-N simulation scenario and produce
    an explainable decision-support result.
    """

    # --------------------------------------------------------
    # BASIC VALUES
    # --------------------------------------------------------

    improvement = (
        earthn_service
        - baseline_service
    )

    grid_stress_percent = (
        grid_stress * 100
    )

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if not failure_triggered:

        risk_level = "LOW"

    elif severity < 0.75:

        risk_level = "MODERATE"

    elif severity < 1.0:

        risk_level = "HIGH"

    else:

        risk_level = "CRITICAL"

    # --------------------------------------------------------
    # FAILURE DESCRIPTION
    # --------------------------------------------------------

    if failure_triggered:

        failure_summary = (
            f"The simulated scenario triggered a failure "
            f"at {failed_node.replace('_', ' ')}."
        )

    else:

        failure_summary = (
            "The simulated scenario did not trigger "
            "a primary infrastructure failure."
        )

    # --------------------------------------------------------
    # AFFECTED INFRASTRUCTURE
    # --------------------------------------------------------

    readable_affected = []

    for node in affected_nodes:

        readable_affected.append(
            node.replace("_", " ")
        )

    if readable_affected:

        affected_summary = (
            ", ".join(readable_affected)
        )

    else:

        affected_summary = (
            "No downstream infrastructure was affected."
        )

    # --------------------------------------------------------
    # INTERVENTION ANALYSIS
    # --------------------------------------------------------

    options = []

    if intervention_df is not None:

        for _, row in intervention_df.iterrows():

            options.append(
                {
                    "intervention": str(
                        row["Intervention"]
                    ),
                    "system_service": float(
                        row["System Service (%)"]
                    ),
                    "critical_service": float(
                        row["Critical Service (%)"]
                    ),
                    "improvement": float(
                        row["Improvement (pp)"]
                    ),
                }
            )

    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    recommendation = (
        selected_intervention
    )

    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    if failure_triggered:

        explanation = (
            f"The decision engine recommends "
            f"{recommendation} because it produced the "
            f"highest simulated system service among the "
            f"tested intervention options."
        )

    else:

        explanation = (
            "No primary failure was triggered. "
            "The intervention result represents a "
            "scenario-based resilience assessment rather "
            "than an emergency response."
        )

    # --------------------------------------------------------
    # CRITICAL INFRASTRUCTURE WARNING
    # --------------------------------------------------------

    critical_nodes = [
        "Hospital",
        "Emergency Center",
        "Industrial Plant",
    ]

    affected_critical = []

    for node in readable_affected:

        if node in critical_nodes:

            affected_critical.append(
                node
            )

    if affected_critical:

        critical_warning = (
            "Critical infrastructure affected: "
            + ", ".join(
                affected_critical
            )
        )

    else:

        critical_warning = (
            "No directly affected critical facility "
            "was identified in the simulated cascade."
        )

    # --------------------------------------------------------
    # DECISION CONFIDENCE
    # --------------------------------------------------------

    if not failure_triggered:

        confidence = "Scenario monitoring"

    elif improvement >= 15:

        confidence = "Strong simulated support"

    elif improvement >= 5:

        confidence = "Moderate simulated support"

    else:

        confidence = "Limited simulated support"

    # --------------------------------------------------------
    # HUMAN-READABLE DECISION
    # --------------------------------------------------------

    decision_statement = (
        f"Under a +{temperature_increase}°C simulated "
        f"heatwave, grid stress reached "
        f"{grid_stress_percent:.1f}%. "
        f"The baseline system service was "
        f"{baseline_service:.1f}%, while the selected "
        f"EARTH-N intervention produced "
        f"{earthn_service:.1f}% system service, "
        f"representing a simulated improvement of "
        f"{improvement:.1f} percentage points."
    )

    # --------------------------------------------------------
    # RETURN DECISION PACKAGE
    # --------------------------------------------------------

    return {
        "risk_level": risk_level,
        "failure_summary": failure_summary,
        "affected_summary": affected_summary,
        "affected_count": len(
            affected_nodes
        ),
        "critical_warning": critical_warning,
        "recommended_intervention": recommendation,
        "explanation": explanation,
        "decision_statement": decision_statement,
        "confidence": confidence,
        "improvement": improvement,
        "baseline_service": baseline_service,
        "earthn_service": earthn_service,
        "grid_stress": grid_stress_percent,
        "failure_triggered": failure_triggered,
        "failed_node": (
            failed_node.replace("_", " ")
            if failed_node
            else None
        ),
        "severity": severity,
        "intervention_options": options,
    }


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "EARTH-N Decision Engine"
    )

    print(
        "Module loaded successfully."
    )