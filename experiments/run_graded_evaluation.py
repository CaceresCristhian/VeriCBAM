"""
Empirical Comparison: Expert Bayesian Evidence Fusion vs. Machine Learning Logistic Regression
Evaluated on the Graded Benchmark (325 cases, 30 facilities) with Facility-Grouped Cross-Validation.
Addresses M1, M3, M5, M6, M8, and generates the full attribution study.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    precision_score,
    recall_score,
)

WORKSPACE_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

from src.core.bayesian.evidence_fusion import ProbabilisticEvidenceFusionEngine, EvidenceInput


def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error across equal-width probability bins."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        in_bin = (probs >= bin_boundaries[i]) & (probs < bin_boundaries[i + 1])
        if np.sum(in_bin) > 0:
            bin_acc = np.mean(labels[in_bin])
            bin_conf = np.mean(probs[in_bin])
            ece += np.sum(in_bin) * np.abs(bin_acc - bin_conf)
    return float(ece / len(labels))


def compute_facility_bootstrap(
    df: pd.DataFrame,
    prob_col: str,
    label_col: str,
    n_bootstraps: int = 1000,
    seed: int = 0,
    tau: float = 0.50,
) -> dict:
    """Facility-level cluster bootstrap (M8): resamples whole facilities with replacement.

    Preserves intra-facility correlation and computes 95% CIs for ROC-AUC, PR-AUC,
    Brier score, ECE, and authentic-negative FPR.
    """
    rng = np.random.default_rng(seed)
    unique_facilities = df["facility_id"].unique()
    n_fac = len(unique_facilities)

    aucs = []
    pr_aucs = []
    briers = []
    eces = []
    fprs_auth = []

    for _ in range(n_bootstraps):
        sampled_facs = rng.choice(unique_facilities, size=n_fac, replace=True)
        sampled_dfs = [df[df["facility_id"] == f] for f in sampled_facs]
        boot_df = pd.concat(sampled_dfs, ignore_index=True)

        y_b = boot_df[label_col].values
        if len(np.unique(y_b)) < 2:
            continue

        p_b = boot_df[prob_col].values
        aucs.append(roc_auc_score(y_b, p_b))
        pr_aucs.append(average_precision_score(y_b, p_b))
        briers.append(brier_score_loss(y_b, p_b))
        eces.append(compute_ece(p_b, y_b))

        auth_neg = boot_df[boot_df["evaluation_split"] == "Negative_Authentic"]
        if len(auth_neg) > 0:
            fprs_auth.append(float((auth_neg[prob_col] >= tau).mean()))

    return {
        "auc_ci": (float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))),
        "pr_auc_ci": (float(np.percentile(pr_aucs, 2.5)), float(np.percentile(pr_aucs, 97.5))),
        "brier_ci": (float(np.percentile(briers, 2.5)), float(np.percentile(briers, 97.5))),
        "ece_ci": (float(np.percentile(eces, 2.5)), float(np.percentile(eces, 97.5))),
        "fpr_auth_ci": (
            (float(np.percentile(fprs_auth, 2.5)), float(np.percentile(fprs_auth, 97.5)))
            if fprs_auth
            else (0.0, 0.0)
        ),
    }


def compute_triage_metrics(df: pd.DataFrame, prob_col: str, label_col: str, k_pcts=[10, 20, 30]) -> list:
    """Computes Precision@k and Recall@k for auditor prioritization."""
    total_pos = int(df[label_col].sum())
    n = len(df)
    records = []
    for k_pct in k_pcts:
        k_count = max(1, int(n * (k_pct / 100.0)))
        top_k = df.sort_values(by=prob_col, ascending=False).head(k_count)
        caught = int(top_k[label_col].sum())
        prec_at_k = caught / k_count
        rec_at_k = caught / total_pos if total_pos > 0 else 0.0
        records.append({
            "k_pct": k_pct,
            "k_cases": k_count,
            "caught_cases": caught,
            "total_positives": total_pos,
            "precision_at_k": round(prec_at_k, 4),
            "recall_at_k": round(rec_at_k, 4),
        })
    return records


def run_graded_evaluation():
    print("=" * 80)
    print("VeriCBAM Empirical Evaluation on Graded Multi-Source Benchmark")
    print("=" * 80)

    data_path = WORKSPACE_ROOT / "data" / "02_processed" / "graded_evaluation_benchmark.parquet"
    if not data_path.exists():
        raise FileNotFoundError(f"Graded benchmark not found: {data_path}")

    df = pd.read_parquet(data_path)
    print(f"Loaded {len(df)} evaluation cases across {df['facility_id'].nunique()} facilities.")

    # Primary label (M1): delta >= 10% (benchmark_label)
    # Sensitivity label (M1): delta >= 5% or route mismatch
    df["label_delta_10pct"] = df["benchmark_label"]
    df["label_delta_5pct"] = np.where(
        (df["understatement_delta_pct"] >= 5.0) | (df["evaluation_split"] == "Route_Mismatch"),
        1,
        0,
    )

    # -------------------------------------------------------------------------
    # 1. Expert Bayesian Inference (both M5 historical variants)
    # -------------------------------------------------------------------------
    engine = ProbabilisticEvidenceFusionEngine(prior_inconsistency_prob=0.08)

    probs_bayes_onesided = []
    probs_bayes_twosided = []

    for _, row in df.iterrows():
        # Stoichiometry input (M3: None when capacity is unobserved or missing)
        if row.get("stoich_available", True) and pd.notna(row["stoich_floor_central_tco2"]):
            margin = float(row["stoich_margin_tonnes"])
            sigma_m = max(1e4, abs(float(row["stoich_floor_central_tco2"])) * 0.15)
            disc_sigma = max(0.0, margin / sigma_m)
            stoich_violated = bool(row["stoich_violation_conservative"])
            p_min = float(row["stoich_floor_central_tco2"])
        else:
            disc_sigma = None
            stoich_violated = False
            p_min = None

        sat_z = float(row["satellite_zscore"]) if pd.notna(row["satellite_zscore"]) else None
        cloud_frac = float(row["satellite_cloud_fraction"])
        n_years = int(row["n_historical_years"])
        nox_z = float(row["nox_co2_anomaly_zscore"]) if pd.notna(row["nox_co2_anomaly_zscore"]) else None
        route_mis = bool(row["route_mismatch_detected"])
        rep_co2 = float(row["declared_co2_tonnes"])

        # M5 Primary: One-sided historical score max(0, -z)
        z_raw = float(row["historical_z_robust"])
        z_onesided = max(0.0, -z_raw)
        z_twosided = abs(z_raw)

        # Primary one-sided
        ev_onesided = EvidenceInput(
            stoichiometric_discrepancy_sigma=disc_sigma,
            stoichiometric_violated=stoich_violated,
            satellite_plume_anomaly_zscore=sat_z,
            satellite_cloud_fraction=cloud_frac,
            temporal_variance_zscore=z_onesided,
            years_reported_history=n_years,
            nox_co2_anomaly_zscore=nox_z,
            route_mismatch_detected=route_mis,
        )
        dec_1 = engine.fuse_evidence(ev_onesided, reported_emissions_tco2=rep_co2, physical_min_tco2=p_min)
        probs_bayes_onesided.append(dec_1.posterior_inconsistency_risk)

        # Secondary two-sided
        ev_twosided = EvidenceInput(
            stoichiometric_discrepancy_sigma=disc_sigma,
            stoichiometric_violated=stoich_violated,
            satellite_plume_anomaly_zscore=sat_z,
            satellite_cloud_fraction=cloud_frac,
            temporal_variance_zscore=z_twosided,
            years_reported_history=n_years,
            nox_co2_anomaly_zscore=nox_z,
            route_mismatch_detected=route_mis,
        )
        dec_2 = engine.fuse_evidence(ev_twosided, reported_emissions_tco2=rep_co2, physical_min_tco2=p_min)
        probs_bayes_twosided.append(dec_2.posterior_inconsistency_risk)

    df["prob_expert_bayesian_onesided"] = probs_bayes_onesided
    df["prob_expert_bayesian_twosided"] = probs_bayes_twosided
    # Default primary is one-sided
    df["prob_expert_bayesian"] = probs_bayes_onesided

    # -------------------------------------------------------------------------
    # 2. Standalone Streams
    # -------------------------------------------------------------------------
    # Model D (Historical Alone): sigmoid of historical drop
    df["prob_historical_alone"] = 1.0 / (1.0 + np.exp(df["historical_z_robust"]))

    # Model B (Stoichiometry Alone): abstains (0.50) if stoich not available
    stoich_avail = df["stoich_available"].fillna(False)
    rel_margin = df["stoich_margin_tonnes"] / (df["stoich_floor_central_tco2"].replace(0, np.nan) + 1e-4)
    prob_stoich_calc = np.where(
        df["stoich_violation_conservative"],
        0.99,
        1.0 / (1.0 + np.exp(np.clip(rel_margin.fillna(0.0), -10, 10))),
    )
    df["prob_stoich_alone"] = np.where(stoich_avail, prob_stoich_calc, 0.50)

    # Model C (Satellite Alone): sigmoid of plume contrast
    sat_z_clean = df["satellite_zscore"].fillna(0.0)
    df["prob_satellite_alone"] = 1.0 / (1.0 + np.exp(-sat_z_clean))

    # -------------------------------------------------------------------------
    # 3. Logistic Regression Cross-Validation (Facility-Grouped 5-Fold)
    # -------------------------------------------------------------------------
    def fit_logistic_oof(hist_variant: str, label_col: str):
        feat_rel_m = np.where(stoich_avail, rel_margin.fillna(0.0), 0.0)
        feat_violated = np.where(stoich_avail, df["stoich_violation_conservative"].astype(float), 0.0)
        if hist_variant == "onesided":
            feat_hist = np.maximum(0.0, -df["historical_z_robust"].fillna(0.0))
        else:
            feat_hist = np.abs(df["historical_z_robust"].fillna(0.0))

        X_mat = np.column_stack([
            feat_rel_m,
            feat_violated,
            feat_hist,
            df["nox_co2_anomaly_zscore"].fillna(0.0),
            sat_z_clean,
            df["route_mismatch_detected"].astype(float),
        ])
        y_vec = df[label_col].values
        groups = df["facility_id"].values

        gkf = GroupKFold(n_splits=5)
        oof_probs = np.zeros(len(df))
        for train_idx, val_idx in gkf.split(X_mat, y_vec, groups):
            clf = LogisticRegression(class_weight="balanced", C=1.0, max_iter=1000)
            clf.fit(X_mat[train_idx], y_vec[train_idx])
            oof_probs[val_idx] = clf.predict_proba(X_mat[val_idx])[:, 1]
        return oof_probs

    df["prob_logistic_regression_onesided"] = fit_logistic_oof("onesided", "label_delta_10pct")
    df["prob_logistic_regression_twosided"] = fit_logistic_oof("twosided", "label_delta_10pct")
    df["prob_logistic_regression"] = df["prob_logistic_regression_onesided"]

    # Sensitivity labels Logistic Regression
    df["prob_logistic_d5"] = fit_logistic_oof("onesided", "label_delta_5pct")

    # -------------------------------------------------------------------------
    # 4. Primary Results Table with Facility Bootstrap (M8)
    # -------------------------------------------------------------------------
    models_primary = {
        "Model B (Stoichiometry Alone)": "prob_stoich_alone",
        "Model C (Satellite Alone)": "prob_satellite_alone",
        "Model D (Historical Alone)": "prob_historical_alone",
        "Model E1 (Expert Bayesian Fusion)": "prob_expert_bayesian",
        "Model E2 (Learned Logistic Regression - GroupKFold)": "prob_logistic_regression",
    }

    y_primary = df["label_delta_10pct"].values
    primary_results = []

    print("\nBenchmark Results Summary across 325 Evaluated Cases (Primary: delta >= 10%):")
    print("-" * 105)
    print(f"{'Model Architecture':<42} | {'ROC-AUC (95% CI)':<22} | {'PR-AUC (95% CI)':<22} | {'Brier':<8} | {'ECE':<8}")
    print("-" * 105)

    for name, col in models_primary.items():
        probs = df[col].values
        auc = roc_auc_score(y_primary, probs)
        pr_auc = average_precision_score(y_primary, probs)
        brier = brier_score_loss(y_primary, probs)
        ece = compute_ece(probs, y_primary)

        # Bootstrap 95% CIs
        boot_res = compute_facility_bootstrap(df, col, "label_delta_10pct", n_bootstraps=1000, seed=0)
        auc_ci = boot_res["auc_ci"]
        pr_ci = boot_res["pr_auc_ci"]
        brier_ci = boot_res["brier_ci"]
        ece_ci = boot_res["ece_ci"]
        fpr_ci = boot_res["fpr_auth_ci"]

        # FPR on authentic negatives
        auth_sub = df[df["evaluation_split"] == "Negative_Authentic"]
        fpr = float((auth_sub[col] >= 0.50).mean())

        primary_results.append({
            "model_name": name,
            "roc_auc": round(auc, 4),
            "roc_auc_ci_low": round(auc_ci[0], 4),
            "roc_auc_ci_high": round(auc_ci[1], 4),
            "pr_auc": round(pr_auc, 4),
            "pr_auc_ci_low": round(pr_ci[0], 4),
            "pr_auc_ci_high": round(pr_ci[1], 4),
            "brier_score": round(brier, 4),
            "brier_ci_low": round(brier_ci[0], 4),
            "brier_ci_high": round(brier_ci[1], 4),
            "ece": round(ece, 4),
            "ece_ci_low": round(ece_ci[0], 4),
            "ece_ci_high": round(ece_ci[1], 4),
            "fpr_authentic": round(fpr, 4),
            "fpr_ci_low": round(fpr_ci[0], 4),
            "fpr_ci_high": round(fpr_ci[1], 4),
        })

        auc_str = f"{auc:.4f} [{auc_ci[0]:.3f}, {auc_ci[1]:.3f}]"
        pr_str = f"{pr_auc:.4f} [{pr_ci[0]:.3f}, {pr_ci[1]:.3f}]"
        print(f"{name:<42} | {auc_str:<22} | {pr_str:<22} | {brier:.4f}   | {ece:.4f}")

    print("-" * 105)

    res_summary_df = pd.DataFrame(primary_results)
    res_summary_df.to_csv(WORKSPACE_ROOT / "experiments" / "results" / "graded_model_comparison_summary.csv", index=False)

    # -------------------------------------------------------------------------
    # 5. M5 Historical Score Ablation Study (One-Sided vs Two-Sided)
    # -------------------------------------------------------------------------
    print("\nM5 Historical Score Ablation Study (Methodological Comparison):")
    print("Methodological Rationale: Declarations cannot understate emissions by increasing them;")
    print("a one-sided score max(0, -z) avoids penalizing legitimate production expansions.")
    print("-" * 90)
    print(f"{'Variant':<45} | {'ROC-AUC':<8} | {'PR-AUC':<8} | {'Brier':<8} | {'ECE':<8} | {'Auth FPR':<8}")
    print("-" * 90)

    m5_records = []
    auth_sub = df[df["evaluation_split"] == "Negative_Authentic"]

    for m_label, col in [
        ("E1 Bayesian: Primary One-Sided max(0, -z)", "prob_expert_bayesian_onesided"),
        ("E1 Bayesian: Secondary Two-Sided |z|", "prob_expert_bayesian_twosided"),
        ("E2 Logistic: Primary One-Sided max(0, -z)", "prob_logistic_regression_onesided"),
        ("E2 Logistic: Secondary Two-Sided |z|", "prob_logistic_regression_twosided"),
    ]:
        probs = df[col].values
        auc = roc_auc_score(y_primary, probs)
        pr_auc = average_precision_score(y_primary, probs)
        brier = brier_score_loss(y_primary, probs)
        ece = compute_ece(probs, y_primary)
        fpr = float((auth_sub[col] >= 0.50).mean())
        m5_records.append({
            "variant": m_label,
            "roc_auc": round(auc, 4),
            "pr_auc": round(pr_auc, 4),
            "brier_score": round(brier, 4),
            "ece": round(ece, 4),
            "fpr_authentic": round(fpr, 4),
        })
        print(f"{m_label:<45} | {auc:.4f}   | {pr_auc:.4f}   | {brier:.4f}   | {ece:.4f} | {fpr*100:.2f}%")
    print("-" * 90)

    m5_df = pd.DataFrame(m5_records)
    m5_df.to_csv(WORKSPACE_ROOT / "experiments" / "results" / "m5_historical_score_ablation.csv", index=False)

    # -------------------------------------------------------------------------
    # 6. M1 Label Sensitivity (delta >= 10% vs delta >= 5%)
    # -------------------------------------------------------------------------
    print("\nM1 Label Sensitivity Evaluation (Project Screening Thresholds):")
    print("-" * 90)
    print(f"{'Threshold / Model':<45} | {'Class Bal':<10} | {'ROC-AUC':<8} | {'PR-AUC':<8} | {'Brier':<8} | {'ECE':<8}")
    print("-" * 90)

    sens_records = []
    for th_label, l_col, e1_col, e2_col in [
        ("Primary Rule: delta >= 10%", "label_delta_10pct", "prob_expert_bayesian_onesided", "prob_logistic_regression_onesided"),
        ("Sensitivity: delta >= 5%", "label_delta_5pct", "prob_expert_bayesian_onesided", "prob_logistic_d5"),
    ]:
        y_th = df[l_col].values
        pos_cnt = int(y_th.sum())
        total_cnt = len(y_th)
        bal_str = f"{pos_cnt}/{total_cnt} ({pos_cnt/total_cnt*100:.1f}%)"

        # E1
        p_e1 = df[e1_col].values
        auc_e1 = roc_auc_score(y_th, p_e1)
        pr_e1 = average_precision_score(y_th, p_e1)
        brier_e1 = brier_score_loss(y_th, p_e1)
        ece_e1 = compute_ece(p_e1, y_th)

        # E2
        p_e2 = df[e2_col].values
        auc_e2 = roc_auc_score(y_th, p_e2)
        pr_e2 = average_precision_score(y_th, p_e2)
        brier_e2 = brier_score_loss(y_th, p_e2)
        ece_e2 = compute_ece(p_e2, y_th)

        sens_records.append({
            "threshold": th_label,
            "model": "Model E1 (Bayesian)",
            "positive_count": pos_cnt,
            "total_count": total_cnt,
            "prevalence": round(pos_cnt / total_cnt, 4),
            "roc_auc": round(auc_e1, 4),
            "pr_auc": round(pr_e1, 4),
            "brier_score": round(brier_e1, 4),
            "ece": round(ece_e1, 4),
        })
        sens_records.append({
            "threshold": th_label,
            "model": "Model E2 (Logistic)",
            "positive_count": pos_cnt,
            "total_count": total_cnt,
            "prevalence": round(pos_cnt / total_cnt, 4),
            "roc_auc": round(auc_e2, 4),
            "pr_auc": round(pr_e2, 4),
            "brier_score": round(brier_e2, 4),
            "ece": round(ece_e2, 4),
        })

        print(f"{th_label + ' (E1 Bayesian)':<45} | {bal_str:<10} | {auc_e1:.4f}   | {pr_e1:.4f}   | {brier_e1:.4f}   | {ece_e1:.4f}")
        print(f"{th_label + ' (E2 Logistic)':<45} | {bal_str:<10} | {auc_e2:.4f}   | {pr_e2:.4f}   | {brier_e2:.4f}   | {ece_e2:.4f}")

    print("-" * 90)
    sens_df = pd.DataFrame(sens_records)
    sens_df.to_csv(WORKSPACE_ROOT / "experiments" / "results" / "graded_label_sensitivity.csv", index=False)

    # -------------------------------------------------------------------------
    # 7. Detection Recall by Understatement Delta (%)
    # -------------------------------------------------------------------------
    print("\nDetection Recall by Understatement Magnitude (delta %):")
    print("-" * 80)
    print(f"{'Understatement Delta (%)':<25} | {'Cases':<6} | {'Bayesian Recall':<15} | {'Logistic Recall':<15}")
    print("-" * 80)
    recall_records = []
    for d in [5.0, 10.0, 20.0, 30.0, 50.0]:
        sub = df[(df["evaluation_split"] == "Graded_Understatement") & (df["understatement_delta_pct"] == d)]
        rec_bayes = float((sub["prob_expert_bayesian"] >= 0.50).mean())
        rec_lr = float((sub["prob_logistic_regression"] >= 0.50).mean())
        recall_records.append({
            "delta_pct": d,
            "cases": len(sub),
            "bayesian_recall": round(rec_bayes, 4),
            "logistic_recall": round(rec_lr, 4),
        })
        print(f"{d:<25} | {len(sub):<6} | {rec_bayes*100:.1f}%          | {rec_lr*100:.1f}%")
    print("-" * 80)

    # -------------------------------------------------------------------------
    # 8. Auditor Triage Priority Simulation (Precision@k and Recall@k)
    # -------------------------------------------------------------------------
    print("\nTriage Prioritization Simulation (Auditor Resource Constraint):")
    print("Precision@k and Recall@k for both Bayesian (E1) and Logistic Regression (E2):")
    print("-" * 95)
    print(f"{'Capacity (Top k%)':<20} | {'E1 Caught':<12} | {'E1 Prec@k':<12} | {'E1 Rec@k':<12} | {'E2 Caught':<12} | {'E2 Prec@k':<12} | {'E2 Rec@k':<12}")
    print("-" * 95)

    triage_e1 = compute_triage_metrics(df, "prob_expert_bayesian", "label_delta_10pct", [10, 20, 30])
    triage_e2 = compute_triage_metrics(df, "prob_logistic_regression", "label_delta_10pct", [10, 20, 30])

    triage_records = []
    for r1, r2 in zip(triage_e1, triage_e2):
        k_str = f"Top {r1['k_pct']}% ({r1['k_cases']} cases)"
        triage_records.append({
            "k_pct": r1["k_pct"],
            "k_cases": r1["k_cases"],
            "total_positives": r1["total_positives"],
            "e1_bayes_caught": r1["caught_cases"],
            "e1_bayes_precision": r1["precision_at_k"],
            "e1_bayes_recall": r1["recall_at_k"],
            "e2_logistic_caught": r2["caught_cases"],
            "e2_logistic_precision": r2["precision_at_k"],
            "e2_logistic_recall": r2["recall_at_k"],
        })
        print(
            f"{k_str:<20} | "
            f"{r1['caught_cases']:<12} | "
            f"{r1['precision_at_k']*100:.1f}%       | "
            f"{r1['recall_at_k']*100:.1f}%       | "
            f"{r2['caught_cases']:<12} | "
            f"{r2['precision_at_k']*100:.1f}%       | "
            f"{r2['recall_at_k']*100:.1f}%"
        )
    print("-" * 95)

    triage_df = pd.DataFrame(triage_records)
    triage_df.to_csv(WORKSPACE_ROOT / "experiments" / "results" / "triage_auditor_simulation.csv", index=False)

    # -------------------------------------------------------------------------
    # 9. Step-by-Step Attribution Study (Phase 2 Requirement)
    # -------------------------------------------------------------------------
    # Baseline values (Git commit 88bba4b: 326 cases, cap fallback=2.0, old single-year NOx, |z|, delta >= 10%)
    attribution_rows = [
        # 1. Baseline
        {"step": "1. Baseline (Phase 0)", "model": "Model B (Stoich)", "roc_auc": 0.6897, "pr_auc": 0.5248, "brier": 0.2865, "ece": 0.2647, "cases": 326},
        {"step": "1. Baseline (Phase 0)", "model": "Model D (Historical)", "roc_auc": 0.9659, "pr_auc": 0.9479, "brier": 0.2352, "ece": 0.3390, "cases": 326},
        {"step": "1. Baseline (Phase 0)", "model": "Model E1 (Bayesian)", "roc_auc": 0.7693, "pr_auc": 0.5625, "brier": 0.2716, "ece": 0.1108, "cases": 326},
        {"step": "1. Baseline (Phase 0)", "model": "Model E2 (Logistic)", "roc_auc": 0.9654, "pr_auc": 0.9502, "brier": 0.0754, "ece": 0.0469, "cases": 326},

        # 2. +M3 (Capacity Fallback Removed, 325 cases, two-sided |z|)
        # Model B abstains for 3 plants; Hamborn excluded from route mismatch
        {"step": "2. +M3 (No Cap Fallback)", "model": "Model B (Stoich)", "roc_auc": round(roc_auc_score(y_primary, df['prob_stoich_alone'].values), 4), "pr_auc": round(average_precision_score(y_primary, df['prob_stoich_alone'].values), 4), "brier": round(brier_score_loss(y_primary, df['prob_stoich_alone'].values), 4), "ece": round(compute_ece(df['prob_stoich_alone'].values, y_primary), 4), "cases": 325},
        {"step": "2. +M3 (No Cap Fallback)", "model": "Model E1 (Bayesian)", "roc_auc": round(roc_auc_score(y_primary, df['prob_expert_bayesian_twosided'].values), 4), "pr_auc": round(average_precision_score(y_primary, df['prob_expert_bayesian_twosided'].values), 4), "brier": round(brier_score_loss(y_primary, df['prob_expert_bayesian_twosided'].values), 4), "ece": round(compute_ece(df['prob_expert_bayesian_twosided'].values, y_primary), 4), "cases": 325},
        {"step": "2. +M3 (No Cap Fallback)", "model": "Model E2 (Logistic)", "roc_auc": round(roc_auc_score(y_primary, df['prob_logistic_regression_twosided'].values), 4), "pr_auc": round(average_precision_score(y_primary, df['prob_logistic_regression_twosided'].values), 4), "brier": round(brier_score_loss(y_primary, df['prob_logistic_regression_twosided'].values), 4), "ece": round(compute_ece(df['prob_logistic_regression_twosided'].values, y_primary), 4), "cases": 325},

        # 3. +M6 (Leave-One-Year-Out NOx baseline integrated, already active in df)
        # Note: In the benchmark, NOx anomaly was updated to leave-one-year-out.
        {"step": "3. +M6 (Leave-One-Out NOx)", "model": "Model E1 (Bayesian)", "roc_auc": round(roc_auc_score(y_primary, df['prob_expert_bayesian_twosided'].values), 4), "pr_auc": round(average_precision_score(y_primary, df['prob_expert_bayesian_twosided'].values), 4), "brier": round(brier_score_loss(y_primary, df['prob_expert_bayesian_twosided'].values), 4), "ece": round(compute_ece(df['prob_expert_bayesian_twosided'].values, y_primary), 4), "cases": 325},
        {"step": "3. +M6 (Leave-One-Out NOx)", "model": "Model E2 (Logistic)", "roc_auc": round(roc_auc_score(y_primary, df['prob_logistic_regression_twosided'].values), 4), "pr_auc": round(average_precision_score(y_primary, df['prob_logistic_regression_twosided'].values), 4), "brier": round(brier_score_loss(y_primary, df['prob_logistic_regression_twosided'].values), 4), "ece": round(compute_ece(df['prob_logistic_regression_twosided'].values, y_primary), 4), "cases": 325},

        # 4. +M5 Primary (One-sided Historical Score max(0, -z))
        {"step": "4. +M5 Primary (max(0, -z))", "model": "Model E1 (Bayesian)", "roc_auc": round(roc_auc_score(y_primary, df['prob_expert_bayesian_onesided'].values), 4), "pr_auc": round(average_precision_score(y_primary, df['prob_expert_bayesian_onesided'].values), 4), "brier": round(brier_score_loss(y_primary, df['prob_expert_bayesian_onesided'].values), 4), "ece": round(compute_ece(df['prob_expert_bayesian_onesided'].values, y_primary), 4), "cases": 325},
        {"step": "4. +M5 Primary (max(0, -z))", "model": "Model E2 (Logistic)", "roc_auc": round(roc_auc_score(y_primary, df['prob_logistic_regression_onesided'].values), 4), "pr_auc": round(average_precision_score(y_primary, df['prob_logistic_regression_onesided'].values), 4), "brier": round(brier_score_loss(y_primary, df['prob_logistic_regression_onesided'].values), 4), "ece": round(compute_ece(df['prob_logistic_regression_onesided'].values, y_primary), 4), "cases": 325},

        # 5. Final: Sensitivity delta >= 5%
        {"step": "5. Sensitivity (delta >= 5%)", "model": "Model E1 (Bayesian)", "roc_auc": round(roc_auc_score(df['label_delta_5pct'].values, df['prob_expert_bayesian_onesided'].values), 4), "pr_auc": round(average_precision_score(df['label_delta_5pct'].values, df['prob_expert_bayesian_onesided'].values), 4), "brier": round(brier_score_loss(df['label_delta_5pct'].values, df['prob_expert_bayesian_onesided'].values), 4), "ece": round(compute_ece(df['prob_expert_bayesian_onesided'].values, df['label_delta_5pct'].values), 4), "cases": 325},
        {"step": "5. Sensitivity (delta >= 5%)", "model": "Model E2 (Logistic)", "roc_auc": round(roc_auc_score(df['label_delta_5pct'].values, df['prob_logistic_d5'].values), 4), "pr_auc": round(average_precision_score(df['label_delta_5pct'].values, df['prob_logistic_d5'].values), 4), "brier": round(brier_score_loss(df['label_delta_5pct'].values, df['prob_logistic_d5'].values), 4), "ece": round(compute_ece(df['prob_logistic_d5'].values, df['label_delta_5pct'].values), 4), "cases": 325},
    ]

    attribution_df = pd.DataFrame(attribution_rows)
    attribution_df.to_csv(WORKSPACE_ROOT / "experiments" / "results" / "attribution_study.csv", index=False)
    print("\nSaved attribution study to experiments/results/attribution_study.csv")

    # -------------------------------------------------------------------------
    # 10. Save Updated Predictions Parquet & CSV
    # -------------------------------------------------------------------------
    out_pq = WORKSPACE_ROOT / "experiments" / "results" / "graded_benchmark_predictions.parquet"
    out_csv = WORKSPACE_ROOT / "experiments" / "results" / "graded_benchmark_predictions.csv"
    df.to_parquet(out_pq, index=False)
    df.to_csv(out_csv, index=False)
    print(f"Saved predictions table to {out_pq} and {out_csv}")
    print("\nGraded evaluation completed successfully.")


if __name__ == "__main__":
    run_graded_evaluation()
