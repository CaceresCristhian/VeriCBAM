"""
VeriCBAM Satellite Engine - Sentinel-5P TROPOMI Level-2 NO2 client (REAL DATA ONLY)

Data source
-----------
Official ESA/Copernicus Sentinel-5P TROPOMI Level-2 tropospheric NO2 product
(product type ``L2__NO2___``, processing mode ``OFFL``), accessed through the public
Microsoft Planetary Computer mirror of the Copernicus archive
(STAC collection ``sentinel-5p-l2-netcdf``). Access is anonymous; a short-lived
read-only SAS token is obtained from the public Planetary Computer token endpoint.
Licence: Copernicus Sentinel data are free and open (Commission Delegated Regulation
(EU) No 1159/2013). Required attribution: "Contains modified Copernicus Sentinel data [year]".

Method (per facility and per satellite overpass)
------------------------------------------------
1. Only the variables required are range-read from the remote NetCDF4/HDF5 file
   (latitude, longitude, NO2 tropospheric column, qa_value, CRB cloud fraction,
   ECMWF eastward/northward wind). The full ~450 MB granule is never downloaded.
2. Quality filter: ``qa_value >= 0.75`` (recommended threshold for the tropospheric
   column in the S5P NO2 Product Readme File, which removes cloudy / snow-covered /
   poor-retrieval pixels).
3. Near-field signal: mean column of valid pixels whose centre lies within
   ``near_radius_km`` of the facility coordinate (E-PRTR registered location).
4. Regional background: median and robust standard deviation (1.4826 x MAD) of valid
   pixels in an annulus ``bg_inner_km``-``bg_outer_km`` around the facility.
5. Every record carries full provenance (granule id, orbit, processor version,
   source URL without token) and ``data_source = "real_sentinel5p"``.

There is deliberately NO synthetic or simulated fallback: when no real observation is
available, the client returns an empty list and downstream modules must report
``INSUFFICIENT_EVIDENCE``.

Scientific caveat: tropospheric NO2 is an indicator of high-temperature combustion
activity (kiln / furnace / sinter / power plant operation). It is NOT a direct
measurement of facility CO2 emissions and is affected by meteorology, chemistry,
neighbouring sources and the ~5.5 x 3.5 km pixel size.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, asdict, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Sequence

import numpy as np
import pandas as pd

try:  # Use the OS certificate store (needed behind corporate / antivirus TLS proxies)
    import truststore

    truststore.inject_into_ssl()
except Exception:  # pragma: no cover
    pass

import requests

logger = logging.getLogger("vericbam.sentinel5p")

CACHE_DIR = Path(__file__).parents[2] / "data" / "03_satellite_cache"

STAC_SEARCH_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
SAS_TOKEN_URL = "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel5euwest/sentinel-5p"
COLLECTION = "sentinel-5p-l2-netcdf"

DATA_SOURCE_REAL = "real_sentinel5p"

QA_THRESHOLD = 0.75
NEAR_RADIUS_KM = 7.0
BG_INNER_KM = 30.0
BG_OUTER_KM = 80.0
MIN_NEAR_PIXELS = 1
MIN_BG_PIXELS = 20


@dataclass
class SatelliteObservation:
    """One REAL Sentinel-5P overpass extracted over one facility."""

    facility_id: str
    facility_name: str
    latitude: float
    longitude: float
    observation_date: str            # YYYY-MM-DD
    observation_time_utc: str        # ISO timestamp of granule (orbit) mid-time
    satellite_mission: str           # "Sentinel-5P TROPOMI"
    product_type: str                # "L2__NO2___"
    tropospheric_column_density_mol_m2: float   # near-field mean (NaN if no valid pixel)
    regional_background_mol_m2: float           # annulus median
    background_std_mol_m2: float                # annulus robust std (1.4826*MAD)
    cloud_fraction: float            # mean CRB cloud fraction of near-field pixels
    quality_flag_qa_value: float     # mean qa_value of near-field pixels (0-1)
    is_cloud_obscured: bool
    is_valid_qa: bool                # True if near-field AND background pass QA thresholds
    n_near_pixels_valid: int = 0
    n_near_pixels_total: int = 0
    n_background_pixels_valid: int = 0
    wind_u_m_s: float = float("nan")  # ECMWF eastward wind (from product INPUT_DATA)
    wind_v_m_s: float = float("nan")  # ECMWF northward wind
    granule_id: str = ""
    orbit: int = -1
    processor_version: str = ""
    source_href: str = ""
    data_source: str = DATA_SOURCE_REAL
    extraction_params: str = ""

    @property
    def enhancement_mol_m2(self) -> float:
        return self.tropospheric_column_density_mol_m2 - self.regional_background_mol_m2


@dataclass
class FacilityTarget:
    facility_id: str
    facility_name: str
    latitude: float
    longitude: float


def _haversine_km(lat0: float, lon0: float, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    r = 6371.0
    p0, p = np.radians(lat0), np.radians(lat)
    dphi = p - p0
    dl = np.radians(lon - lon0)
    a = np.sin(dphi / 2) ** 2 + np.cos(p0) * np.cos(p) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


class CopernicusSentinel5PClient:
    """Real-data-only client for Sentinel-5P TROPOMI L2 NO2 facility extraction."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        qa_threshold: float = QA_THRESHOLD,
        near_radius_km: float = NEAR_RADIUS_KM,
        bg_inner_km: float = BG_INNER_KM,
        bg_outer_km: float = BG_OUTER_KM,
    ):
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.qa_threshold = qa_threshold
        self.near_radius_km = near_radius_km
        self.bg_inner_km = bg_inner_km
        self.bg_outer_km = bg_outer_km
        self._token: Optional[str] = None
        self._token_time: Optional[datetime] = None
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "VeriCBAM-Research-Client/2.0 (academic capstone)"})

    # ------------------------------------------------------------------ cache
    def cache_path(self, year: int) -> Path:
        return self.cache_dir / f"s5p_no2_overpasses_{year}.parquet"

    def load_cache(self, year: int) -> pd.DataFrame:
        p = self.cache_path(year)
        if not p.exists():
            return pd.DataFrame()
        df = pd.read_parquet(p)
        # Defensive provenance gate: never serve anything that is not real satellite data
        return df[df["data_source"] == DATA_SOURCE_REAL].copy()

    @property
    def extraction_params(self) -> str:
        return json.dumps(
            {
                "qa_threshold": self.qa_threshold,
                "near_radius_km": self.near_radius_km,
                "bg_annulus_km": [self.bg_inner_km, self.bg_outer_km],
                "product": "L2__NO2___ OFFL",
                "variable": "PRODUCT/nitrogendioxide_tropospheric_column",
            }
        )

    # ------------------------------------------------------------------ STAC
    def _sas_token(self) -> str:
        if self._token and self._token_time and datetime.utcnow() - self._token_time < timedelta(minutes=30):
            return self._token
        r = self._session.get(SAS_TOKEN_URL, timeout=30)
        r.raise_for_status()
        self._token = r.json()["token"]
        self._token_time = datetime.utcnow()
        return self._token

    def search_granules(
        self,
        bbox: Sequence[float],
        start: date,
        end: date,
        daytime_utc_hours: tuple = (8, 15),
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """Searches OFFL L2 NO2 granules intersecting ``bbox`` (minlon, minlat, maxlon, maxlat)."""
        body = {
            "collections": [COLLECTION],
            "bbox": list(bbox),
            "datetime": f"{start.isoformat()}T00:00:00Z/{end.isoformat()}T23:59:59Z",
            "query": {"s5p:product_name": {"eq": "no2"}, "s5p:processing_mode": {"eq": "OFFL"}},
            "limit": limit,
        }
        out: List[Dict[str, Any]] = []
        url = STAC_SEARCH_URL
        while url:
            r = self._session.post(url, json=body, timeout=60)
            r.raise_for_status()
            js = r.json()
            for f in js.get("features", []):
                p = f["properties"]
                t = datetime.fromisoformat(p["datetime"].replace("Z", "+00:00"))
                if not (daytime_utc_hours[0] <= t.hour <= daytime_utc_hours[1]):
                    continue  # NO2 is retrieved on the sunlit side only
                out.append(
                    {
                        "granule_id": f["id"],
                        "datetime": p["datetime"],
                        "orbit": p.get("sat:absolute_orbit", -1),
                        "collection_identifier": p.get("s5p:collection_identifier", ""),
                        "href": f["assets"]["no2"]["href"],
                    }
                )
            nxt = [l for l in js.get("links", []) if l.get("rel") == "next"]
            if nxt and nxt[0].get("body"):
                body = nxt[0]["body"]
                url = nxt[0].get("href", STAC_SEARCH_URL)
            else:
                url = None
        return out

    # ------------------------------------------------------------- extraction
    def extract_granule(self, granule: Dict[str, Any], targets: Sequence[FacilityTarget]) -> List[SatelliteObservation]:
        """Range-reads one real granule and extracts near-field/background statistics for each target."""
        import fsspec
        import h5py

        url = f"{granule['href']}?{self._sas_token()}"
        fs = fsspec.filesystem("http", block_size=4 * 1024 * 1024)
        results: List[SatelliteObservation] = []
        with fs.open(url, "rb", cache_type="readahead") as fobj, h5py.File(fobj, "r") as f:
            g = f["PRODUCT"]
            processor_version = str(f.attrs.get("processor_version", b"").decode() if isinstance(f.attrs.get("processor_version", b""), bytes) else f.attrs.get("processor_version", ""))
            lat_all = g["latitude"][0]
            # Restrict to scanlines covering the cohort latitude band (reduces bytes read)
            lat_min = min(t.latitude for t in targets) - 1.5
            lat_max = max(t.latitude for t in targets) + 1.5
            rows = np.where(((lat_all >= lat_min) & (lat_all <= lat_max)).any(axis=1))[0]
            if rows.size == 0:
                return results
            r0, r1 = int(rows.min()), int(rows.max()) + 1
            lat = lat_all[r0:r1]
            lon = g["longitude"][0, r0:r1]
            fill = None
            no2_ds = g["nitrogendioxide_tropospheric_column"]
            fill = no2_ds.attrs.get("_FillValue", [9.96921e36])[0]
            no2 = no2_ds[0, r0:r1].astype("float64")
            no2[no2 >= fill * 0.99] = np.nan
            qa_ds = g["qa_value"]
            qa = qa_ds[0, r0:r1].astype("float64") * float(qa_ds.attrs.get("scale_factor", [0.01])[0])
            inp = g["SUPPORT_DATA"]["INPUT_DATA"]
            cf = inp["cloud_fraction_crb"][0, r0:r1].astype("float64")
            u = inp["eastward_wind"][0, r0:r1].astype("float64")
            v = inp["northward_wind"][0, r0:r1].astype("float64")
            for arr in (cf, u, v):
                arr[np.abs(arr) > 1e30] = np.nan

            obs_date = granule["datetime"][:10]
            for t in targets:
                if not (lat.min() - 0.5 <= t.latitude <= lat.max() + 0.5):
                    continue
                d = _haversine_km(t.latitude, t.longitude, lat, lon)
                if np.nanmin(d) > self.near_radius_km:
                    continue  # facility outside this swath
                near = d <= self.near_radius_km
                ring = (d >= self.bg_inner_km) & (d <= self.bg_outer_km)
                good = (qa >= self.qa_threshold) & np.isfinite(no2)
                near_v = near & good
                ring_v = ring & good
                n_near, n_near_tot, n_bg = int(near_v.sum()), int(near.sum()), int(ring_v.sum())
                if n_bg >= MIN_BG_PIXELS:
                    bg_vals = no2[ring_v]
                    bg_med = float(np.median(bg_vals))
                    bg_std = float(1.4826 * np.median(np.abs(bg_vals - bg_med)))
                else:
                    bg_med, bg_std = float("nan"), float("nan")
                near_mean = float(np.mean(no2[near_v])) if n_near >= MIN_NEAR_PIXELS else float("nan")
                cf_near = float(np.nanmean(cf[near])) if n_near_tot else float("nan")
                qa_near = float(np.nanmean(qa[near])) if n_near_tot else float("nan")
                i_nearest = np.unravel_index(np.nanargmin(d), d.shape)
                valid = n_near >= MIN_NEAR_PIXELS and n_bg >= MIN_BG_PIXELS and bg_std > 0
                results.append(
                    SatelliteObservation(
                        facility_id=t.facility_id,
                        facility_name=t.facility_name,
                        latitude=round(t.latitude, 5),
                        longitude=round(t.longitude, 5),
                        observation_date=obs_date,
                        observation_time_utc=granule["datetime"],
                        satellite_mission="Sentinel-5P TROPOMI",
                        product_type="L2__NO2___",
                        tropospheric_column_density_mol_m2=near_mean,
                        regional_background_mol_m2=bg_med,
                        background_std_mol_m2=bg_std,
                        cloud_fraction=cf_near,
                        quality_flag_qa_value=qa_near,
                        is_cloud_obscured=bool(n_near == 0 and n_near_tot > 0),
                        is_valid_qa=bool(valid),
                        n_near_pixels_valid=n_near,
                        n_near_pixels_total=n_near_tot,
                        n_background_pixels_valid=n_bg,
                        wind_u_m_s=float(u[i_nearest]),
                        wind_v_m_s=float(v[i_nearest]),
                        granule_id=granule["granule_id"],
                        orbit=int(granule.get("orbit", -1)),
                        processor_version=processor_version,
                        source_href=granule["href"],
                        data_source=DATA_SOURCE_REAL,
                        extraction_params=self.extraction_params,
                    )
                )
        return results

    # ---------------------------------------------------------------- public
    def get_facility_observations(
        self,
        facility_id: str,
        facility_name: str,
        lat: float,
        lon: float,
        year: int = 2023,
        product: str = "L2__NO2___",
        fetch_if_missing: bool = False,
        days: Optional[Sequence[date]] = None,
    ) -> List[SatelliteObservation]:
        """
        Returns REAL cached Sentinel-5P overpasses for a facility-year.

        If nothing is cached and ``fetch_if_missing`` is True, real granules are queried and
        extracted on demand (slow: several seconds per granule). Otherwise an empty list is
        returned and the caller must treat satellite evidence as unavailable.
        """
        df = self.load_cache(year)
        if not df.empty:
            sub = df[df["facility_id"] == facility_id]
            if not sub.empty:
                return [self._row_to_obs(r) for r in sub.to_dict("records")]
        if not fetch_if_missing:
            return []
        target = FacilityTarget(facility_id, facility_name, lat, lon)
        days = days or [date(year, m, d) for m in range(1, 13) for d in (5, 15, 25)]
        obs: List[SatelliteObservation] = []
        bbox = (lon - 0.5, lat - 0.5, lon + 0.5, lat + 0.5)
        for day in days:
            try:
                for gr in self.search_granules(bbox, day, day):
                    obs.extend(self.extract_granule(gr, [target]))
            except Exception as exc:  # network errors are reported, never replaced by fake data
                logger.warning("Sentinel-5P fetch failed for %s on %s: %s", facility_name, day, exc)
        return obs

    @staticmethod
    def _row_to_obs(r: Dict[str, Any]) -> SatelliteObservation:
        names = SatelliteObservation.__dataclass_fields__.keys()
        return SatelliteObservation(**{k: r[k] for k in names if k in r})

    @staticmethod
    def observations_to_frame(obs: List[SatelliteObservation]) -> pd.DataFrame:
        return pd.DataFrame([asdict(o) for o in obs])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = CopernicusSentinel5PClient()
    # Real on-demand test: CEMEX Rüdersdorf (E-PRTR coordinate), three days in June 2023
    obs = client.get_facility_observations(
        facility_id="https://registry.gdi-de.org/id/de.bb.inspire.pf.eureg/23020947",
        facility_name="CEMEX Zement GmbH",
        lat=52.48907,
        lon=13.83693,
        year=2023,
        fetch_if_missing=True,
        days=[date(2023, 6, 2), date(2023, 6, 3), date(2023, 6, 4)],
    )
    for o in obs:
        print(o.observation_time_utc, o.granule_id, f"near={o.tropospheric_column_density_mol_m2:.3e}",
              f"bg={o.regional_background_mol_m2:.3e}", f"valid={o.is_valid_qa}", f"n={o.n_near_pixels_valid}/{o.n_near_pixels_total}")
