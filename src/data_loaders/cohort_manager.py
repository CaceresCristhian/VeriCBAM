"""
VeriCBAM Data Loader - Benchmark Cohort Manager
Provides access to the curated 30-facility European heavy industrial cohort (Cement & Steel).
All data sourced directly from EEA Industrial Reporting (E-PRTR / IED v16).
"""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

COHORT_PARQUET = Path(__file__).parents[2] / "data" / "02_processed" / "benchmark_cohort.parquet"
COHORT_CSV = Path(__file__).parents[2] / "data" / "02_processed" / "benchmark_cohort.csv"
FACILITIES_META_CSV = Path(__file__).parents[2] / "data" / "02_processed" / "benchmark_facilities_meta.csv"


class CohortManager:
    """Manages access to the verified 30-facility industrial cohort."""

    def __init__(self, data_path: Optional[Path] = None):
        path = data_path or COHORT_PARQUET
        if path.exists():
            self._df = pd.read_parquet(path)
        else:
            self._df = pd.read_csv(COHORT_CSV)

        meta_path = FACILITIES_META_CSV
        if meta_path.exists():
            self._meta = pd.read_csv(meta_path)
        else:
            self._meta = pd.DataFrame()

    def get_all_facilities(self) -> pd.DataFrame:
        """Returns metadata for all 30 benchmark facilities."""
        if not self._meta.empty:
            meta = self._meta.copy()
        else:
            meta = (
                self._df.groupby(["FacilityInspireId", "facilityName", "sector", "countryName", "city"])
                .agg(
                    mean_co2_tonnes=("co2_tonnes", "mean"),
                    min_co2_tonnes=("co2_tonnes", "min"),
                    max_co2_tonnes=("co2_tonnes", "max"),
                    Latitude=("Latitude", "first"),
                    Longitude=("Longitude", "first"),
                )
                .reset_index()
            )

        # Merge technology registry if available
        tech_path = Path(__file__).parents[2] / "data" / "02_processed" / "facility_technology_registry.csv"
        if tech_path.exists():
            df_tech = pd.read_csv(tech_path)
            cols_to_merge = [c for c in df_tech.columns if c not in meta.columns or c == "FacilityInspireId"]
            meta = meta.merge(df_tech[cols_to_merge], on="FacilityInspireId", how="left")

        # Standardize: ensure both uppercase and lowercase exist
        if "Latitude" in meta.columns:
            meta["latitude"] = meta["Latitude"]
        elif "latitude" in meta.columns:
            meta["Latitude"] = meta["latitude"]

        if "Longitude" in meta.columns:
            meta["longitude"] = meta["Longitude"]
        elif "longitude" in meta.columns:
            meta["Longitude"] = meta["longitude"]

        return meta

    def get_facilities_by_sector(self, sector: str) -> pd.DataFrame:
        """Filter cohort facilities by sector: 'Cement' or 'Steel'."""
        meta = self.get_all_facilities()
        return meta[meta["sector"].str.lower() == sector.lower()].reset_index(drop=True)

    def get_facility_time_series(self, facility_id: str) -> pd.DataFrame:
        """Get annual emissions time series (2018-2023) for a specific facility."""
        sub = self._df[self._df["FacilityInspireId"] == facility_id].copy()
        return sub.sort_values(by="reportingYear").reset_index(drop=True)

    def find_facility_by_name(self, search_query: str) -> pd.DataFrame:
        """Fuzzy search facilities by name substring."""
        pattern = search_query.lower()
        return self._meta[self._meta["facilityName"].str.lower().str.contains(pattern, na=False)]


if __name__ == "__main__":
    manager = CohortManager()
    cement = manager.get_facilities_by_sector("Cement")
    steel = manager.get_facilities_by_sector("Steel")
    print(f"Loaded {len(cement)} Cement facilities and {len(steel)} Steel facilities.")
    print("\nCement Sample:")
    print(cement[["facilityName", "countryName", "mean_co2_tonnes"]].head(3))
    print("\nSteel Sample:")
    print(steel[["facilityName", "countryName", "mean_co2_tonnes"]].head(3))
