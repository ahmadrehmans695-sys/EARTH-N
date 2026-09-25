from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# EARTH-N
# Quantitative Evaluation
# Baseline vs Earth-N Intervention
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

INPUT_FILE = RESULTS_DIR / "earthn_baseline_vs_intervention.csv"
SUMMARY_FILE = RESULTS_DIR / "earthn_quantitative_summary.csv"
EVIDENCE_FILE = RESULTS_DIR / "earthn_quantitative_evidence.csv"


def main():

    print("=" * 70)
    print("EARTH-N QUANTITATIVE EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load existing experiment data
    # --------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print(f"\nInput file: {INPUT_FILE}")
    print(f"Total scenarios: {len(df)}")

    # --------------------------------------------------------
    # Validate actual columns from our experiment
    # --------------------------------------------------------

    required_columns = [
        "temperature_c",
        "grid_stress_percent",
        "failure",
        "severity",
        "baseline_system_service_percent",
        "baseline_critical_service_percent",
        "earthn_service_percent",
        "improvement_percentage_points"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # --------------------------------------------------------
    # Identify failure scenarios
    # --------------------------------------------------------

    failure_df = df[
        df["failure"].astype(str).str.upper() == "YES"
    ].copy()

    no_failure_df = df[
        df["failure"].astype(str).str.upper() != "YES"
    ].copy()

    # --------------------------------------------------------
    # First simulated failure
    # --------------------------------------------------------

    if len(failure_df) > 0:

        first_failure_temperature = failure_df[
            "temperature_c"
        ].min()

    else:

        first_failure_temperature = np.nan

    # --------------------------------------------------------
    # Overall statistics
    # --------------------------------------------------------

    total_scenarios = len(df)

    failure_scenarios = len(failure_df)

    no_failure_scenarios = len(no_failure_df)

    overall_baseline_mean = df[
        "baseline_system_service_percent"
    ].mean()

    overall_earthn_mean = df[
        "earthn_service_percent"
    ].mean()

    overall_improvement_mean = df[
        "improvement_percentage_points"
    ].mean()

    # --------------------------------------------------------
    # Failure-only statistics
    # --------------------------------------------------------

    if len(failure_df) > 0:

        failure_baseline_mean = failure_df[
            "baseline_system_service_percent"
        ].mean()

        failure_earthn_mean = failure_df[
            "earthn_service_percent"
        ].mean()

        failure_improvement_mean = failure_df[
            "improvement_percentage_points"
        ].mean()

        failure_improvement_median = failure_df[
            "improvement_percentage_points"
        ].median()

        failure_improvement_min = failure_df[
            "improvement_percentage_points"
        ].min()

        failure_improvement_max = failure_df[
            "improvement_percentage_points"
        ].max()

        failure_improvement_std = failure_df[
            "improvement_percentage_points"
        ].std()

        failure_baseline_median = failure_df[
            "baseline_system_service_percent"
        ].median()

        failure_earthn_median = failure_df[
            "earthn_service_percent"
        ].median()

    else:

        failure_baseline_mean = np.nan
        failure_earthn_mean = np.nan
        failure_improvement_mean = np.nan
        failure_improvement_median = np.nan
        failure_improvement_min = np.nan
        failure_improvement_max = np.nan
        failure_improvement_std = np.nan
        failure_baseline_median = np.nan
        failure_earthn_median = np.nan

    # --------------------------------------------------------
    # Build quantitative summary
    # --------------------------------------------------------

    summary = pd.DataFrame({

        "metric": [

            "Total simulated scenarios",

            "Failure scenarios",

            "No-failure scenarios",

            "First simulated failure temperature (°C)",

            "Overall mean baseline system service (%)",

            "Overall mean Earth-N service (%)",

            "Overall mean improvement (percentage points)",

            "Failure-only mean baseline system service (%)",

            "Failure-only mean Earth-N service (%)",

            "Failure-only mean improvement (percentage points)",

            "Failure-only median improvement (percentage points)",

            "Failure-only minimum improvement (percentage points)",

            "Failure-only maximum improvement (percentage points)",

            "Failure-only improvement standard deviation",

            "Failure-only median baseline system service (%)",

            "Failure-only median Earth-N service (%)"
        ],

        "value": [

            total_scenarios,

            failure_scenarios,

            no_failure_scenarios,

            first_failure_temperature,

            overall_baseline_mean,

            overall_earthn_mean,

            overall_improvement_mean,

            failure_baseline_mean,

            failure_earthn_mean,

            failure_improvement_mean,

            failure_improvement_median,

            failure_improvement_min,

            failure_improvement_max,

            failure_improvement_std,

            failure_baseline_median,

            failure_earthn_median
        ]
    })

    # --------------------------------------------------------
    # Save summary
    # --------------------------------------------------------

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Create detailed evidence table
    # --------------------------------------------------------

    evidence_columns = [

        "temperature_c",

        "grid_stress_percent",

        "failure",

        "severity",

        "baseline_system_service_percent",

        "baseline_critical_service_percent",

        "earthn_service_percent",

        "improvement_percentage_points",

        "selected_intervention"
    ]

    evidence = df[evidence_columns].copy()

    # Difference between Earth-N and baseline
    evidence["absolute_service_difference"] = (

        evidence["earthn_service_percent"]

        - evidence["baseline_system_service_percent"]
    )

    # Whether Earth-N produced a higher service value
    evidence["earthn_higher_service"] = (

        evidence["earthn_service_percent"]

        > evidence["baseline_system_service_percent"]
    )

    # --------------------------------------------------------
    # Save evidence
    # --------------------------------------------------------

    evidence.to_csv(
        EVIDENCE_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Console report
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("EXPERIMENT SUMMARY")
    print("-" * 70)

    print(
        f"Total scenarios: "
        f"{total_scenarios}"
    )

    print(
        f"Failure scenarios: "
        f"{failure_scenarios}"
    )

    print(
        f"No-failure scenarios: "
        f"{no_failure_scenarios}"
    )

    if not np.isnan(first_failure_temperature):

        print(
            f"First simulated failure: "
            f"+{first_failure_temperature:.1f}°C"
        )

    print("\nOVERALL")

    print(
        f"Mean baseline system service: "
        f"{overall_baseline_mean:.2f}%"
    )

    print(
        f"Mean Earth-N service: "
        f"{overall_earthn_mean:.2f}%"
    )

    print(
        f"Mean improvement: "
        f"{overall_improvement_mean:.2f} percentage points"
    )

    if len(failure_df) > 0:

        print("\nFAILURE SCENARIOS ONLY")

        print(
            f"Mean baseline system service: "
            f"{failure_baseline_mean:.2f}%"
        )

        print(
            f"Mean Earth-N service: "
            f"{failure_earthn_mean:.2f}%"
        )

        print(
            f"Mean improvement: "
            f"{failure_improvement_mean:.2f} percentage points"
        )

        print(
            f"Median improvement: "
            f"{failure_improvement_median:.2f} percentage points"
        )

        print(
            f"Minimum improvement: "
            f"{failure_improvement_min:.2f} percentage points"
        )

        print(
            f"Maximum improvement: "
            f"{failure_improvement_max:.2f} percentage points"
        )

        print(
            f"Standard deviation: "
            f"{failure_improvement_std:.2f}"
        )

        print(
            f"Median baseline system service: "
            f"{failure_baseline_median:.2f}%"
        )

        print(
            f"Median Earth-N service: "
            f"{failure_earthn_median:.2f}%"
        )

    # --------------------------------------------------------
    # Scenario-by-scenario evidence
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("SCENARIO EVIDENCE")
    print("-" * 70)

    display_columns = [

        "temperature_c",

        "grid_stress_percent",

        "failure",

        "severity",

        "baseline_system_service_percent",

        "earthn_service_percent",

        "improvement_percentage_points",

        "selected_intervention"
    ]

    print(
        evidence[display_columns].to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Files created
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FILES CREATED")
    print("=" * 70)

    print(
        f"Summary:  "
        f"{SUMMARY_FILE}"
    )

    print(
        f"Evidence: "
        f"{EVIDENCE_FILE}"
    )

    print("\nQuantitative evaluation completed successfully.")


if __name__ == "__main__":
    main()