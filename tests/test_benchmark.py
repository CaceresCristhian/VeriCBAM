"""
Unit tests for the 325-case graded evaluation benchmark dataset and verified technology registry.
"""

from pathlib import Path
import pandas as pd

BENCHMARK_PATH = Path(__file__).parents[1] / "data" / "02_processed" / "graded_evaluation_benchmark.parquet"
TECH_REGISTRY_PATH = Path(__file__).parents[1] / "data" / "02_processed" / "facility_technology_registry.csv"


def test_technology_registry_completeness():
    """Verify that all 30 facilities have documented capacity and route metadata."""
    assert TECH_REGISTRY_PATH.exists()
    df = pd.read_csv(TECH_REGISTRY_PATH)
    assert len(df) == 30
    for col in ("verified_technology_route", "technology_source", "technology_source_url"):
        assert col in df.columns
    assert not df["verified_technology_route"].isna().any()


def test_graded_benchmark_structure():
    """Verify 325-case schema, evaluation splits, and multimodal evidence columns."""
    assert BENCHMARK_PATH.exists()
    df = pd.read_parquet(BENCHMARK_PATH)
    assert len(df) == 325
    assert "benchmark_label" in df.columns
    assert "ground_truth_inconsistent_label" not in df.columns

    expected_splits = {"Negative_Authentic", "Graded_Understatement", "Route_Mismatch"}
    assert set(df["evaluation_split"].unique()) == expected_splits

    required_cols = [
        "case_id",
        "facility_id",
        "nameplate_capacity_mtpa",
        "assumed_production_tonnes_central",
        "actual_technology_route",
        "declared_production_route",
        "stoich_applicable",
        "stoich_available",
        "stoich_margin_tonnes",
        "stoich_violation_conservative",
        "historical_z_robust",
        "nox_co2_anomaly_zscore",
        "satellite_zscore",
        "route_mismatch_detected",
        "benchmark_label",
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"
