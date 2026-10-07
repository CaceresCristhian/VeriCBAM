"""
VeriCBAM Evaluated Multi-Source Benchmark Generator
Addresses issues E1, E2, E3, E4, E6, D2:
- E1: Negatives are authentic facility-years (leave-one-year-out).
- E2: Positives are graded understatements: delta in {5%, 10%, 20%, 30%, 50%}.
- E6: Robust pooled z-score based on median absolute deviation across all plants.
- D2: Utilization range [0.50, 0.95] for stoichiometric lower bounds.
- Authentic NOx/CO2 internal consistency stream.
- Satellite plume contrast z-scores included with documented empirical correlation.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

WORKSPACE_ROOT = Path(__file__).parents[2]
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "02_processed"
SATELLITE_DIR = WORKSPACE_ROOT / "data" / "03_satellite_cache"


@dataclass
class GradedBenchmarkCase:
    case_id: str
    facility_id: str
    facility_name: str
    sector: str
    country: str
    reporting_year: int

    # Technology & Activity
    actual_technology_route: str
    declared_production_route: str
    nameplate_capacity_mtpa: float
    assumed_production_tonnes_central: float
    assumed_production_tonnes_max: float

    # Reported & Declared Emissions
    original_reported_co2_tonnes: float
    declared_co2_tonnes: float
    understatement_delta_pct: float
    benchmark_label: int  # 0 = Concordant/Neg, 1 = Material Inconsistency

    # Modality 1: Stoichiometric Bounding
    stoich_floor_central_tco2: float
    stoich_floor_max_tco2: float
    stoich_violation_central: bool
    stoich_violation_conservative: bool  # True only if violated even at max capacity
    stoich_margin_tonnes: float

    # Modality 2: Longitudinal Robust Historical Drift (E6)
    historical_median_co2_tonnes: float
    historical_log_ratio: float
    historical_z_robust: float
    n_historical_years: int

    # Modality 3: Multi-Pollutant NOx/CO2 Internal Consistency
    reported_nox_tonnes: Optional[float]
    baseline_nox_co2_ratio_mean: Optional[float]
    baseline_nox_co2_ratio_cv: Optional[float]
    nox_co2_anomaly_zscore: Optional[float]

    # Modality 4: Satellite Remote Sensing (S5P TROPOMI 2023)
    satellite_zscore: Optional[float]
    satellite_cloud_fraction: float
    satellite_valid_overpasses: int
    satellite_confidence: float

    # Modality 5: Documentary Technology Registry Check
    route_mismatch_detected: bool
    evaluation_split: str  # "Negative_Authentic", "Graded_Understatement", "Route_Mismatch"


def generate_graded_benchmark():
    print("Generating authentic graded evaluation benchmark...")
    cohort_path = PROCESSED_DIR / "benchmark_cohort_multipollutant.parquet"
    if not cohort_path.exists():
        # Fall back to standard cohort if multipollutant not yet built
        cohort_path = PROCESSED_DIR / "benchmark_cohort.parquet"

    cohort = pd.read_parquet(cohort_path)
    reg = pd.read_csv(PROCESSED_DIR / "facility_technology_registry.csv").set_index("FacilityInspireId")

    # Load NOx/CO2 baseline fingerprints if available
    nox_ratio_path = PROCESSED_DIR / "facility_nox_co2_ratios.csv"
    nox_ratios = pd.read_csv(nox_ratio_path).set_index("facility_inspire_id") if nox_ratio_path.exists() else pd.DataFrame()

    # Load satellite 2023 cache
    sat_path = SATELLITE_DIR / "s5p_no2_overpasses_2023.parquet"
    sat_summary = {}
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

    # Step 1: Precompute leave-one-year-out log ratios across all facilities to find pooled sigma (MAD)
    all_log_ratios = []
    for fid, grp in cohort.groupby("FacilityInspireId"):
        vals = grp["co2_tonnes"].values
        if len(vals) >= 3:
            for i in range(len(vals)):
                other_med = np.median(np.delete(vals, i))
                if other_med > 0 and vals[i] > 0:
                    lr = np.log(vals[i] / other_med)
                    all_log_ratios.append(lr)

    med_lr = np.median(all_log_ratios)
    mad_lr = np.median(np.abs(all_log_ratios - med_lr))
    sigma_pooled = max(0.05, 1.4826 * mad_lr)
    print(f"Computed robust pooled historical scale: sigma_pooled = {sigma_pooled:.4f} (MAD across {len(all_log_ratios)} facility-years)")

    cases: List[GradedBenchmarkCase] = []
    case_idx = 1

    # Sector specific floor constants (tCO2 / t output)
    # Cement: calcination process floor ~ 0.49 tCO2/t + BAT thermal combustion ~ 0.28 tCO2/t = 0.77 (or calcination only ~0.50)
    CEMENT_CALCINATION_FLOOR = 0.495
    BF_BOF_STOICH_FLOOR = 1.35  # EU BREF absolute BAT minimum
    EAF_STOICH_FLOOR = 0.04     # Scrap EAF minimum Scope 1

    # 1. AUTHENTIC NEGATIVES: All 177 real facility-years
    for _, row in cohort.iterrows():
        fid = row["FacilityInspireId"]
        year = int(row["reportingYear"])
        rep_co2 = float(row["co2_tonnes"])
        if fid not in reg.index or pd.isna(rep_co2) or rep_co2 <= 0:
            continue

        r_info = reg.loc[fid]
        sector = r_info["sector"]
        country = r_info["country"]
        route = r_info["verified_technology_route"]

        # Capacity & production range [0.50, 0.95]
        if sector == "Cement":
            cap_mtpa = float(r_info.get("clinker_capacity_mtpa", 1.2))
            if pd.isna(cap_mtpa) or cap_mtpa <= 0:
                cap_mtpa = float(r_info.get("cement_capacity_mtpa", 1.5)) * 0.75
        else:
            cap_mtpa = float(r_info.get("crude_steel_capacity_mtpa", 2.0))
            if pd.isna(cap_mtpa) or cap_mtpa <= 0:
                cap_mtpa = 2.0

        prod_central = cap_mtpa * 1e6 * 0.75
        prod_max = cap_mtpa * 1e6 * 0.95

        # Stoichiometric floors
        if sector == "Cement":
            floor_central = prod_central * CEMENT_CALCINATION_FLOOR
            floor_max = prod_max * CEMENT_CALCINATION_FLOOR
        else:
            unit_floor = BF_BOF_STOICH_FLOOR if "BF" in route else EAF_STOICH_FLOOR
            floor_central = prod_central * unit_floor
            floor_max = prod_max * unit_floor

        # Robust leave-one-year-out historical drift
        fac_all = cohort[cohort["FacilityInspireId"] == fid]
        other_years = fac_all[fac_all["reportingYear"] != year]["co2_tonnes"].values
        hist_med = np.median(other_years) if len(other_years) > 0 else rep_co2
        log_r = np.log(rep_co2 / hist_med) if hist_med > 0 else 0.0
        z_robust = (log_r - med_lr) / sigma_pooled

        # Multi-pollutant NOx/CO2 anomaly
        nox_t = row.get("nox_tonnes", np.nan)
        nox_z = None
        nox_base_mean = None
        nox_base_cv = None
        if fid in nox_ratios.index and pd.notna(nox_t) and nox_t > 0:
            n_row = nox_ratios.loc[fid]
            nox_base_mean = float(n_row["nox_co2_ratio_mean"])
            nox_base_cv = float(n_row["nox_co2_ratio_cv"])
            obs_ratio = nox_t / rep_co2
            sigma_ratio = max(1e-4, nox_base_mean * max(0.08, nox_base_cv))
            nox_z = (obs_ratio - nox_base_mean) / sigma_ratio

        # Satellite
        sat_info = sat_summary.get(fid, {"mean_z": 0.0, "n_valid": 0, "mean_cloud": 0.1})

        # Add Authentic Negative Case
        cases.append(GradedBenchmarkCase(
            case_id=f"CASE_{case_idx:04d}_AUTH_NEG",
            facility_id=fid,
            facility_name=row["facilityName"],
            sector=sector,
            country=country,
            reporting_year=year,
            actual_technology_route=route,
            declared_production_route=route,
            nameplate_capacity_mtpa=cap_mtpa,
            assumed_production_tonnes_central=round(prod_central, 1),
            assumed_production_tonnes_max=round(prod_max, 1),
            original_reported_co2_tonnes=round(rep_co2, 1),
            declared_co2_tonnes=round(rep_co2, 1),
            understatement_delta_pct=0.0,
            benchmark_label=0,
            stoich_floor_central_tco2=round(floor_central, 1),
            stoich_floor_max_tco2=round(floor_max, 1),
            stoich_violation_central=bool(rep_co2 < floor_central),
            stoich_violation_conservative=bool(rep_co2 < floor_max),
            stoich_margin_tonnes=round(rep_co2 - floor_central, 1),
            historical_median_co2_tonnes=round(hist_med, 1),
            historical_log_ratio=round(log_r, 4),
            historical_z_robust=round(z_robust, 2),
            n_historical_years=len(other_years),
            reported_nox_tonnes=round(nox_t, 1) if pd.notna(nox_t) else None,
            baseline_nox_co2_ratio_mean=round(nox_base_mean, 5) if nox_base_mean else None,
            baseline_nox_co2_ratio_cv=round(nox_base_cv, 4) if nox_base_cv else None,
            nox_co2_anomaly_zscore=round(nox_z, 2) if nox_z is not None else None,
            satellite_zscore=round(sat_info["mean_z"], 2) if sat_info["n_valid"] > 0 else None,
            satellite_cloud_fraction=round(sat_info["mean_cloud"], 2),
            satellite_valid_overpasses=sat_info["n_valid"],
            satellite_confidence=round(min(1.0, sat_info["n_valid"] / 5.0) * (1.0 - sat_info["mean_cloud"]), 2),
            route_mismatch_detected=False,
            evaluation_split="Negative_Authentic",
        ))
        case_idx += 1

    # 2. GRADED POSITIVES: Understatement deltas applied to 2023 observations across all 30 facilities
    # Deliberate materiality threshold: delta >= 10% is material inconsistency under EU CBAM verification (Implementing Reg 2025/2546)
    deltas = [0.05, 0.10, 0.20, 0.30, 0.50]
    c2023 = cohort[cohort["reportingYear"] == 2023]

    for delta in deltas:
        for _, row in c2023.iterrows():
            fid = row["FacilityInspireId"]
            rep_co2 = float(row["co2_tonnes"])
            if fid not in reg.index or pd.isna(rep_co2) or rep_co2 <= 0:
                continue

            r_info = reg.loc[fid]
            sector = r_info["sector"]
            country = r_info["country"]
            route = r_info["verified_technology_route"]

            if sector == "Cement":
                cap_mtpa = float(r_info.get("clinker_capacity_mtpa", 1.2))
                if pd.isna(cap_mtpa) or cap_mtpa <= 0:
                    cap_mtpa = float(r_info.get("cement_capacity_mtpa", 1.5)) * 0.75
            else:
                cap_mtpa = float(r_info.get("crude_steel_capacity_mtpa", 2.0))
                if pd.isna(cap_mtpa) or cap_mtpa <= 0:
                    cap_mtpa = 2.0

            prod_central = cap_mtpa * 1e6 * 0.75
            prod_max = cap_mtpa * 1e6 * 0.95

            # Declared suppressed CO2
            decl_co2 = rep_co2 * (1.0 - delta)

            # Stoichiometric floors
            if sector == "Cement":
                floor_central = prod_central * CEMENT_CALCINATION_FLOOR
                floor_max = prod_max * CEMENT_CALCINATION_FLOOR
            else:
                unit_floor = BF_BOF_STOICH_FLOOR if "BF" in route else EAF_STOICH_FLOOR
                floor_central = prod_central * unit_floor
                floor_max = prod_max * unit_floor

            # Robust historical drift for suppressed emissions
            fac_all = cohort[cohort["FacilityInspireId"] == fid]
            other_years = fac_all[fac_all["reportingYear"] != 2023]["co2_tonnes"].values
            hist_med = np.median(other_years) if len(other_years) > 0 else rep_co2
            log_r = np.log(decl_co2 / hist_med) if hist_med > 0 else 0.0
            z_robust = (log_r - med_lr) / sigma_pooled

            # NOx / Declared CO2 ratio anomaly: Reported NOx stays at genuine combustion levels while declared CO2 dropped
            nox_t = row.get("nox_tonnes", np.nan)
            nox_z = None
            nox_base_mean = None
            nox_base_cv = None
            if fid in nox_ratios.index and pd.notna(nox_t) and nox_t > 0:
                n_row = nox_ratios.loc[fid]
                nox_base_mean = float(n_row["nox_co2_ratio_mean"])
                nox_base_cv = float(n_row["nox_co2_ratio_cv"])
                obs_ratio = nox_t / decl_co2  # artifically high ratio!
                sigma_ratio = max(1e-4, nox_base_mean * max(0.08, nox_base_cv))
                nox_z = (obs_ratio - nox_base_mean) / sigma_ratio

            sat_info = sat_summary.get(fid, {"mean_z": 0.0, "n_valid": 0, "mean_cloud": 0.1})

            cases.append(GradedBenchmarkCase(
                case_id=f"CASE_{case_idx:04d}_GRADED_D{int(delta*100)}",
                facility_id=fid,
                facility_name=row["facilityName"],
                sector=sector,
                country=country,
                reporting_year=2023,
                actual_technology_route=route,
                declared_production_route=route,
                nameplate_capacity_mtpa=cap_mtpa,
                assumed_production_tonnes_central=round(prod_central, 1),
                assumed_production_tonnes_max=round(prod_max, 1),
                original_reported_co2_tonnes=round(rep_co2, 1),
                declared_co2_tonnes=round(decl_co2, 1),
                understatement_delta_pct=round(delta * 100, 1),
                benchmark_label=1 if delta >= 0.10 else 0,  # 5% is within normal audit tolerance; >=10% is material
                stoich_floor_central_tco2=round(floor_central, 1),
                stoich_floor_max_tco2=round(floor_max, 1),
                stoich_violation_central=bool(decl_co2 < floor_central),
                stoich_violation_conservative=bool(decl_co2 < floor_max),
                stoich_margin_tonnes=round(decl_co2 - floor_central, 1),
                historical_median_co2_tonnes=round(hist_med, 1),
                historical_log_ratio=round(log_r, 4),
                historical_z_robust=round(z_robust, 2),
                n_historical_years=len(other_years),
                reported_nox_tonnes=round(nox_t, 1) if pd.notna(nox_t) else None,
                baseline_nox_co2_ratio_mean=round(nox_base_mean, 5) if nox_base_mean else None,
                baseline_nox_co2_ratio_cv=round(nox_base_cv, 4) if nox_base_cv else None,
                nox_co2_anomaly_zscore=round(nox_z, 2) if nox_z is not None else None,
                satellite_zscore=round(sat_info["mean_z"], 2) if sat_info["n_valid"] > 0 else None,
                satellite_cloud_fraction=round(sat_info["mean_cloud"], 2),
                satellite_valid_overpasses=sat_info["n_valid"],
                satellite_confidence=round(min(1.0, sat_info["n_valid"] / 5.0) * (1.0 - sat_info["mean_cloud"]), 2),
                route_mismatch_detected=False,
                evaluation_split="Graded_Understatement",
            ))
            case_idx += 1

    # 3. ROUTE MISMATCH CASES: 11 controlled route mismatches (integrated BF-BOF falsely claiming Scrap-EAF)
    bf_facilities = reg[reg["verified_technology_route"].str.contains("BF-BOF", na=False)].index[:11]
    for fid in bf_facilities:
        row_match = c2023[c2023["FacilityInspireId"] == fid]
        if len(row_match) == 0:
            continue
        row = row_match.iloc[0]
        rep_co2 = float(row["co2_tonnes"])
        r_info = reg.loc[fid]
        cap_mtpa = float(r_info.get("crude_steel_capacity_mtpa", 2.0))
        prod_central = cap_mtpa * 1e6 * 0.75
        prod_max = cap_mtpa * 1e6 * 0.95

        # Declared under Scrap-EAF route benchmark: ~0.15 tCO2/t instead of ~1.85 tCO2/t
        declared_eaf_co2 = max(1000.0, prod_central * 0.15)

        fac_all = cohort[cohort["FacilityInspireId"] == fid]
        other_years = fac_all[fac_all["reportingYear"] != 2023]["co2_tonnes"].values
        hist_med = np.median(other_years) if len(other_years) > 0 else rep_co2
        log_r = np.log(max(1.0, declared_eaf_co2) / max(1.0, hist_med)) if hist_med > 0 else 0.0
        z_robust = (log_r - med_lr) / sigma_pooled

        sat_info = sat_summary.get(fid, {"mean_z": 0.0, "n_valid": 0, "mean_cloud": 0.1})

        cases.append(GradedBenchmarkCase(
            case_id=f"CASE_{case_idx:04d}_ROUTE_MISMATCH",
            facility_id=fid,
            facility_name=row["facilityName"],
            sector="Steel",
            country=r_info["country"],
            reporting_year=2023,
            actual_technology_route=r_info["verified_technology_route"],
            declared_production_route="Scrap-EAF",
            nameplate_capacity_mtpa=cap_mtpa,
            assumed_production_tonnes_central=round(prod_central, 1),
            assumed_production_tonnes_max=round(prod_max, 1),
            original_reported_co2_tonnes=round(rep_co2, 1),
            declared_co2_tonnes=round(declared_eaf_co2, 1),
            understatement_delta_pct=round(((rep_co2 - declared_eaf_co2) / rep_co2) * 100, 1),
            benchmark_label=1,
            stoich_floor_central_tco2=round(prod_central * BF_BOF_STOICH_FLOOR, 1),
            stoich_floor_max_tco2=round(prod_max * BF_BOF_STOICH_FLOOR, 1),
            stoich_violation_central=True,  # 0.15 is below 1.35
            stoich_violation_conservative=True,
            stoich_margin_tonnes=round(declared_eaf_co2 - prod_central * BF_BOF_STOICH_FLOOR, 1),
            historical_median_co2_tonnes=round(hist_med, 1),
            historical_log_ratio=round(log_r, 4),
            historical_z_robust=round(z_robust, 2),
            n_historical_years=len(other_years),
            reported_nox_tonnes=None,
            baseline_nox_co2_ratio_mean=None,
            baseline_nox_co2_ratio_cv=None,
            nox_co2_anomaly_zscore=None,
            satellite_zscore=round(sat_info["mean_z"], 2) if sat_info["n_valid"] > 0 else None,
            satellite_cloud_fraction=round(sat_info["mean_cloud"], 2),
            satellite_valid_overpasses=sat_info["n_valid"],
            satellite_confidence=round(min(1.0, sat_info["n_valid"] / 5.0) * (1.0 - sat_info["mean_cloud"]), 2),
            route_mismatch_detected=True,
            evaluation_split="Route_Mismatch",
        ))
        case_idx += 1

    df_cases = pd.DataFrame([asdict(c) for c in cases])
    out_parquet = PROCESSED_DIR / "graded_evaluation_benchmark.parquet"
    out_csv = PROCESSED_DIR / "graded_evaluation_benchmark.csv"
    df_cases.to_parquet(out_parquet, index=False)
    df_cases.to_csv(out_csv, index=False)

    print(f"\nSaved Graded Benchmark to {out_parquet}")
    print(f"Total benchmark cases: {len(df_cases)}")
    print("Breakdown by Evaluation Split:")
    print(df_cases["evaluation_split"].value_counts())
    print("\nBreakdown by Understatement Delta (%):")
    print(df_cases["understatement_delta_pct"].value_counts().sort_index())
    print("\nBenchmark Label distribution (0=Concordant, 1=Inconsistent):")
    print(df_cases["benchmark_label"].value_counts())


if __name__ == "__main__":
    generate_graded_benchmark()
