"""
VeriCBAM Sensitivity Analysis Experiment (Addressing Findings #8, #9, #11 / Orange O2)
Evaluates Prior Sensitivity and Likelihood Ratio (LR) Sensitivity across the 101 Controlled Benchmark Cases.

Scientific Rationale:
1. Likelihood Ratio Sensitivity (Finding #8 / Experiment 8):
   In the expert-parameterized Bayesian evidence-fusion engine, LRs are derived from physical
   margins, plume anomaly z-scores, and historical trajectory shifts.
   To test model robustness against misspecification of expert LRs, we scale log(LR) by
   alpha in [0.50, 0.75, 1.00, 1.25, 1.50].
2. Prior Probability Sensitivity (Finding #9 / Experiment 7):
   The baseline prior P(H) = 0.08 reflects the historical ETS non-compliance rate.
   We test sensitivity across P(H) in [0.02, 0.05, 0.08, 0.12, 0.15] to ensure that:
   - Case ranking remains invariant (Spearman rank correlation ~ 1.0).
   - High-inconsistency cases remain prioritized.
   - Discrimination (ROC-AUC, PR-AUC) remains stable.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import (
    brier_score_loss,
    f1_score,
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
)

WORKSPACE_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

from src.core.bayesian.evidence_fusion import (
    ProbabilisticEvidenceFusionEngine,
    EvidenceInput,
)

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


def run_model_e_custom(
    df: pd.DataFrame,
    prior: float = 0.08,
    lr_scale: float = 1.0,
) -> np.ndarray:
    """Runs Model E with custom prior and scaled log-likelihood ratios."""
    probs = []
    prior_logit = np.log(prior / (1.0 - prior))

    for _, row in df.iterrows():
        sec = row["sector"]
        viol = int(row["stoich_violation"])
        margin = float(row["stoich_margin_tco2_per_t"])
        rep_co2 = float(row["declared_co2_tonnes"])
        lower_bound = float(row["stoich_lower_bound_tco2_per_t"]) * float(row["declared_production_tonnes"])

        # Physical overrule under specified model assumptions
        if viol == 1:
            probs.append(0.999)
            continue

        route_mc = (row["perturbation_type"] == "ROUTE_MISCLASSIFICATION")
        z_sat = float(row["satellite_zscore"])
        conf_sat = float(row["satellite_confidence"])
        z_hist = float(row["historical_zscore"])
        conf_hist = float(row["historical_confidence"])
        util = float(row["capacity_utilization_ratio"])

        ev = EvidenceInput(
            stoichiometric_discrepancy_sigma=margin / 0.10,
            stoichiometric_violated=False,
            satellite_plume_anomaly_zscore=z_sat,
            satellite_cloud_fraction=1.0 - conf_sat,
            temporal_variance_zscore=abs(z_hist),
            years_reported_history=5,
            registry_capacity_ratio=util,
            route_mismatch_detected=route_mc,
        )

        engine = ProbabilisticEvidenceFusionEngine(prior_inconsistency_prob=prior)
        streams = engine.build_evidence_streams(ev)

        # Scale log(LR) by lr_scale: log(LR') = lr_scale * log(LR)
        weighted_log_lr_sum = sum(
            s.weight * s.confidence_factor * (lr_scale * np.log(max(1e-4, s.likelihood_ratio)))
            for s in streams
        )
        post_logit = prior_logit + weighted_log_lr_sum
        p = 1.0 / (1.0 + np.exp(-np.clip(post_logit, -25.0, 25.0)))
        probs.append(float(np.clip(p, 0.001, 0.999)))

    return np.array(probs)


def run_sensitivity_analysis() -> Dict[str, Any]:
    """Executes systematic Likelihood Ratio and Prior Sensitivity analyses."""
    df = pd.read_parquet(BENCHMARK_PARQUET)
    y_true = df["benchmark_label"].values

    # Baseline predictions (Prior=0.08, LR_scale=1.0)
    baseline_probs = run_model_e_custom(df, prior=0.08, lr_scale=1.0)

    # 1. Prior Sensitivity: [0.02, 0.05, 0.08, 0.12, 0.15]
    priors = [0.02, 0.05, 0.08, 0.12, 0.15]
    prior_results = []

    for p_val in priors:
        p_probs = run_model_e_custom(df, prior=p_val, lr_scale=1.0)
        y_pred = (p_probs >= 0.50).astype(int)
        corr, _ = spearmanr(baseline_probs, p_probs)

        prior_results.append({
            "prior_P_H": p_val,
            "mean_posterior": round(float(np.mean(p_probs)), 4),
            "spearman_rank_corr": round(float(corr), 4),
            "brier_score": round(float(brier_score_loss(y_true, p_probs)), 4),
            "ece": round(compute_ece(y_true, p_probs), 4),
            "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
            "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_true, p_probs)), 4),
            "pr_auc": round(float(average_precision_score(y_true, p_probs)), 4),
        })

    # 2. Likelihood Ratio (LR) Scale Sensitivity: [0.50, 0.75, 1.00, 1.25, 1.50]
    lr_scales = [0.50, 0.75, 1.00, 1.25, 1.50]
    lr_results = []

    for scale in lr_scales:
        s_probs = run_model_e_custom(df, prior=0.08, lr_scale=scale)
        y_pred = (s_probs >= 0.50).astype(int)
        corr, _ = spearmanr(baseline_probs, s_probs)

        lr_results.append({
            "lr_scaling_factor": scale,
            "mean_posterior": round(float(np.mean(s_probs)), 4),
            "spearman_rank_corr": round(float(corr), 4),
            "brier_score": round(float(brier_score_loss(y_true, s_probs)), 4),
            "ece": round(compute_ece(y_true, s_probs), 4),
            "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
            "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_true, s_probs)), 4),
            "pr_auc": round(float(average_precision_score(y_true, s_probs)), 4),
        })

    df_prior = pd.DataFrame(prior_results)
    df_lr = pd.DataFrame(lr_results)

    df_prior.to_csv(RESULTS_DIR / "prior_sensitivity_summary.csv", index=False)
    df_lr.to_csv(RESULTS_DIR / "lr_sensitivity_summary.csv", index=False)

    full_output = {
        "prior_sensitivity": prior_results,
        "lr_sensitivity": lr_results,
    }
    with open(RESULTS_DIR / "sensitivity_analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)

    return full_output


if __name__ == "__main__":
    res = run_sensitivity_analysis()
    print("=" * 80)
    print("VeriCBAM Experiment 7: Prior Probability Sensitivity Analysis (P(H) in [0.02 - 0.15])")
    print("=" * 80)
    df_prior = pd.DataFrame(res["prior_sensitivity"])
    print(df_prior.to_string(index=False))

    print("\n" + "=" * 80)
    print("VeriCBAM Experiment 8: Likelihood Ratio (LR) Sensitivity Analysis (Scale in [0.50x - 1.50x])")
    print("=" * 80)
    df_lr = pd.DataFrame(res["lr_sensitivity"])
    print(df_lr.to_string(index=False))
    print("\nSaved artifacts to experiments/results/")
