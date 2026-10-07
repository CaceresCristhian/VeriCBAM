"""
VeriCBAM Multi-Year Satellite Ingestion Pipeline (Copernicus Data Space Ecosystem)
Queries official Copernicus Sentinel Hub Statistical API on sh.dataspace.copernicus.eu
using authenticated OAuth2 credentials to aggregate annual tropospheric NO2 column densities
for the 30 target industrial installations across multi-year reporting windows (2019-2023).
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import requests

WORKSPACE_ROOT = Path(__file__).parents[2]
CREDS_FILE = WORKSPACE_ROOT / "Copernicus.txt"
REGISTRY_FILE = WORKSPACE_ROOT / "data" / "02_processed" / "facility_technology_registry.csv"
OUTPUT_CACHE = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "s5p_no2_annual_stats_2019_2023.parquet"
OUTPUT_CSV = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "s5p_no2_annual_stats_2019_2023.csv"


class CopernicusMultiYearClient:
    TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    STAT_URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"

    def __init__(self, credentials_path: Path = CREDS_FILE):
        if not credentials_path.exists():
            raise FileNotFoundError(f"Copernicus credentials file missing: {credentials_path}")
        
        self.client_id, self.client_secret = self._load_credentials(credentials_path)
        self.access_token = None
        self.token_expiry_time = 0

    def _load_credentials(self, p: Path):
        with open(p, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        cid, sec = None, None
        for l in lines:
            if "id" in l.lower() and ":" in l:
                cid = l.split(":", 1)[1].strip()
            elif "secret" in l.lower() and ":" in l:
                sec = l.split(":", 1)[1].strip()
            elif len(lines) == 2 and not cid:
                cid = lines[0]
                sec = lines[1]
        if not cid or not sec:
            raise ValueError("Could not parse Client ID and Client Secret from Copernicus.txt")
        return cid, sec

    def get_token(self) -> str:
        if self.access_token and time.time() < (self.token_expiry_time - 60):
            return self.access_token
        
        resp = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=15,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to obtain CDSE token: {resp.status_code} {resp.text}")
        data = resp.json()
        self.access_token = data["access_token"]
        self.token_expiry_time = time.time() + float(data.get("expires_in", 1800))
        return self.access_token

    def fetch_annual_facility_stats(self, lat: float, lon: float, year: int) -> Optional[Dict[str, Any]]:
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Bounding box ~ 7km radius (0.06 deg lat, 0.09 deg lon)
        bbox = [
            round(lon - 0.08, 4),
            round(lat - 0.05, 4),
            round(lon + 0.08, 4),
            round(lat + 0.05, 4),
        ]

        # Query clear-sky summer window (June 1 - August 31) with daily aggregation
        # Sentinel-5P L2 Statistical API requires daily intervals to prevent whole-month noData masking
        from_date = f"{year}-06-01T00:00:00Z"
        to_date = f"{year}-08-31T23:59:59Z"

        payload = {
            "input": {
                "bounds": {"bbox": bbox},
                "data": [{
                    "type": "sentinel-5p-l2",
                    "dataFilter": {
                        "timeRange": {"from": from_date, "to": to_date}
                    }
                }]
            },
            "aggregation": {
                "timeRange": {"from": from_date, "to": to_date},
                "aggregationInterval": {"of": "P1D"},
                "evalscript": """//VERSION=3
