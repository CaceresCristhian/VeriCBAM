"""
VeriCBAM Facility-Grouped Cross-Validation Experiment (Addressing Finding #12 / Orange O1)
Evaluates out-of-facility generalization using GroupKFold (n_splits=5, groups=facility_id).

Scientific Rationale:
The controlled evaluation benchmark contains 101 cases constructed across 30 European industrial facilities.
Because multiple perturbation cases (baseline, physical violation, historical drop, route mismatch)
can originate from the same industrial facility, standard stratified K-fold cross-validation
risks optimistic calibration metrics due to facility-level correlation.

This module evaluates Platt Scaling and Isotonic Regression under strict GroupKFold cross-validation,
ensuring that entire facilities (all cases associated with a given plant) are held out in test folds.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    brier_score_loss,
    log_loss,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    accuracy_score,
)

WORKSPACE_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

PREDICTIONS_PARQUET = WORKSPACE_ROOT / "experiments" / "results" / "ablation_predictions_101.parquet"
BENCHMARK_PARQUET = WORKSPACE_ROOT / "data" / "02_processed" / "controlled_perturbation_benchmark.parquet"
RESULTS_DIR = WORKSPACE_ROOT / "experiments" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error across M equal-width probability bins."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(y_prob, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)

    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        mask = bin_indices == i
        count = np.sum(mask)
        if count > 0:
            acc = np.mean(y_true[mask])
            conf = np.mean(y_prob[mask])
            ece += (count / n) * abs(acc - conf)
    return float(ece)


def run_facility_grouped_validation(n_splits: int = 5, seed: int = 42) -> Dict[str, Any]:
    """Runs GroupKFold cross-validation grouped strictly by facility_id."""
    if not PREDICTIONS_PARQUET.exists():
        raise FileNotFoundError(f"Predictions parquet missing: {PREDICTIONS_PARQUET}")

    df = pd.read_parquet(PREDICTIONS_PARQUET)
    y_true = df["benchmark_label"].values
    raw_probs = df["prob_model_e"].values
    groups = df["facility_id"].values

    eps = 1e-4
    clipped_probs = np.clip(raw_probs, eps, 1.0 - eps)
    raw_logits = np.log(clipped_probs / (1.0 - clipped_probs)).reshape(-1, 1)

    oof_platt = np.zeros_like(raw_probs)
    oof_isotonic = np.zeros_like(raw_probs)

    gkf = GroupKFold(n_splits=n_splits)
    fold_details = []

    for fold, (train_idx, test_idx) in enumerate(gkf.split(raw_logits, y_true, groups=groups), 1):
        train_facilities = np.unique(groups[train_idx])
        test_facilities = np.unique(groups[test_idx])

        # Verify zero facility leakage
        assert len(set(train_facilities).intersection(set(test_facilities))) == 0, "Facility leakage detected!"

        # Platt Scaling
        platt = LogisticRegression(solver="lbfgs", C=1.0)
        platt.fit(raw_logits[train_idx], y_true[train_idx])
        oof_platt[test_idx] = platt.predict_proba(raw_logits[test_idx])[:, 1]

        # Isotonic Regression
        iso = IsotonicRegression(out_of_bounds="clip")
        iso.fit(clipped_probs[train_idx], y_true[train_idx])
        oof_isotonic[test_idx] = iso.predict(clipped_probs[test_idx])

        fold_details.append({
            "fold": fold,
            "test_cases": int(len(test_idx)),
            "test_facilities_count": int(len(test_facilities)),
            "test_prevalence": float(np.mean(y_true[test_idx])),
        })

    # Add columns
    df["prob_grouped_platt"] = oof_platt
    df["prob_grouped_isotonic"] = oof_isotonic

    methods = [
        {"name": "Raw Posterior (No Calibration)", "probs": raw_probs},
        {"name": "Platt Scaling (GroupKFold)", "probs": oof_platt},
        {"name": "Isotonic Regression (GroupKFold)", "probs": oof_isotonic},
    ]

    metrics_list = []
    for m in methods:
        p = m["probs"]
        y_pred = (p >= 0.5).astype(int)
        p_clipped = np.clip(p, 1e-12, 1.0 - 1e-12)
        metrics_list.append({
            "calibration_method": m["name"],
            "brier_score": round(float(brier_score_loss(y_true, p)), 4),
            "ece": round(compute_ece(y_true, p), 4),
            "log_loss": round(float(log_loss(y_true, p_clipped)), 4),
            "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
            "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_true, p)), 4),
            "pr_auc": round(float(average_precision_score(y_true, p)), 4),
        })

    df_summary = pd.DataFrame(metrics_list)

    # Save summary and predictions
    summary_csv = RESULTS_DIR / "grouped_validation_summary.csv"
    results_json = RESULTS_DIR / "grouped_validation_results.json"
    pred_parquet = RESULTS_DIR / "grouped_validation_predictions.parquet"

    df_summary.to_csv(summary_csv, index=False)
    df.to_parquet(pred_parquet, index=False)

    full_output = {
        "n_splits": n_splits,
        "n_facilities": int(len(np.unique(groups))),
        "n_cases": int(len(df)),
        "folds": fold_details,
        "metrics": metrics_list,
    }
    with open(results_json, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)

    return full_output


if __name__ == "__main__":
    res = run_facility_grouped_validation(n_splits=5)
    print("=" * 80)
    print("VeriCBAM Facility-Grouped Validation Results (GroupKFold, groups=facility_id)")
    print(f"Facilities: {res['n_facilities']} | Total Cases: {res['n_cases']} | Splits: {res['n_splits']}")
    print("=" * 80)
    df_res = pd.DataFrame(res["metrics"])
    print(df_res.to_string(index=False))
    print("\nSaved artifacts to experiments/results/")
