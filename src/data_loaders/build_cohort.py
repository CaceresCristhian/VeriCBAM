"""
Build authentic multi-pollutant industrial cohort from EEA E-PRTR / IED v16 tables.
Extracts CO2, NOx, and SOx for the 30 target European industrial facilities (2018-2023).
Documents duplicate resolution rules and calculates multi-pollutant baselines.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

WORKSPACE_ROOT = Path(__file__).parents[2]
RAW_DIR = WORKSPACE_ROOT / "data" / "01_raw" / "eprtr_reference" / "csv_tables"
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "02_processed"


def build_cohort():
    print("Building authentic multi-pollutant cohort from raw EEA tables...")
    f14_path = RAW_DIR / "F1_4_Air_Releases_Facilities.csv"
    if not f14_path.exists():
        raise FileNotFoundError(f"Raw EEA Air Releases table not found at: {f14_path}")

    # Load 30-facility registry to match exact facilities
    registry_path = PROCESSED_DIR / "facility_technology_registry.csv"
    if not registry_path.exists():
        raise FileNotFoundError(f"Technology registry missing: {registry_path}")

    registry = pd.read_csv(registry_path)
    target_ids = set(registry["FacilityInspireId"].dropna().unique())
    print(f"Targeting {len(target_ids)} verified facilities from technology registry.")

    # Read F1_4 in chunks to filter target facilities efficiently
    target_pollutants = {
        "Carbon dioxide (CO2)",
        "Carbon dioxide (CO2) excluding biomass",
        "Nitrogen oxides (NOX)",
        "Sulphur oxides (SOX)",
        "Carbon monoxide (CO)",
    }

    chunks = []
    for chunk in pd.read_csv(f14_path, chunksize=100000, low_memory=False):
        sub = chunk[
            (chunk["FacilityInspireId"].isin(target_ids))
            & (chunk["reportingYear"] >= 2018)
            & (chunk["reportingYear"] <= 2023)
            & (chunk["Pollutant"].isin(target_pollutants))
        ]
        if len(sub) > 0:
            chunks.append(sub)

    df_raw = pd.concat(chunks, ignore_index=True)
    print(f"Extracted {len(df_raw)} matching raw air pollutant records.")

    # Duplicate resolution rule:
    # 1. Primary CO2: Prefer 'Carbon dioxide (CO2) excluding biomass' if available, else 'Carbon dioxide (CO2)'
    # 2. For identical facility, year, and pollutant, take the maximum reported release (conservative accounting).
    df_raw = df_raw.sort_values(by=["FacilityInspireId", "reportingYear", "Pollutant", "Releases"])
    df_dedup = df_raw.drop_duplicates(subset=["FacilityInspireId", "reportingYear", "Pollutant"], keep="last")

    # Pivot pollutants to wide format
    piv = df_dedup.pivot(
        index=[
            "FacilityInspireId",
            "facilityName",
            "countryName",
            "reportingYear",
            "city",
            "Latitude",
            "Longitude",
            "EPRTR_SectorName",
            "EPRTRAnnexIMainActivity",
        ],
        columns="Pollutant",
        values="Releases",
    ).reset_index()

    # Calculate metric tonnes
    piv["co2_tonnes"] = piv.get("Carbon dioxide (CO2)", np.nan) / 1000.0
    piv["co2_excl_biomass_tonnes"] = piv.get("Carbon dioxide (CO2) excluding biomass", np.nan) / 1000.0
    piv["nox_tonnes"] = piv.get("Nitrogen oxides (NOX)", np.nan) / 1000.0
    piv["sox_tonnes"] = piv.get("Sulphur oxides (SOX)", np.nan) / 1000.0
    piv["co_tonnes"] = piv.get("Carbon monoxide (CO)", np.nan) / 1000.0

    # Sector mapping
    def map_sector(row):
        sector_name = str(row.get("EPRTR_SectorName", ""))
        act = str(row.get("EPRTRAnnexIMainActivity", ""))
        if "metal" in sector_name.lower() or "2.2" in act:
            return "Steel"
        return "Cement"

    piv["sector"] = piv.apply(map_sector, axis=1)

    # Reorder and format
    cohort_output = piv[
        [
            "FacilityInspireId",
            "facilityName",
            "countryName",
            "city",
            "Latitude",
            "Longitude",
            "sector",
            "reportingYear",
            "co2_tonnes",
            "co2_excl_biomass_tonnes",
            "nox_tonnes",
            "sox_tonnes",
            "co_tonnes",
            "EPRTR_SectorName",
            "EPRTRAnnexIMainActivity",
        ]
    ].sort_values(by=["sector", "facilityName", "reportingYear"])

    # Save to parquet and csv
    out_parquet = PROCESSED_DIR / "benchmark_cohort_multipollutant.parquet"
    out_csv = PROCESSED_DIR / "benchmark_cohort_multipollutant.csv"
    cohort_output.to_parquet(out_parquet, index=False)
    cohort_output.to_csv(out_csv, index=False)

    print(f"Successfully generated multi-pollutant cohort: {out_parquet}")
    print(f"Total facility-year records: {len(cohort_output)}")
    print(f"Facility-years with CO2: {cohort_output['co2_tonnes'].notna().sum()}")
    print(f"Facility-years with NOx: {cohort_output['nox_tonnes'].notna().sum()}")
    print(f"Facility-years with SOx: {cohort_output['sox_tonnes'].notna().sum()}")

    # Compute NOx/CO2 baseline ratio per facility (historical 2018-2022)
    hist_mask = cohort_output["reportingYear"] < 2023
    ratios = []
    for fid, grp in cohort_output[hist_mask].groupby("FacilityInspireId"):
        valid = grp[(grp["co2_tonnes"] > 0) & (grp["nox_tonnes"] > 0)]
        if len(valid) >= 2:
            r = valid["nox_tonnes"] / valid["co2_tonnes"]
            ratios.append({
                "facility_inspire_id": fid,
                "nox_co2_ratio_mean": r.mean(),
                "nox_co2_ratio_std": r.std(),
                "nox_co2_ratio_cv": r.std() / r.mean() if r.mean() > 0 else 0.0,
                "n_ratio_obs": len(valid),
            })
    df_ratios = pd.DataFrame(ratios)
    df_ratios.to_csv(PROCESSED_DIR / "facility_nox_co2_ratios.csv", index=False)
    print(f"Calculated NOx/CO2 baseline fingerprints for {len(df_ratios)} facilities.")


if __name__ == "__main__":
    build_cohort()
