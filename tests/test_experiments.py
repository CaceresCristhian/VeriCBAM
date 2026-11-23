"""
Unit and integration tests for the 325-case graded evaluation pipeline and sensitivity metrics.
"""

from pathlib import Path
import numpy as np
import pandas as pd

from experiments.run_graded_evaluation import (
    compute_ece,
    compute_recall_at_fpr,
    compute_triage_metrics,
)
from src.core.bayesian.evidence_fusion import ProbabilisticEvidenceFusionEngine, EvidenceInput

RESULTS_DIR = Path(__file__).parents[1] / "experiments" / "results"


def test_ece_metric_calculation():
    """Verify Expected Calibration Error returns 0 for perfect calibration and 1 for inverted predictions."""
    y_true = np.array([0, 0, 1, 1])
    assert compute_ece(np.array([0.0, 0.0, 1.0, 1.0]), y_true, n_bins=5) == 0.0
    assert compute_ece(np.array([1.0, 1.0, 0.0, 0.0]), y_true, n_bins=5) == 1.0


def test_recall_at_fpr_and_triage_metrics():
    """Verify fixed-FPR recall ignores NaN abstentions and triage ranks highest-risk cases first."""
    scores = np.array([0.05, 0.10, 0.15, 0.20, np.nan, 0.85, 0.90, 0.95, 0.30, np.nan])
    auth_mask = np.array([True, True, True, True, True, False, False, False, False, False])
    pos_mask = np.array([False, False, False, False, False, True, True, True, True, True])

    rec, th = compute_recall_at_fpr(scores, auth_mask, pos_mask, target_fpr=0.20)
    assert 0.5 <= rec <= 1.0
    assert 0.15 <= th <= 0.25

    df_triage = pd.DataFrame({"prob": scores, "label": pos_mask.astype(int)})
    records = compute_triage_metrics(df_triage, "prob", "label", k_pcts=[30])
    assert records[0]["caught_cases"] == 3
    assert records[0]["precision_at_k"] == 1.0


def test_graded_model_summary_results_consistency():
    """Verify authoritative 325-case summary CSV includes Stage 1 + Stage 2 models and expected hierarchy."""
    summary_path = RESULTS_DIR / "graded_model_comparison_summary.csv"
    assert summary_path.exists()
    df_sum = pd.read_csv(summary_path).set_index("model_name")

    assert len(df_sum) == 7
    auc_c1 = df_sum.loc["Model C1 (Stage 1 Satellite: TROPOMI NO2)", "roc_auc"]
    auc_c2 = df_sum.loc["Model C2 (Stage 2 Satellite: Thermal & Freight EO)", "roc_auc"]
    auc_e1 = df_sum.loc["Model E1 (Stage 1 Expert Bayesian Fusion)", "roc_auc"]
    auc_e2 = df_sum.loc["Model E2 (Stage 2 Multi-Sensor Bayesian Fusion)", "roc_auc"]
    auc_e3 = df_sum.loc["Model E3 (Learned Logistic Regression - GroupKFold)", "roc_auc"]

    assert auc_c2 > 0.95 and auc_c2 > auc_c1
    assert auc_e2 > auc_e1
    assert auc_e3 > 0.95


def test_bayesian_prior_sensitivity_monotonicity():
    """Verify posterior risk increases monotonically across base priors from 2% to 15%."""
    engine = ProbabilisticEvidenceFusionEngine()
    ev = EvidenceInput(
        stoichiometric_discrepancy_sigma=0.6,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=2.2,
        satellite_cloud_fraction=0.15,
        temporal_variance_zscore=2.5,
        years_reported_history=5,
        thermal_anomaly_zscore=2.1,
        thermal_operating_months_ratio=0.92,
        freight_logistics_zscore=1.5,
    )
    sens = engine.evaluate_prior_sensitivity(
        ev, reported_emissions_tco2=750_000, physical_min_tco2=700_000,
        candidate_priors=[0.02, 0.05, 0.08, 0.12, 0.15],
    )
    probs = list(sens.values())
    assert probs == sorted(probs)
    assert probs[-1] > probs[0]


def test_ui_theme_bento_card_escaping():
    """Verify UI bento_card helper escapes label/subtitle HTML and applies custom value color."""
    from src.ui.theme import bento_card

    html_out = bento_card("Test <Metric>", "96.6%", "Sub & Check", value_color="#4edea3")
    assert "Test &lt;Metric&gt;" in html_out
    assert "Sub &amp; Check" in html_out
    assert 'style="color: #4edea3;"' in html_out
    assert "96.6%" in html_out
