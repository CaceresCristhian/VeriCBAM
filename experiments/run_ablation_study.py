"""
VeriCBAM Experimental Suite - 5-Model Ablation Study
Evaluates the core scientific hypothesis across the Layer B Controlled Inconsistency Benchmark (101 cases):
"To what extent can independent physical, observational, historical, and documentary evidence
be fused into a calibrated decision-support model that identifies inconsistent CBAM emissions
declarations more reliably than isolated evidence sources?"

Evaluated Models:
- Model A: Declaration-Only Baseline (Tabular generic sector intensity outlier detection)
- Model B: Stoichiometric Physical Model Alone (Chemical & thermodynamic mass-balance lower bounds)
- Model C: Satellite Remote Sensing Model Alone (Copernicus Sentinel-5P NO2 plume contrast)
- Model D: Historical Behavioral Model Alone (Facility longitudinal multi-year drift)
- Model E: VeriCBAM Multimodal Fusion (Confidence-weighted Bayesian log-odds synthesis)

Metrics Computed:
- Precision, Recall, F1-Score, Specificity, False Positive Rate (FPR)
- ROC-AUC, PR-AUC (Average Precision)
- Brier Score (Mean Squared Error in probability space)
- Expected Calibration Error (ECE, 10 bins)
- Category-level breakdown (Baselines, Physical Violations, Historical Drops, Route Misclassifications)
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    accuracy_score,
)

# Workspace root
WORKSPACE_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

from src.core.bayesian.evidence_fusion import (
    ProbabilisticEvidenceFusionEngine,
    EvidenceInput,
)

BENCHMARK_PARQUET = WORKSPACE_ROOT / "data" / "02_processed" / "controlled_perturbation_benchmark.parquet"
RESULTS_DIR = WORKSPACE_ROOT / "experiments" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def compute_expected_calibration_error(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> float:
    """
    Computes Expected Calibration Error (ECE) across M equal-width probability bins:
    ECE = sum_m (|B_m| / N) * | acc(B_m) - conf(B_m) |
    """
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(y_prob, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)

    ece = 0.0
    n_samples = len(y_true)

    for i in range(n_bins):
        bin_mask = bin_indices == i
        bin_count = np.sum(bin_mask)
        if bin_count > 0:
            bin_acc = np.mean(y_true[bin_mask])
            bin_conf = np.mean(y_prob[bin_mask])
            ece += (bin_count / n_samples) * abs(bin_acc - bin_conf)

    return float(ece)


def predict_model_a(df: pd.DataFrame) -> np.ndarray:
    """
    Model A: Declaration-Only Baseline (Generic sector intensity deviation).
    Compares declared specific emissions against sector defaults without facility history or physics.
    """
    probs = []
    for _, row in df.iterrows():
        sec = row["sector"]
        route = str(row["declared_production_route"])
        see = float(row["declared_specific_emissions"])

        if sec == "Cement":
            expected_mean = 0.84
            expected_std = 0.10
        else:
            if "Scrap" in route or "EAF" in route:
                expected_mean = 0.25
                expected_std = 0.08
            else:
                expected_mean = 1.85
                expected_std = 0.25

        # Distance below expected mean
        z_under = (expected_mean - see) / expected_std
        # Logistic probability of underreporting
        p = 1.0 / (1.0 + np.exp(-1.5 * (z_under - 1.2)))
        probs.append(float(np.clip(p, 0.01, 0.99)))

    return np.array(probs)


def predict_model_b(df: pd.DataFrame) -> np.ndarray:
    """
    Model B: Stoichiometric Physical Model Alone.
    Evaluates mass-balance lower bounds (calcination/reduction floors).
    """
    probs = []
    for _, row in df.iterrows():
        viol = int(row["stoich_violation"])
        margin = float(row["stoich_margin_tco2_per_t"])

        if viol == 1:
            p = 0.999
        else:
            # Scaled margin: if margin is tight (<0.05), moderate suspicion; if large, low risk
            z_margin = -margin / 0.15
            p = 1.0 / (1.0 + np.exp(-2.0 * (z_margin + 1.0)))
            p = min(0.35, p)  # Cap compliant margin risk
        probs.append(float(np.clip(p, 0.01, 0.999)))

    return np.array(probs)


def predict_model_c(df: pd.DataFrame) -> np.ndarray:
    """
    Model C: Copernicus Sentinel-5P Satellite Alone.
    Evaluates remote-sensing operational plume contrast z-score.
    """
    prior = 0.08
    prior_logit = np.log(prior / (1.0 - prior))
    probs = []

    for _, row in df.iterrows():
        z_sat = float(row["satellite_zscore"])
        conf_sat = float(row["satellite_confidence"])

        if z_sat > 2.5:
            lr = 6.5
        elif z_sat > 1.5:
            lr = 2.8
        elif z_sat < -1.5:
            lr = 0.4
        else:
            lr = 1.0

        post_logit = prior_logit + (conf_sat * np.log(lr))
        p = 1.0 / (1.0 + np.exp(-post_logit))
        probs.append(float(np.clip(p, 0.01, 0.99)))

    return np.array(probs)


def predict_model_d(df: pd.DataFrame) -> np.ndarray:
    """
    Model D: Historical Facility Behavioral Model Alone.
    Evaluates longitudinal deviation against the facility's multi-year historical fingerprint.
    """
    prior = 0.08
    prior_logit = np.log(prior / (1.0 - prior))
    probs = []

    for _, row in df.iterrows():
        z_hist = float(row["historical_zscore"])
        conf_hist = float(row["historical_confidence"])
        drop_magnitude = max(0.0, -z_hist)

        if drop_magnitude > 3.0:
            lr = 7.5
        elif drop_magnitude > 2.0:
            lr = 3.2
        elif drop_magnitude < 0.5:
            lr = 0.45
        else:
            lr = 1.0

        post_logit = prior_logit + (conf_hist * np.log(lr))
        p = 1.0 / (1.0 + np.exp(-post_logit))
        probs.append(float(np.clip(p, 0.01, 0.99)))

    return np.array(probs)


def predict_model_e(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Model E: VeriCBAM Multimodal Fused Model.
    Confidence-weighted Bayesian log-odds synthesis combining Models B + C + D + Registry.
    """
    engine = ProbabilisticEvidenceFusionEngine(prior_inconsistency_prob=0.08)
    probs = []
    confs = []

    for _, row in df.iterrows():
        hist_z_anomaly = max(0.0, -float(row["historical_zscore"]))
        margin = float(row["stoich_margin_tco2_per_t"])
        stoich_viol = bool(row["stoich_violation"] == 1)
        stoich_sigma = 0.0 if stoich_viol else max(0.1, margin / 0.15)
        sat_cloud = max(0.0, 1.0 - float(row["satellite_confidence"]))

        route_mismatch = (
            ("BF-BOF" in str(row["actual_technology_route"]) or "Blast" in str(row["actual_technology_route"]))
            and ("Scrap" in str(row["declared_production_route"]) or "EAF" in str(row["declared_production_route"]))
        )

        ev = EvidenceInput(
            stoichiometric_discrepancy_sigma=stoich_sigma,
            stoichiometric_violated=stoich_viol,
            satellite_plume_anomaly_zscore=float(row["satellite_zscore"]),
            satellite_cloud_fraction=sat_cloud,
            temporal_variance_zscore=hist_z_anomaly,
            years_reported_history=5,
            registry_capacity_ratio=float(row["capacity_utilization_ratio"]) / 0.80 if float(row["capacity_utilization_ratio"]) > 0 else 1.0,
            route_mismatch_detected=route_mismatch,
        )

        rep_emissions = float(row["declared_co2_tonnes"])
        phys_min = float(row["stoich_lower_bound_tco2_per_t"]) * float(row["declared_production_tonnes"])

        dec = engine.fuse_evidence(ev, rep_emissions, phys_min)
        probs.append(dec.posterior_inconsistency_risk)
        confs.append(dec.evidence_confidence_score)

    return np.array(probs), np.array(confs)


