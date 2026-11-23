"""
VeriCBAM Evaluated Multi-Source Benchmark Generator (325 Cases).
Constructs the Layer B graded evaluation suite combining:
- 177 authentic E-PRTR facility-years (2018-2023)
- 140 graded understatements (delta in {5%, 10%, 20%, 30%, 50%})
- 8 controlled process route misclassifications (BF-BOF claiming Scrap-EAF)
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import numpy as np
import pandas as pd

WORKSPACE_ROOT = Path(__file__).parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "02_processed"
SATELLITE_DIR = WORKSPACE_ROOT / "data" / "03_satellite_cache"

CEMENT_CALCINATION_FLOOR = 0.495
BF_BOF_STOICH_FLOOR = 1.35
EAF_STOICH_FLOOR = 0.04

# Steel installations exporting BF/COG process gases to off-site power plants (E-PRTR boundary mismatch)
TRANSFERRED_GAS_STEEL_PLANTS = [
    "https://registry.gdi-de.org/id/de.hb/de.hb.pf.bube-eureg.06-04-11/2005382/5/0",  # ArcelorMittal Bremen
    "https://registry.gdi-de.org/id/de.bb.inspire.pf.eureg/23024102",  # ArcelorMittal Eisenhüttenstadt
    "IT.CAED/741231004.FACILITY",  # Acciaierie d'Italia (Taranto)
    "https://registry.gdi-de.org/id/de.nw.inspire.pf.bube-eureg/arb-2017-112000-100-0077961",  # HKM Duisburg
    "NL.RIVM/000023301.FACILITY",  # Tata Steel IJmuiden
]


@dataclass
class GradedBenchmarkCase:
    case_id: str
    facility_id: str
    facility_name: str
    sector: str
    country: str
    reporting_year: int
    actual_technology_route: str
    declared_production_route: str
    nameplate_capacity_mtpa: Optional[float]
    assumed_production_tonnes_central: Optional[float]
    assumed_production_tonnes_max: Optional[float]
    original_reported_co2_tonnes: float
    declared_co2_tonnes: float
    understatement_delta_pct: float
    benchmark_label: int
    stoich_applicable: bool
    stoich_available: bool
    stoich_floor_central_tco2: Optional[float]
    stoich_floor_max_tco2: Optional[float]
    stoich_violation_central: bool
    stoich_violation_conservative: bool
    stoich_margin_tonnes: Optional[float]
    historical_median_co2_tonnes: float
    historical_log_ratio: float
    historical_z_robust: float
    n_historical_years: int
    reported_nox_tonnes: Optional[float]
    baseline_nox_co2_ratio_mean: Optional[float]
    baseline_nox_co2_ratio_cv: Optional[float]
    nox_co2_anomaly_zscore: Optional[float]
    satellite_zscore: Optional[float]
    satellite_cloud_fraction: float
    satellite_valid_overpasses: int
    satellite_confidence: float
    route_mismatch_detected: bool
    evaluation_split: str


def _resolve_capacity_mtpa(r_info: pd.Series, sector: str) -> float:
    """Resolves verified nameplate capacity (Mtpa) without inventing fallback constants."""
    if sector == "Cement":
        cap_raw = r_info.get("clinker_capacity_mtpa", np.nan)
        cap_mtpa = float(cap_raw) if pd.notna(cap_raw) else np.nan
        if pd.isna(cap_mtpa) or cap_mtpa <= 0:
            cem_raw = r_info.get("cement_capacity_mtpa", np.nan)
            cap_mtpa = float(cem_raw) * 0.75 if pd.notna(cem_raw) else np.nan
        return cap_mtpa
    stl_raw = r_info.get("crude_steel_capacity_mtpa", np.nan)
    return float(stl_raw) if pd.notna(stl_raw) else np.nan


def _build_facility_case(
    *,
    case_id: str,
    row: pd.Series,
    r_info: pd.Series,
    cohort: pd.DataFrame,
    nox_ratios: pd.DataFrame,
    sat_summary: Dict[str, Dict[str, Any]],
    med_lr: float,
    sigma_pooled: float,
    declared_co2: float,
    declared_route: str,
    delta_pct: float,
    benchmark_label: int,
    route_mismatch_detected: bool,
    evaluation_split: str,
    include_nox: bool = True,
) -> GradedBenchmarkCase:
    """Constructs a single standardized GradedBenchmarkCase across all benchmark splits."""
    fid = row["FacilityInspireId"]
    year = int(row["reportingYear"])
    rep_co2 = float(row["co2_tonnes"])
    sector = r_info["sector"]
    country = r_info["country"]
    route = r_info["verified_technology_route"]

    stoich_app = fid not in TRANSFERRED_GAS_STEEL_PLANTS
    cap_mtpa = _resolve_capacity_mtpa(r_info, sector)

    if not stoich_app or pd.isna(cap_mtpa) or cap_mtpa <= 0:
        cap_mtpa_val = float(cap_mtpa) if (pd.notna(cap_mtpa) and cap_mtpa > 0) else None
        prod_central = prod_max = floor_central = floor_max = stoich_margin = None
        stoich_available = False
        stoich_violation_central = stoich_violation_conservative = False
    else:
        cap_mtpa_val = float(cap_mtpa)
        stoich_available = True
        prod_min = cap_mtpa_val * 1e6 * 0.50
        prod_central = cap_mtpa_val * 1e6 * 0.75
        prod_max = cap_mtpa_val * 1e6 * 0.95

        unit_floor = CEMENT_CALCINATION_FLOOR if sector == "Cement" else (
            BF_BOF_STOICH_FLOOR if "BF" in route else EAF_STOICH_FLOOR
        )
        floor_min = prod_min * unit_floor
        floor_central = prod_central * unit_floor
        floor_max = prod_max * unit_floor
        stoich_violation_central = bool(declared_co2 < floor_central)
        stoich_violation_conservative = bool(declared_co2 < floor_min)
        stoich_margin = round(declared_co2 - floor_central, 1)

    fac_all = cohort[cohort["FacilityInspireId"] == fid]
    other_years = fac_all[fac_all["reportingYear"] != year]["co2_tonnes"].values
    hist_med = float(np.median(other_years)) if len(other_years) > 0 else rep_co2
    log_r = float(np.log(max(1.0, declared_co2) / max(1.0, hist_med))) if hist_med > 0 else 0.0
    z_robust = (log_r - med_lr) / sigma_pooled

    nox_t = row.get("nox_tonnes", np.nan) if include_nox else np.nan
    nox_z = nox_base_mean = nox_base_cv = None
    if include_nox and (fid, year) in nox_ratios.index and pd.notna(nox_t) and nox_t > 0:
        n_row = nox_ratios.loc[(fid, year)]
        if isinstance(n_row, pd.DataFrame):
            n_row = n_row.iloc[0]
        if pd.notna(n_row.get("nox_co2_ratio_mean")):
            nox_base_mean = float(n_row["nox_co2_ratio_mean"])
            nox_base_cv = float(n_row["nox_co2_ratio_cv"])
            obs_ratio = float(nox_t) / declared_co2
            sigma_ratio = max(1e-4, nox_base_mean * max(0.08, nox_base_cv))
            nox_z = (obs_ratio - nox_base_mean) / sigma_ratio

    sat_info = sat_summary.get(fid, {"mean_z": 0.0, "n_valid": 0, "mean_cloud": 0.1})

    return GradedBenchmarkCase(
        case_id=case_id,
        facility_id=fid,
        facility_name=row["facilityName"],
        sector=sector,
        country=country,
        reporting_year=year,
        actual_technology_route=route,
        declared_production_route=declared_route,
        nameplate_capacity_mtpa=round(cap_mtpa_val, 4) if cap_mtpa_val is not None else None,
        assumed_production_tonnes_central=round(prod_central, 1) if prod_central is not None else None,
        assumed_production_tonnes_max=round(prod_max, 1) if prod_max is not None else None,
        original_reported_co2_tonnes=round(rep_co2, 1),
        declared_co2_tonnes=round(declared_co2, 1),
        understatement_delta_pct=delta_pct,
        benchmark_label=benchmark_label,
        stoich_applicable=stoich_app,
        stoich_available=stoich_available,
        stoich_floor_central_tco2=round(floor_central, 1) if floor_central is not None else None,
        stoich_floor_max_tco2=round(floor_max, 1) if floor_max is not None else None,
        stoich_violation_central=stoich_violation_central,
        stoich_violation_conservative=stoich_violation_conservative,
        stoich_margin_tonnes=stoich_margin,
        historical_median_co2_tonnes=round(hist_med, 1),
        historical_log_ratio=round(log_r, 4),
        historical_z_robust=round(z_robust, 2),
        n_historical_years=len(other_years),
        reported_nox_tonnes=round(float(nox_t), 1) if pd.notna(nox_t) else None,
        baseline_nox_co2_ratio_mean=round(nox_base_mean, 5) if nox_base_mean else None,
        baseline_nox_co2_ratio_cv=round(nox_base_cv, 4) if nox_base_cv else None,
        nox_co2_anomaly_zscore=round(nox_z, 2) if nox_z is not None else None,
        satellite_zscore=round(sat_info["mean_z"], 2) if sat_info["n_valid"] > 0 else None,
        satellite_cloud_fraction=round(sat_info["mean_cloud"], 2),
        satellite_valid_overpasses=sat_info["n_valid"],
        satellite_confidence=round(min(1.0, sat_info["n_valid"] / 5.0) * (1.0 - sat_info["mean_cloud"]), 2),
        route_mismatch_detected=route_mismatch_detected,
        evaluation_split=evaluation_split,
    )


def generate_graded_benchmark(save_files: bool = True) -> pd.DataFrame:
    """Generates and optionally persists the 325-case graded multi-source evaluation benchmark."""
    print("Generating 325-case graded evaluation benchmark...")
    cohort_path = PROCESSED_DIR / "benchmark_cohort_multipollutant.parquet"
    if not cohort_path.exists():
        cohort_path = PROCESSED_DIR / "benchmark_cohort.parquet"

    cohort = pd.read_parquet(cohort_path)
    reg = pd.read_csv(PROCESSED_DIR / "facility_technology_registry.csv").set_index("FacilityInspireId")

    try:
        from src.data_loaders.nox_baseline import compute_leave_one_year_out_nox_ratios
    except ImportError:
        from data_loaders.nox_baseline import compute_leave_one_year_out_nox_ratios

    nox_ratio_path = PROCESSED_DIR / "facility_nox_co2_ratios.csv"
    if nox_ratio_path.exists():
        nox_df = pd.read_csv(nox_ratio_path)
    else:
        nox_df = compute_leave_one_year_out_nox_ratios(cohort, min_years=3)
    nox_ratios = nox_df.set_index(["facility_inspire_id", "reporting_year"])

    sat_path = SATELLITE_DIR / "s5p_no2_overpasses_2023.parquet"
    sat_summary: Dict[str, Dict[str, Any]] = {}
    if sat_path.exists():
        s5p = pd.read_parquet(sat_path)
        s5p_valid = s5p[s5p["is_valid_qa"] & (~s5p["is_cloud_obscured"])].copy()
        s5p_valid["enhancement"] = s5p_valid["tropospheric_column_density_mol_m2"] - s5p_valid["regional_background_mol_m2"]
        s5p_valid["zscore"] = s5p_valid["enhancement"] / s5p_valid["background_std_mol_m2"].replace(0, np.nan)
        for fid, grp in s5p_valid.groupby("facility_id"):
            sat_summary[fid] = {
                "mean_z": float(grp["zscore"].mean()) if len(grp) > 0 else 0.0,
                "n_valid": len(grp),
                "mean_cloud": float(grp["cloud_fraction"].mean()) if len(grp) > 0 else 0.1,
            }

    all_log_ratios = []
    for _, grp in cohort.groupby("FacilityInspireId"):
        vals = grp["co2_tonnes"].values
        if len(vals) >= 3:
            for i in range(len(vals)):
                other_med = np.median(np.delete(vals, i))
                if other_med > 0 and vals[i] > 0:
                    all_log_ratios.append(np.log(vals[i] / other_med))

    med_lr = float(np.median(all_log_ratios))
    sigma_pooled = float(max(0.05, 1.4826 * np.median(np.abs(np.array(all_log_ratios) - med_lr))))
    print(f"Computed robust pooled historical scale: sigma_pooled = {sigma_pooled:.4f} (n={len(all_log_ratios)})")

    cases: List[GradedBenchmarkCase] = []
    case_idx = 1

    # 1. Authentic Negatives (177 real facility-years)
    for _, row in cohort.iterrows():
        fid = row["FacilityInspireId"]
        rep_co2 = float(row["co2_tonnes"])
        if fid not in reg.index or pd.isna(rep_co2) or rep_co2 <= 0:
            continue
        r_info = reg.loc[fid]
        cases.append(_build_facility_case(
            case_id=f"CASE_{case_idx:04d}_AUTH_NEG",
            row=row, r_info=r_info, cohort=cohort, nox_ratios=nox_ratios, sat_summary=sat_summary,
            med_lr=med_lr, sigma_pooled=sigma_pooled,
            declared_co2=rep_co2, declared_route=r_info["verified_technology_route"],
            delta_pct=0.0, benchmark_label=0, route_mismatch_detected=False,
            evaluation_split="Negative_Authentic", include_nox=True,
        ))
        case_idx += 1

    # 2. Graded Understatements (2023 cohort perturbed by delta in {5%, 10%, 20%, 30%, 50%})
    c2023 = cohort[cohort["reportingYear"] == 2023]
    for delta in [0.05, 0.10, 0.20, 0.30, 0.50]:
        for _, row in c2023.iterrows():
            fid = row["FacilityInspireId"]
            rep_co2 = float(row["co2_tonnes"])
            if fid not in reg.index or pd.isna(rep_co2) or rep_co2 <= 0:
                continue
            r_info = reg.loc[fid]
            cases.append(_build_facility_case(
                case_id=f"CASE_{case_idx:04d}_GRADED_D{int(delta*100)}",
                row=row, r_info=r_info, cohort=cohort, nox_ratios=nox_ratios, sat_summary=sat_summary,
                med_lr=med_lr, sigma_pooled=sigma_pooled,
                declared_co2=rep_co2 * (1.0 - delta), declared_route=r_info["verified_technology_route"],
                delta_pct=round(delta * 100, 1), benchmark_label=1 if delta >= 0.10 else 0,
                route_mismatch_detected=False, evaluation_split="Graded_Understatement", include_nox=True,
            ))
            case_idx += 1

    # 3. Route Mismatch Cases (BF-BOF facilities with verified positive capacity claiming Scrap-EAF)
    bf_facilities = reg[reg["verified_technology_route"].str.contains("BF-BOF", na=False)].index
    for fid in bf_facilities:
        row_match = c2023[c2023["FacilityInspireId"] == fid]
        if row_match.empty:
            continue
        row = row_match.iloc[0]
        r_info = reg.loc[fid]
        cap_mtpa = _resolve_capacity_mtpa(r_info, "Steel")
        if pd.isna(cap_mtpa) or cap_mtpa <= 0:
            continue
        rep_co2 = float(row["co2_tonnes"])
        declared_eaf_co2 = max(1000.0, (cap_mtpa * 1e6 * 0.75) * 0.15)
        cases.append(_build_facility_case(
            case_id=f"CASE_{case_idx:04d}_ROUTE_MISMATCH",
            row=row, r_info=r_info, cohort=cohort, nox_ratios=nox_ratios, sat_summary=sat_summary,
            med_lr=med_lr, sigma_pooled=sigma_pooled,
            declared_co2=declared_eaf_co2, declared_route="Scrap-EAF",
            delta_pct=round(((rep_co2 - declared_eaf_co2) / rep_co2) * 100, 1),
            benchmark_label=1, route_mismatch_detected=True,
            evaluation_split="Route_Mismatch", include_nox=False,
        ))
        case_idx += 1

    df_cases = pd.DataFrame([asdict(c) for c in cases])
    if save_files:
        out_parquet = PROCESSED_DIR / "graded_evaluation_benchmark.parquet"
        out_csv = PROCESSED_DIR / "graded_evaluation_benchmark.csv"
        df_cases.to_parquet(out_parquet, index=False)
        df_cases.to_csv(out_csv, index=False)
        print(f"Saved {len(df_cases)} cases to {out_parquet}")

    return df_cases


if __name__ == "__main__":
    generate_graded_benchmark()
