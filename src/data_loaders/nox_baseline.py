"""
VeriCBAM Leave-One-Year-Out NOx/CO2 Combustion Ratio Baseline Calculator.
Calculates authentic facility-year multi-pollutant baselines strictly excluding
the tested year itself from the reference distribution.
"""

import numpy as np
import pandas as pd


def compute_leave_one_year_out_nox_ratios(
    cohort_df: pd.DataFrame, min_years: int = 3
) -> pd.DataFrame:
    """Computes facility-year leave-one-year-out NOx/CO2 combustion ratio baselines.

    For every (facility_id, reporting_year), the baseline is derived exclusively
    from other reporting years of that facility (reporting_year != evaluated_year).
    If fewer than `min_years` other valid observations exist, returns NaN, signaling
    that the NOx evidence stream must abstain.
    """
    results = []
    valid_data = cohort_df[
        (cohort_df["co2_tonnes"] > 0)
        & (cohort_df["nox_tonnes"] > 0)
        & cohort_df["co2_tonnes"].notna()
        & cohort_df["nox_tonnes"].notna()
    ].copy()

    for fid in cohort_df["FacilityInspireId"].dropna().unique():
        fac_rows = valid_data[valid_data["FacilityInspireId"] == fid]
        all_years = cohort_df[cohort_df["FacilityInspireId"] == fid]["reportingYear"].dropna().unique()

        for yr in all_years:
            other_rows = fac_rows[fac_rows["reportingYear"] != yr]
            n_obs = len(other_rows)
            if n_obs >= min_years:
                ratios = other_rows["nox_tonnes"] / other_rows["co2_tonnes"]
                mean_ratio = float(ratios.mean())
                std_ratio = float(ratios.std(ddof=1)) if n_obs > 1 else 0.0
                cv_ratio = float(std_ratio / mean_ratio) if mean_ratio > 0 else 0.0
                results.append({
                    "facility_inspire_id": fid,
                    "reporting_year": int(yr),
                    "nox_co2_ratio_mean": mean_ratio,
                    "nox_co2_ratio_std": std_ratio,
                    "nox_co2_ratio_cv": cv_ratio,
                    "n_ratio_obs": n_obs,
                })
            else:
                results.append({
                    "facility_inspire_id": fid,
                    "reporting_year": int(yr),
                    "nox_co2_ratio_mean": np.nan,
                    "nox_co2_ratio_std": np.nan,
                    "nox_co2_ratio_cv": np.nan,
                    "n_ratio_obs": n_obs,
                })

    return pd.DataFrame(results)
