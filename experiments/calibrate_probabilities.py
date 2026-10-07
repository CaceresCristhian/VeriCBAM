"""
VeriCBAM Probability Calibration Engine
Implements Platt Scaling (parametric logistic calibration) and Isotonic Regression
(non-parametric monotonic calibration) with Stratified 5-Fold Cross-Validation.

Evaluates:
- Reliability Diagrams (empirical observation frequency vs. predicted risk confidence)
- Brier Score (mean squared error in probability space)
- Expected Calibration Error (ECE across 10 bins)
- Log-Loss / Negative Log-Likelihood
- F1-Score & Accuracy at calibrated thresholds
- Generates interactive Plotly reliability diagrams and ROC curves
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    brier_score_loss,
    log_loss,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    accuracy_score,
)
import plotly.graph_objects as go
from plotly.subplots import make_subplots

WORKSPACE_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

PREDICTIONS_PARQUET = WORKSPACE_ROOT / "experiments" / "results" / "ablation_predictions_101.parquet"
RESULTS_DIR = WORKSPACE_ROOT / "experiments" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error with M equal-width bins."""
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


def run_probability_calibration(n_splits: int = 5, seed: int = 42) -> Dict[str, Any]:
    """Fits and compares Platt Scaling vs Isotonic Regression using Stratified K-Fold CV."""
    if not PREDICTIONS_PARQUET.exists():
        raise FileNotFoundError(f"Predictions parquet missing: {PREDICTIONS_PARQUET}")

    df = pd.read_parquet(PREDICTIONS_PARQUET)
    y_true = df["benchmark_label"].values
    raw_probs = df["prob_model_e"].values

    # Pre-clip raw probabilities for numerically stable log-odds
    eps = 1e-4
    clipped_probs = np.clip(raw_probs, eps, 1.0 - eps)
    raw_logits = np.log(clipped_probs / (1.0 - clipped_probs)).reshape(-1, 1)

    # Initialize out-of-fold prediction arrays
    oof_platt = np.zeros_like(raw_probs)
    oof_isotonic = np.zeros_like(raw_probs)

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    for train_idx, test_idx in skf.split(raw_logits, y_true):
        # 1. Platt Scaling: Logistic Regression on logits
        platt = LogisticRegression(solver="lbfgs", C=1.0)
        platt.fit(raw_logits[train_idx], y_true[train_idx])
        oof_platt[test_idx] = platt.predict_proba(raw_logits[test_idx])[:, 1]

        # 2. Isotonic Regression: non-parametric isotonic fit
        iso = IsotonicRegression(out_of_bounds="clip")
        iso.fit(clipped_probs[train_idx], y_true[train_idx])
        oof_isotonic[test_idx] = iso.predict(clipped_probs[test_idx])

    # Store in DataFrame
    df["prob_uncalibrated"] = raw_probs
    df["prob_platt"] = oof_platt
    df["prob_isotonic"] = oof_isotonic

    # Evaluate methods
    methods = [
        ("Raw Bayesian Posterior (Uncalibrated)", raw_probs),
        ("Platt Scaling (5-Fold CV)", oof_platt),
        ("Isotonic Regression (5-Fold CV)", oof_isotonic),
    ]

    comparison_records = []
    reliability_data = []

    for name, probs in methods:
        brier = float(brier_score_loss(y_true, probs))
        ece = compute_ece(y_true, probs, n_bins=10)
        loss = float(log_loss(y_true, np.clip(probs, eps, 1.0 - eps)))
        preds = (probs >= 0.50).astype(int)
        f1 = float(f1_score(y_true, preds, zero_division=0))
        prec = float(precision_score(y_true, preds, zero_division=0))
        rec = float(recall_score(y_true, preds, zero_division=0))
        acc = float(accuracy_score(y_true, preds))
        roc_auc = float(roc_auc_score(y_true, probs))

        comparison_records.append({
            "calibration_method": name,
            "brier_score": round(brier, 4),
            "ece": round(ece, 4),
            "log_loss": round(loss, 4),
            "f1_score": round(f1, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "accuracy": round(acc, 4),
            "roc_auc": round(roc_auc, 4),
        })

        # Compute reliability curve coordinates
        frac_pos, mean_pred = calibration_curve(y_true, probs, n_bins=10, strategy="uniform")
        for i, (fp, mp) in enumerate(zip(frac_pos, mean_pred)):
            reliability_data.append({
                "calibration_method": name,
                "bin_index": i + 1,
                "mean_predicted_prob": round(float(mp), 4),
                "fraction_of_positives": round(float(fp), 4),
            })

    df_comp = pd.DataFrame(comparison_records)
    df_rel = pd.DataFrame(reliability_data)

    # Save artifacts
    df_comp.to_csv(RESULTS_DIR / "calibration_comparison.csv", index=False)
    df_rel.to_csv(RESULTS_DIR / "reliability_curves.csv", index=False)
    df.to_parquet(RESULTS_DIR / "calibrated_predictions_101.parquet")

    results_json = {
        "dataset_size": len(df),
        "cv_folds": n_splits,
        "comparison": comparison_records,
        "reliability_bins": reliability_data,
    }
    with open(RESULTS_DIR / "calibration_results.json", "w", encoding="utf-8") as f:
        json.dump(results_json, f, indent=2)

    # Generate Interactive Plotly Visualization
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Reliability Curves (Calibration)", "Model Probability Distribution"),
        horizontal_spacing=0.12
    )

    # Diagonal perfect calibration line
    fig.add_trace(
        go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(dash="dash", color="gray"), name="Perfectly Calibrated"),
        row=1, col=1
    )

    colors = {"Raw Bayesian Posterior (Uncalibrated)": "#1f77b4", "Platt Scaling (5-Fold CV)": "#2ca02c", "Isotonic Regression (5-Fold CV)": "#ff7f0e"}
    for name, probs in methods:
        sub_rel = df_rel[df_rel["calibration_method"] == name]
        fig.add_trace(
            go.Scatter(
                x=sub_rel["mean_predicted_prob"],
                y=sub_rel["fraction_of_positives"],
                mode="lines+markers",
                name=name,
                line=dict(color=colors.get(name, "#333333"), width=2),
                marker=dict(size=7)
            ),
            row=1, col=1
        )

    # Probability Histogram for VeriCBAM Fused
    fig.add_trace(
        go.Histogram(x=df[df["benchmark_label"] == 0]["prob_platt"], nbinsx=20, name="Concordant (Label=0)", marker_color="#2ca02c", opacity=0.7),
        row=1, col=2
    )
    fig.add_trace(
        go.Histogram(x=df[df["benchmark_label"] == 1]["prob_platt"], nbinsx=20, name="Inconsistent (Label=1)", marker_color="#d62728", opacity=0.7),
        row=1, col=2
    )

    fig.update_xaxes(title_text="Mean Predicted Risk Probability", range=[0, 1], row=1, col=1)
    fig.update_yaxes(title_text="Observed Inconsistency Frequency", range=[0, 1], row=1, col=1)
    fig.update_xaxes(title_text="Calibrated Inconsistency Risk", range=[0, 1], row=1, col=2)
    fig.update_yaxes(title_text="Case Count", row=1, col=2)

    fig.update_layout(
        title_text="<b>VeriCBAM Probability Calibration & Reliability Assessment (101 Cases, 5-Fold CV)</b>",
        barmode="overlay",
        template="plotly_white",
        width=1150,
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5)
    )

    html_path = RESULTS_DIR / "calibration_and_roc_curves.html"
    fig.write_html(html_path)

    # Print summary table
    print("================================================================================")
    print("VeriCBAM Probability Calibration Results (Stratified 5-Fold Cross-Validation)")
    print("================================================================================\n")
    print(df_comp[["calibration_method", "brier_score", "ece", "log_loss", "f1_score", "roc_auc"]].to_string(index=False))
    print(f"\nArtifacts Saved Successfully:")
    print(f"  - Comparison CSV:  {RESULTS_DIR / 'calibration_comparison.csv'}")
    print(f"  - Reliability CSV: {RESULTS_DIR / 'reliability_curves.csv'}")
    print(f"  - Plotly HTML:     {html_path}")
    print(f"  - Predictions:     {RESULTS_DIR / 'calibrated_predictions_101.parquet'}")

    return results_json


if __name__ == "__main__":
    run_probability_calibration()
