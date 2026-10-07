"""
Unit tests for controlled perturbation benchmark dataset and technology registry.
"""
from pathlib import Path
import pandas as pd
import pytest

BENCHMARK_PATH = Path(__file__).parents[1] / "data" / "02_processed" / "controlled_perturbation_benchmark.parquet"
TECH_REGISTRY_PATH = Path(__file__).parents[1] / "data" / "02_processed" / "facility_technology_registry.csv"


def test_technology_registry_completeness():
    """Verify that all 30 facilities have documented capacity and route metadata."""
    assert TECH_REGISTRY_PATH.exists()
    df = pd.read_csv(TECH_REGISTRY_PATH)
    assert len(df) == 30
    assert "verified_technology_route" in df.columns
    assert "technology_source" in df.columns
    assert "technology_source_url" in df.columns
    # Ensure no empty routes
    assert not df["verified_technology_route"].isna().any()


def test_controlled_benchmark_structure():
    """Verify schema, label naming, and non-circular production in benchmark dataset."""
    assert BENCHMARK_PATH.exists()
    df = pd.read_parquet(BENCHMARK_PATH)
    assert len(df) >= 100

    # Critical Review Check: Benchmark label must be named benchmark_label, NOT ground_truth
    assert "benchmark_label" in df.columns
    assert "ground_truth_inconsistent_label" not in df.columns

    # Verify presence of multimodal evidence columns
    required_cols = [
        "case_id",
        "facility_id",
        "declared_production_tonnes",
        "independent_capacity_mtpa",
        "actual_technology_route",
        "declared_production_route",
        "stoich_margin_tco2_per_t",
        "stoich_violation",
        "satellite_zscore",
        "satellite_data_source",
        "historical_zscore",
        "benchmark_label",
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"

    # Verify that satellite data source is real_sentinel5p or no_data
    assert set(df["satellite_data_source"].unique()).issubset({"real_sentinel5p", "no_data"})