def evaluate_model_predictions(
    y_true: np.ndarray, y_prob: np.ndarray, model_name: str, threshold: float = 0.50
) -> Dict[str, Any]:
    """Computes comprehensive quantitative performance and calibration metrics."""
    y_pred = (y_prob >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    accuracy = float(accuracy_score(y_true, y_pred))

    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    roc_auc = float(roc_auc_score(y_true, y_prob))
    pr_auc = float(average_precision_score(y_true, y_prob))
    brier = float(brier_score_loss(y_true, y_prob))
    ece = compute_expected_calibration_error(y_true, y_prob, n_bins=10)

    return {
        "model_name": model_name,
        "threshold": threshold,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "specificity": round(specificity, 4),
        "fpr": round(fpr, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "ece": round(ece, 4),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }


def compute_category_recalls(df: pd.DataFrame, y_prob: np.ndarray, threshold: float = 0.50) -> Dict[str, float]:
    """Computes detection recall across individual controlled perturbation categories."""
    y_pred = (y_prob >= threshold).astype(int)
    results = {}
    for ptype, group in df.groupby("perturbation_type"):
        idx = group.index
        actual_labels = df.loc[idx, "benchmark_label"].values
        preds = y_pred[idx]
        if actual_labels[0] == 1:
            rec = float(np.mean(preds == 1))
            results[f"recall_{ptype}"] = round(rec, 4)
        else:
            spec = float(np.mean(preds == 0))
            results[f"specificity_{ptype}"] = round(spec, 4)
    return results


def run_ablation_experiment() -> Dict[str, Any]:
    """Main execution of the 5-Model Ablation Study."""
    if not BENCHMARK_PARQUET.exists():
        raise FileNotFoundError(f"Benchmark parquet not found at: {BENCHMARK_PARQUET}")

    df = pd.read_parquet(BENCHMARK_PARQUET)
    y_true = df["benchmark_label"].values

    print(f"================================================================================")
    print(f"VeriCBAM 5-Model Ablation Experiment - Layer B Controlled Benchmark")
    print(f"Cohort Size: {len(df)} cases | Inconsistent: {np.sum(y_true == 1)} | Concordant: {np.sum(y_true == 0)}")
    print(f"================================================================================\n")

    # 1. Run predictions across all 5 models
    prob_a = predict_model_a(df)
    prob_b = predict_model_b(df)
    prob_c = predict_model_c(df)
    prob_d = predict_model_d(df)
    prob_e, conf_e = predict_model_e(df)

    models = [
        ("Model A (Declaration Baseline)", prob_a),
        ("Model B (Stoichiometry Alone)", prob_b),
        ("Model C (Satellite Alone)", prob_c),
        ("Model D (Historical Alone)", prob_d),
        ("Model E (VeriCBAM Fused)", prob_e),
    ]

    metrics_list = []
    category_breakdown = {}

    for name, probs in models:
        metrics = evaluate_model_predictions(y_true, probs, name, threshold=0.50)
        cat_rec = compute_category_recalls(df, probs, threshold=0.50)
        metrics.update(cat_rec)
        metrics_list.append(metrics)
        category_breakdown[name] = cat_rec

    # Save detailed prediction table
    df_preds = df.copy()
    df_preds["prob_model_a"] = prob_a
    df_preds["prob_model_b"] = prob_b
    df_preds["prob_model_c"] = prob_c
    df_preds["prob_model_d"] = prob_d
    df_preds["prob_model_e"] = prob_e
    df_preds["conf_model_e"] = conf_e

    df_preds.to_parquet(RESULTS_DIR / "ablation_predictions_101.parquet")
    df_preds.to_csv(RESULTS_DIR / "ablation_predictions_101.csv", index=False)

    # Convert metrics to DataFrame
    df_summary = pd.DataFrame(metrics_list)
    df_summary.to_csv(RESULTS_DIR / "ablation_study_summary.csv", index=False)

    summary_json = {
        "n_cases": len(df),
        "n_inconsistent": int(np.sum(y_true == 1)),
        "n_concordant": int(np.sum(y_true == 0)),
        "models": metrics_list,
    }
    with open(RESULTS_DIR / "ablation_study_results.json", "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2)

    # Print clean formatted summary table
    cols_display = ["model_name", "precision", "recall", "f1_score", "fpr", "roc_auc", "pr_auc", "brier_score", "ece"]
    print(df_summary[cols_display].to_string(index=False))

    print("\n--------------------------------------------------------------------------------")
    print("Subgroup Detection Rates by Perturbation Type (Threshold = 0.50):")
    print("--------------------------------------------------------------------------------")
    for name, cats in category_breakdown.items():
        print(f"[{name}]")
        for k, v in cats.items():
            print(f"  {k}: {v*100:.1f}%")

    print("\nArtifacts Saved Successfully:")
    print(f"  - Metrics JSON:  {RESULTS_DIR / 'ablation_study_results.json'}")
    print(f"  - Summary CSV:   {RESULTS_DIR / 'ablation_study_summary.csv'}")
    print(f"  - Predictions:   {RESULTS_DIR / 'ablation_predictions_101.parquet'}")

    return summary_json


if __name__ == "__main__":
    run_ablation_experiment()
