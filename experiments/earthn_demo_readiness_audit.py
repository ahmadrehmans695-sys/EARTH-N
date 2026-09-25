from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ============================================================
# REQUIRED FILES
# ============================================================

REQUIRED_FILES = [
    # Core simulation
    "simulation/city_model.py",
    "simulation/cascade_engine.py",
    "simulation/disaster_engine.py",

    # Intervention intelligence
    "ai/intervention_engine.py",

    # Main dashboard
    "dashboard_v2.py",

    # Main experiments
    "experiments/baseline_vs_earthn_experiment.py",
    "experiments/earthn_quantitative_evaluation.py",
    "experiments/earthn_sensitivity_analysis.py",
    "experiments/earthn_robustness_analysis.py",

    # Visualizations
    "visualization/network_map.py",
    "visualization/heatwave_cascade.py",
    "visualization/resilience_curve.py",
    "visualization/baseline_vs_earthn_chart.py",
    "visualization/dependency_sensitivity_chart.py",
    "visualization/robustness_analysis_chart.py",

    # Experimental evidence
    "results/earthn_baseline_vs_intervention.csv",
    "results/earthn_quantitative_summary.csv",
    "results/earthn_quantitative_evidence.csv",
    "results/earthn_sensitivity_results.csv",
    "results/earthn_sensitivity_summary.csv",
    "results/earthn_robustness_results.csv",

    # Research figures
    "results/earthn_network_map.png",
    "results/earthn_heatwave_cascade.png",
    "results/earthn_resilience_curve.png",
    "results/earthn_baseline_vs_intervention.png",
    "results/earthn_dependency_sensitivity.png",
    "results/earthn_robustness_chart.png",
]


# ============================================================
# AUDIT
# ============================================================

def main():

    print("=" * 80)
    print("EARTH-N — DEMO READINESS AUDIT")
    print("=" * 80)

    missing_files = []
    existing_files = []

    print()
    print("CHECKING PROJECT COMPONENTS")
    print("-" * 80)

    for relative_path in REQUIRED_FILES:

        full_path = (
            PROJECT_ROOT
            / relative_path
        )

        if full_path.exists():

            existing_files.append(
                relative_path
            )

            print(
                f"[OK]      {relative_path}"
            )

        else:

            missing_files.append(
                relative_path
            )

            print(
                f"[MISSING] {relative_path}"
            )

    print()
    print("-" * 80)

    print(
        f"Required files: {len(REQUIRED_FILES)}"
    )

    print(
        f"Available:      {len(existing_files)}"
    )

    print(
        f"Missing:        {len(missing_files)}"
    )

    print()

    if missing_files:

        print(
            "DEMO READINESS: INCOMPLETE"
        )

        print()
        print(
            "Missing files:"
        )

        for file in missing_files:

            print(
                f"  - {file}"
            )

    else:

        print(
            "DEMO READINESS: READY"
        )

        print()
        print(
            "All required EARTH-N prototype "
            "components and evidence files are present."
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()