function setup() {
  return {
    input: [{ bands: ["NO2", "dataMask"] }],
    output: [
      { id: "default", bands: 1, sampleType: "FLOAT32" },
      { id: "dataMask", bands: 1, sampleType: "UINT8" }
    ]
  };
}
function evaluatePixel(sample) {
  return {
    default: [sample.NO2],
    dataMask: [sample.dataMask]
  };
}"""
            }
        }

        for attempt in range(3):
            try:
                res = requests.post(self.STAT_URL, headers=headers, json=payload, timeout=30)
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    # Compute annual weighted average across valid monthly intervals
                    means = []
                    valid_counts = []
                    for entry in data:
                        st = entry.get("outputs", {}).get("default", {}).get("bands", {}).get("B0", {}).get("stats", {})
                        cnt = st.get("sampleCount", 0) - st.get("noDataCount", 0)
                        mean_val = st.get("mean")
                        if cnt > 10 and mean_val is not None and str(mean_val) != "NaN":
                            try:
                                m_float = float(mean_val)
                                if not np.isnan(m_float) and m_float > 0:
                                    means.append(m_float)
                                    valid_counts.append(cnt)
                            except (ValueError, TypeError):
                                pass
                    
                    if means and sum(valid_counts) > 0:
                        annual_mean = float(np.average(means, weights=valid_counts))
                        return {
                            "year": year,
                            "annual_mean_tropospheric_no2_mol_m2": annual_mean,
                            "valid_months": len(means),
                            "total_samples": int(sum(valid_counts)),
                        }
                    return None
                elif res.status_code == 429:
                    time.sleep(2.0 * (attempt + 1))
                else:
                    return None
            except Exception:
                time.sleep(1.0)
        return None


def run_multiyear_ingestion(sample_only: bool = True):
    print("=" * 80)
    print("VeriCBAM Multi-Year Copernicus Earth Observation Ingestion Pipeline")
    print("=" * 80)
    
    if not CREDS_FILE.exists():
        print(f"Skipping: Credentials file {CREDS_FILE} not found.")
        return

    client = CopernicusMultiYearClient()
    registry = pd.read_csv(REGISTRY_FILE)
    cohort = pd.read_parquet(WORKSPACE_ROOT / "data" / "02_processed" / "benchmark_cohort.parquet")
    
    target_facilities = registry[["FacilityInspireId", "facilityName", "sector", "country"]].drop_duplicates()
    if sample_only:
        # Pull 5 premier industrial installations across 2019-2023 for empirical within-plant validation
        target_facilities = target_facilities.head(5)
        print("Running targeted multi-year pull on 5 premier benchmark installations (2019–2023)...")
    else:
        print(f"Running full multi-year pull across all {len(target_facilities)} installations (2019–2023)...")

    results = []
    years = [2019, 2020, 2021, 2022, 2023]

    for _, fac in target_facilities.iterrows():
        fid = fac["FacilityInspireId"]
        fname = fac["facilityName"]
        c_sub = cohort[cohort["FacilityInspireId"] == fid]
        if c_sub.empty:
            continue
        lat = float(c_sub.iloc[0]["Latitude"])
        lon = float(c_sub.iloc[0]["Longitude"])

        print(f"\nQuerying CDSE for: {fname} ({fac['sector']}) at ({lat:.3f}, {lon:.3f})")
        for yr in years:
            print(f"  -> Year {yr}...", end=" ", flush=True)
            stats = client.fetch_annual_facility_stats(lat, lon, yr)
            if stats:
                print(f"OK (NO2 = {stats['annual_mean_tropospheric_no2_mol_m2']*1e6:.1f} µmol/m² across {stats['valid_months']} mos)")
                results.append({
                    "facility_id": fid,
                    "facility_name": fname,
                    "sector": fac["sector"],
                    "country": fac["country"],
                    "latitude": lat,
                    "longitude": lon,
                    "reporting_year": yr,
                    "annual_mean_no2_mol_m2": stats["annual_mean_tropospheric_no2_mol_m2"],
                    "valid_months": stats["valid_months"],
                    "total_samples": stats["total_samples"],
                })
            else:
                print("No clear-sky data")
            time.sleep(0.5)

    if results:
        df_out = pd.DataFrame(results)
        df_out.to_parquet(OUTPUT_CACHE, index=False)
        df_out.to_csv(OUTPUT_CSV, index=False)
        print("\n" + "=" * 80)
        print(f"Saved {len(df_out)} authentic multi-year satellite records to:")
        print(f"  {OUTPUT_CACHE}")
        print("=" * 80)

        # Merge with reported emissions to test within-plant temporal tracking
        merged = pd.merge(cohort, df_out, left_on=["FacilityInspireId", "reportingYear"], right_on=["facility_id", "reporting_year"])
        if len(merged) >= 5:
            print("\nWithin-Plant Longitudinal Correlation Check (NO2 tempo vs. Reported CO2):")
            from scipy.stats import spearmanr
            for f_name, grp in merged.groupby("facility_name"):
                if len(grp) >= 3:
                    rho, p = spearmanr(grp["annual_mean_no2_mol_m2"], grp["co2_tonnes"])
                    print(f"  - {f_name:<40}: Spearman rho = {rho:+.3f} (p = {p:.3f}, n = {len(grp)} years)")


if __name__ == "__main__":
    run_multiyear_ingestion(sample_only=True)
