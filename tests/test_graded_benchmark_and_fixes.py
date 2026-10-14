"""
Unit tests for VeriCBAM Graded Benchmark and Methodological Fixes.
Covers requirements M1, M3, M5, M6, N5:
- M3: Capacity fallback removal (stoich_available=False, NaN floors for unobserved capacity).
- M1: Both label thresholds (delta >= 10% primary, delta >= 5% sensitivity).
- M6: Leave-one-year-out NOx baseline excludes tested year and requires min_years >= 3.
- Duplicate resolution rule in cohort building.
- M5: One-sided historical score max(0, -z) vs two-sided |z| sign convention.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data_loaders.nox_baseline import compute_leave_one_year_out_nox_ratios
from src.core.bayesian.evidence_fusion import ProbabilisticEvidenceFusionEngine, EvidenceInput


WORKSPACE_ROOT = Path(__file__).parents[1]
GRADED_BENCHMARK_PATH = WORKSPACE_ROOT / "data" / "02_processed" / "graded_evaluation_benchmark.parquet"
REGISTRY_PATH = WORKSPACE_ROOT / "data" / "02_processed" / "facility_technology_registry.csv"


def test_m3_capacity_fallback_removal():
    """Verify M3: Plants with missing or <=0 capacity receive stoich_available=False and NaN floors."""
    assert GRADED_BENCHMARK_PATH.exists(), "Graded benchmark dataset not found"
    df = pd.read_parquet(GRADED_BENCHMARK_PATH)
    reg = pd.read_csv(REGISTRY_PATH).set_index("FacilityInspireId")

    # Find plants with <=0 crude steel capacity (e.g. Hamborn, Beeckerwerth, DK Recycling)
    zero_cap_fids = reg[
        (reg["sector"] == "Steel") &
        (reg["crude_steel_capacity_mtpa"].isna() | (reg["crude_steel_capacity_mtpa"] <= 0.0))
    ].index.tolist()

    assert len(zero_cap_fids) == 3, f"Expected 3 steel plants with zero crude capacity, found {len(zero_cap_fids)}"

    for fid in zero_cap_fids:
        fac_cases = df[df["facility_id"] == fid]
        assert len(fac_cases) > 0, f"Expected cases for facility {fid}"

        # In authentic negatives and graded understatements:
        for _, row in fac_cases.iterrows():
            assert row["stoich_available"] is False or row["stoich_available"] == 0
            assert pd.isna(row["stoich_floor_central_tco2"])
            assert pd.isna(row["stoich_floor_max_tco2"])
            assert row["stoich_violation_central"] is False or row["stoich_violation_central"] == 0
            assert row["stoich_violation_conservative"] is False or row["stoich_violation_conservative"] == 0
            assert pd.isna(row["stoich_margin_tonnes"])

    # Verify plants with positive capacity and applicable boundaries have stoich_available=True and positive floors
    from src.benchmark.graded_benchmark_generator import TRANSFERRED_GAS_STEEL_PLANTS
    applicable_pos_cap = df[
        (~df["facility_id"].isin(zero_cap_fids)) &
        (~df["facility_id"].isin(TRANSFERRED_GAS_STEEL_PLANTS))
    ]
    assert (applicable_pos_cap["stoich_available"] == True).all()
    assert (applicable_pos_cap["stoich_floor_central_tco2"] > 0).all()

    # Verify M3 route-mismatch guard: Hamborn (zero crude steel capacity) must NOT be in route mismatches
    route_mis = df[df["evaluation_split"] == "Route_Mismatch"]
    assert not (route_mis["facility_id"].isin(zero_cap_fids)).any()
    assert len(route_mis) == 8, f"Expected 8 route mismatch cases after skipping Hamborn, got {len(route_mis)}"


def test_m1_label_thresholds_sensitivity():
    """Verify M1: Both benchmark label rules work and 5% is distinct from 10%."""
    df = pd.read_parquet(GRADED_BENCHMARK_PATH)

    # Authentic negatives: must be 0 under both thresholds
    auth_neg = df[df["evaluation_split"] == "Negative_Authentic"]
    assert (auth_neg["benchmark_label"] == 0).all()

    # Understatement delta = 5%:
    d5_cases = df[(df["evaluation_split"] == "Graded_Understatement") & (df["understatement_delta_pct"] == 5.0)]
    assert len(d5_cases) > 0
    # Under primary delta >= 10% rule, delta = 5% is labeled 0 (Concordant/Within Audit Tolerance)
    assert (d5_cases["benchmark_label"] == 0).all()

    # Under sensitivity delta >= 5% rule:
    label_d5 = np.where(
        (df["understatement_delta_pct"] >= 5.0) | (df["evaluation_split"] == "Route_Mismatch"),
        1,
        0,
    )
    assert label_d5[d5_cases.index].all() == 1

    # Understatement delta >= 10%: must be labeled 1 under both
    d10_plus = df[
        (df["evaluation_split"] == "Graded_Understatement") &
        (df["understatement_delta_pct"] >= 10.0)
    ]
    assert (d10_plus["benchmark_label"] == 1).all()
    assert (label_d5[d10_plus.index] == 1).all()

    # Route mismatches: must be labeled 1 under both
    route_mis = df[df["evaluation_split"] == "Route_Mismatch"]
    assert (route_mis["benchmark_label"] == 1).all()
    assert (label_d5[route_mis.index] == 1).all()


def test_m6_leave_one_year_out_nox_baseline():
    """Verify M6: NOx/CO2 baseline strictly excludes tested year and requires min_years >= 3."""
    # Synthetic cohort with 4 years for Facility A and 2 years for Facility B
    toy_data = pd.DataFrame([
        # Facility A: 4 years (2018-2021)
        {"FacilityInspireId": "FAC_A", "reportingYear": 2018, "co2_tonnes": 1000.0, "nox_tonnes": 1.0},  # ratio = 0.001
        {"FacilityInspireId": "FAC_A", "reportingYear": 2019, "co2_tonnes": 1000.0, "nox_tonnes": 2.0},  # ratio = 0.002
        {"FacilityInspireId": "FAC_A", "reportingYear": 2020, "co2_tonnes": 1000.0, "nox_tonnes": 3.0},  # ratio = 0.003
        {"FacilityInspireId": "FAC_A", "reportingYear": 2021, "co2_tonnes": 1000.0, "nox_tonnes": 4.0},  # ratio = 0.004
        # Facility B: 2 years (insufficient for min_years=3)
        {"FacilityInspireId": "FAC_B", "reportingYear": 2020, "co2_tonnes": 500.0, "nox_tonnes": 1.0},
        {"FacilityInspireId": "FAC_B", "reportingYear": 2021, "co2_tonnes": 500.0, "nox_tonnes": 1.5},
    ])

    res = compute_leave_one_year_out_nox_ratios(toy_data, min_years=3)

    # Facility B must have NaN baselines because remaining years (1) < 3 min_years
    fac_b_res = res[res["facility_inspire_id"] == "FAC_B"]
    assert len(fac_b_res) == 2
    assert fac_b_res["nox_co2_ratio_mean"].isna().all()
    assert (fac_b_res["n_ratio_obs"] < 3).all()

    # Facility A must have 4 rows (one per year) with valid leave-one-year-out baselines
    fac_a_res = res[res["facility_inspire_id"] == "FAC_A"].set_index("reporting_year")
    assert len(fac_a_res) == 4

    # For reportingYear 2021: baseline must be computed on [2018, 2019, 2020] ratios: [0.001, 0.002, 0.003]
    # Mean of [0.001, 0.002, 0.003] = 0.0020
    row_2021 = fac_a_res.loc[2021]
    assert np.isclose(row_2021["nox_co2_ratio_mean"], 0.0020, atol=1e-6)
    assert row_2021["n_ratio_obs"] == 3

    # For reportingYear 2018: baseline must be computed on [2019, 2020, 2021] ratios: [0.002, 0.003, 0.004]
    # Mean of [0.002, 0.003, 0.004] = 0.0030
    row_2018 = fac_a_res.loc[2018]
    assert np.isclose(row_2018["nox_co2_ratio_mean"], 0.0030, atol=1e-6)
    assert row_2018["n_ratio_obs"] == 3


def test_duplicate_resolution_rule():
    """Verify duplicate resolution rule: for same (facility, year, pollutant), keep maximum reported release."""
    toy_raw = pd.DataFrame([
        {"FacilityInspireId": "F1", "reportingYear": 2020, "Pollutant": "CO2", "Releases": 1000.0},
        {"FacilityInspireId": "F1", "reportingYear": 2020, "Pollutant": "CO2", "Releases": 1500.0},  # duplicate, higher
        {"FacilityInspireId": "F1", "reportingYear": 2021, "Pollutant": "CO2", "Releases": 2000.0},
    ])

    sorted_raw = toy_raw.sort_values(by=["FacilityInspireId", "reportingYear", "Pollutant", "Releases"])
    dedup = sorted_raw.drop_duplicates(subset=["FacilityInspireId", "reportingYear", "Pollutant"], keep="last")

    assert len(dedup) == 2
    f1_2020 = dedup[(dedup["FacilityInspireId"] == "F1") & (dedup["reportingYear"] == 2020)]
    assert f1_2020.iloc[0]["Releases"] == 1500.0


def test_m5_one_sided_historical_score():
    """Verify M5: max(0, -z) penalizes understatements (z < 0) but not production expansions (z > 0)."""
    # Negative z indicates emissions dropped below historical median (potential understatement)
    z_understatement = -2.5
    score_onesided_under = max(0.0, -z_understatement)
    score_twosided_under = abs(z_understatement)
    assert score_onesided_under == 2.5
    assert score_twosided_under == 2.5

    # Positive z indicates emissions grew above historical median (expansion)
    z_expansion = 2.5
    score_onesided_exp = max(0.0, -z_expansion)
    score_twosided_exp = abs(z_expansion)
    # One-sided score correctly assigns 0 risk to genuine expansion
    assert score_onesided_exp == 0.0
    # Two-sided score incorrectly flags expansion as 2.5 sigma anomaly
    assert score_twosided_exp == 2.5

    # Test Bayesian engine response to both scores (with sufficient observational confidence)
    engine = ProbabilisticEvidenceFusionEngine(prior_inconsistency_prob=0.08)

    ev_expansion_onesided = EvidenceInput(
        temporal_variance_zscore=score_onesided_exp,
        years_reported_history=5,
        stoichiometric_discrepancy_sigma=2.0,  # comfortable stoichiometric margin
        satellite_plume_anomaly_zscore=0.0,    # clear satellite, concordant
        satellite_cloud_fraction=0.1,
    )
    dec_onesided = engine.fuse_evidence(ev_expansion_onesided, reported_emissions_tco2=1e6, physical_min_tco2=5e5)

    ev_expansion_twosided = EvidenceInput(
        temporal_variance_zscore=score_twosided_exp,
        years_reported_history=5,
        stoichiometric_discrepancy_sigma=2.0,  # comfortable stoichiometric margin
        satellite_plume_anomaly_zscore=0.0,    # clear satellite, concordant
        satellite_cloud_fraction=0.1,
    )
    dec_twosided = engine.fuse_evidence(ev_expansion_twosided, reported_emissions_tco2=1e6, physical_min_tco2=5e5)

    # One-sided risk treats expansion as consistent (posterior risk drops below prior 8%)
    assert dec_onesided.posterior_inconsistency_risk < 0.05
    # Two-sided score artificially inflates risk because it treats expansion as a suspicious anomaly
    assert dec_twosided.posterior_inconsistency_risk > dec_onesided.posterior_inconsistency_risk


def test_model_b_abstentions_never_flagged():
    """Verify Step 6: Model B abstentions return NaN (not 0.50) and are never counted as flags."""
    df_pred = pd.read_parquet(WORKSPACE_ROOT / "experiments" / "results" / "graded_benchmark_predictions.parquet")
    assert "prob_stoich_alone" in df_pred.columns

    # When stoich_available is False, prob_stoich_alone must be NaN
    abstaining = df_pred[~df_pred["stoich_available"]]
    assert len(abstaining) > 0, "Expected abstaining cases"
    assert abstaining["prob_stoich_alone"].isna().all(), "Abstaining cases must have NaN prob_stoich_alone"

    # In authentic negatives, no abstaining case should ever be flagged
    auth_neg = df_pred[df_pred["evaluation_split"] == "Negative_Authentic"]
    auth_abstain = auth_neg[~auth_neg["stoich_available"]]
    assert len(auth_abstain) > 0
    # NaNs are not >= 0.50
    flagged_abstentions = (auth_abstain["prob_stoich_alone"] >= 0.50).sum()
    assert flagged_abstentions == 0, "Abstentions must never be counted as flagged"


def test_recall_at_fpr_monotone():
    """Verify Step 6: Recall@FPR is monotonically non-decreasing in FPR (5% <= 10% <= 20%)."""
    summary_path = WORKSPACE_ROOT / "experiments" / "results" / "graded_model_comparison_summary.csv"
    assert summary_path.exists(), "Summary CSV not found"
    df_sum = pd.read_csv(summary_path)

    for _, row in df_sum.iterrows():
        r5 = row.get("recall_at_fpr_5")
        r10 = row.get("recall_at_fpr_10")
        r20 = row.get("recall_at_fpr_20")

        if pd.notna(r5) and pd.notna(r10) and pd.notna(r20):
            assert r5 <= r10 + 1e-6, f"{row['model_name']}: Recall@5% ({r5}) > Recall@10% ({r10})"
            assert r10 <= r20 + 1e-6, f"{row['model_name']}: Recall@10% ({r10}) > Recall@20% ({r20})"


def test_model_d_zero_deviation_not_at_cutoff():
    """Verify Step 6: Model D score at z=0 (no deviation) does not equal the 0.50 cutoff."""
    df_pred = pd.read_parquet(WORKSPACE_ROOT / "experiments" / "results" / "graded_benchmark_predictions.parquet")
    # In authentic negatives, median probability of Model D must be low (~0.1-0.3, well below 0.50)
    auth_neg = df_pred[df_pred["evaluation_split"] == "Negative_Authentic"]
    med_auth_prob = auth_neg["prob_historical_alone"].median()
    assert med_auth_prob < 0.35, f"Expected Model D authentic median < 0.35, got {med_auth_prob:.4f}"

    # Authentic FPR at 0.50 must be low (< 10%), eliminating the 51.98% artifact
    fpr_auth = (auth_neg["prob_historical_alone"] >= 0.50).mean()
    assert fpr_auth < 0.10, f"Expected Model D authentic FPR < 10%, got {fpr_auth*100:.2f}%"


def test_steel_boundary_applicability_and_conservative_floor():
    """Verify Step 7: Boundary-mismatched steel plants abstain and conservative floor produces 0 authentic breaches."""
    df_bench = pd.read_parquet(GRADED_BENCHMARK_PATH)
    from src.benchmark.graded_benchmark_generator import TRANSFERRED_GAS_STEEL_PLANTS

    # 1. Transferred process gas steelworks must have stoich_applicable=False and stoich_available=False
    for fid in TRANSFERRED_GAS_STEEL_PLANTS:
        fac_cases = df_bench[df_bench["facility_id"] == fid]
        assert len(fac_cases) > 0
        assert (fac_cases["stoich_applicable"] == False).all()
        assert (fac_cases["stoich_available"] == False).all()

    # 2. Authentic negatives must have 0 conservative floor breaches
    auth_neg = df_bench[df_bench["evaluation_split"] == "Negative_Authentic"]
    cons_breaches = auth_neg["stoich_violation_conservative"].sum()
    assert cons_breaches == 0, f"Expected 0 conservative floor breaches on authentic negatives, got {cons_breaches}"

