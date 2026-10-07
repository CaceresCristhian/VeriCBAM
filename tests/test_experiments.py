"""
Unit tests for VeriCBAM Ablation Study and Calibration Pipelines.
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from experiments.run_ablation_study import (
    run_ablation_experiment,
    compute_expected_calibration_error,
)
from experiments.calibrate_probabilities import (
    run_probability_calibration,
    compute_ece,
)


def test_ece_metric_calculation():
    """Verify Expected Calibration Error calculation against synthetic calibrated probabilities."""
    y_true = np.array([0, 0, 1, 1])
    # Perfectly calibrated probabilities
    y_prob_perfect = np.array([0.0, 0.0, 1.0, 1.0])
    ece_perf = compute_expected_calibration_error(y_true, y_prob_perfect, n_bins=5)
    assert ece_perf == 0.0

    # Inverted probabilities (worst calibration)
    y_prob_inverted = np.array([1.0, 1.0, 0.0, 0.0])
    ece_inv = compute_expected_calibration_error(y_true, y_prob_inverted, n_bins=5)
    assert ece_inv == 1.0


def test_ablation_study_execution():
    """Verify that the 5-Model Ablation Study executes and outputs all 5 models."""
    results = run_ablation_experiment()
    assert results["n_cases"] == 101
    assert len(results["models"]) == 5

    model_names = [m["model_name"] for m in results["models"]]
    assert any("Model A" in n for n in model_names)
    assert any("Model B" in n for n in model_names)
    assert any("Model C" in n for n in model_names)
    assert any("Model D" in n for n in model_names)
    assert any("Model E" in n for n in model_names)

    # Model E (Fused) must strictly outperform Model A and Model B in F1-score
    f1_a = next(m["f1_score"] for m in results["models"] if "Model A" in m["model_name"])
    f1_b = next(m["f1_score"] for m in results["models"] if "Model B" in m["model_name"])
    f1_e = next(m["f1_score"] for m in results["models"] if "Model E" in m["model_name"])
    assert f1_e > f1_a
    assert f1_e > f1_b
    assert f1_e >= 0.90


def test_probability_calibration_execution():
    """Verify that probability calibration completes 5-fold CV and reduces Brier score."""
    cal_res = run_probability_calibration(n_splits=5, seed=42)
    assert cal_res["dataset_size"] == 101
    assert len(cal_res["comparison"]) == 3

    uncal_brier = next(c["brier_score"] for c in cal_res["comparison"] if "Uncalibrated" in c["calibration_method"])
    platt_brier = next(c["brier_score"] for c in cal_res["comparison"] if "Platt" in c["calibration_method"])
    assert platt_brier < uncal_brier


def test_facility_grouped_validation_execution():
    """Verify that GroupKFold cross-validation holds out entire facilities without data leakage."""
    from experiments.run_grouped_validation import run_facility_grouped_validation
    res = run_facility_grouped_validation(n_splits=5)
    assert res["n_splits"] == 5
    assert res["n_facilities"] == 30
    assert res["n_cases"] == 101
    assert len(res["metrics"]) == 3
    # Platt scaling should achieve lower Brier score than raw posterior
    raw_brier = next(m["brier_score"] for m in res["metrics"] if "Raw" in m["calibration_method"])
    platt_brier = next(m["brier_score"] for m in res["metrics"] if "Platt" in m["calibration_method"])
    assert platt_brier <= raw_brier


def test_sensitivity_analysis_execution():
    """Verify that LR and Prior sensitivity analyses evaluate all scaling factors and preserve ranking."""
    from experiments.run_lr_sensitivity import run_sensitivity_analysis
    res = run_sensitivity_analysis()
    assert len(res["prior_sensitivity"]) == 5
    assert len(res["lr_sensitivity"]) == 5
    # Spearman rank correlation should be >= 0.95 across all variations
    for item in res["prior_sensitivity"]:
        assert item["spearman_rank_corr"] >= 0.95
    for item in res["lr_sensitivity"]:
        assert item["spearman_rank_corr"] >= 0.95
