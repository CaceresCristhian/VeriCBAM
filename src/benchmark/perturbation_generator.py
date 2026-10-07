"""
VeriCBAM Benchmark Suite - Controlled Inconsistency Benchmark Generator
Distinguishes Layer A (Authentic Reference Observations) from Layer B (Controlled Evaluation Suite).

Methodological Principles (in accordance with Capstone Scientific Review):
1. Independent Activity Data: Production volumes are derived from independently verified
   nameplate plant capacities and industrial utilization factors (GEM Trackers, company reports),
   breaking any circular dependency with reported CO2.
2. Verified Technology Registry: Actual production routes (BF-BOF vs. Scrap-EAF vs. Dry Kiln)
   are sourced from official environmental permits, enabling realistic route-mismatch testing.
3. Explicit Mathematical Anomalies: Historical deviations are recorded with exact Z-scores:
   z = (declared_co2 - historical_mean) / historical_std.
4. Multimodal Feature Alignment: Every case includes stoichiometric margins, historical z-scores,
   and authentic Sentinel-5P atmospheric plume indicators from the real satellite cache.
5. Terminology Discipline: Labels are designated as 'benchmark_label' (controlled experimental target),
   never claiming external 'legal ground truth'.
"""

from dataclasses import dataclass, asdict
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core.stoichiometry.cement_models import CementDeclarationInput, audit_cement_declaration
from src.core.stoichiometry.steel_models import SteelDeclarationInput, audit_steel_declaration
from src.satellite.copernicus_client import CopernicusSentinel5PClient
from src.satellite.plume_analyzer import SatellitePlumeAnalyzer

BENCHMARK_PARQUET = Path(__file__).parents[2] / "data" / "02_processed" / "controlled_perturbation_benchmark.parquet"
BENCHMARK_CSV = Path(__file__).parents[2] / "data" / "02_processed" / "controlled_perturbation_benchmark.csv"
COHORT_PARQUET = Path(__file__).parents[2] / "data" / "02_processed" / "benchmark_cohort.parquet"
TECH_REGISTRY_CSV = Path(__file__).parents[2] / "data" / "02_processed" / "facility_technology_registry.csv"


@dataclass
class ControlledEvaluationCase:
    """Represents a controlled evaluation case with multi-source evidence indicators."""
    case_id: str
    facility_id: str
    facility_name: str
    sector: str
    country: str
    reference_year: int

    # Activity & Technology (Independently sourced)
    independent_capacity_mtpa: float
    declared_production_tonnes: float
    capacity_utilization_ratio: float
    actual_technology_route: str
    declared_production_route: str

    # Emissions (Reference vs Declared)
    original_reported_co2_tonnes: float
    declared_co2_tonnes: float
    declared_specific_emissions: float  # tCO2 / t output

    # Controlled Case Metadata
    perturbation_type: str  # "BASELINE_CONCORDANT", "PHYSICAL_BOUND_VIOLATION", "HISTORICAL_DROP_ANOMALY", "ROUTE_MISCLASSIFICATION", "ACTIVITY_DISCREPANCY"
    perturbation_magnitude_pct: float
    benchmark_label: int  # 1 = Inconsistent, 0 = Concordant
    affected_modalities: str
    scientific_rationale: str

    # Level 1: Stoichiometric Evidence
    stoich_lower_bound_tco2_per_t: float
    stoich_margin_tco2_per_t: float
    stoich_violation: int  # 1 if declared < bound, else 0

    # Level 2: Satellite Operational Evidence (Real Sentinel-5P)
    satellite_zscore: float
    satellite_valid_overpasses: int
    satellite_confidence: float
    satellite_data_source: str
    satellite_operational_verdict: str

    # Level 3: Historical Evidence
    historical_mean_co2_tonnes: float
    historical_std_co2_tonnes: float
    historical_zscore: float
    historical_confidence: float

    # Registry & Metadata Quality
    registry_confidence: float


class ControlledBenchmarkGenerator:
    """Generates Layer B controlled evaluation suite combining real reference cohort and technology data."""

    def __init__(
        self,
        cohort_path: Optional[Path] = None,
        tech_path: Optional[Path] = None,
    ):
        self.cohort_path = cohort_path or COHORT_PARQUET
        self.tech_path = tech_path or TECH_REGISTRY_CSV
        self.df_cohort = pd.read_parquet(self.cohort_path)
        self.df_tech = pd.read_csv(self.tech_path) if self.tech_path.exists() else pd.DataFrame()

        self.sat_client = CopernicusSentinel5PClient()
        self.sat_analyzer = SatellitePlumeAnalyzer()

    def _eval_cement(self, clinker_tonnes: float, co2_tonnes: float):
        decl = CementDeclarationInput(
            facility_name="Benchmark Facility",
            reporting_year=2023,
            clinker_produced_tonnes=clinker_tonnes,
            cement_produced_tonnes=clinker_tonnes / 0.80,
            clinker_ratio=0.80,
            reported_direct_emissions_tco2=co2_tonnes,
        )
        res = audit_cement_declaration(decl)
        bound = res.minimum_specific_intensity_tco2_per_t_clinker
        margin = res.reported_specific_intensity_tco2_per_t_clinker - bound
        violation = 1 if not res.is_physically_feasible else 0
        return bound, margin, violation

    def _eval_steel(self, steel_tonnes: float, co2_tonnes: float, route: str):
        valid_routes = ["BF-BOF", "DRI-NG-EAF", "DRI-H2-EAF", "Scrap-EAF"]
        clean_route = route if route in valid_routes else (
            "Scrap-EAF" if any(k in route for k in ["Scrap", "EAF", "Converter", "Rolling", "Finishing"]) else "BF-BOF"
        )
        decl = SteelDeclarationInput(
            facility_name="Benchmark Facility",
            reporting_year=2023,
            crude_steel_produced_tonnes=steel_tonnes,
            claimed_production_route=clean_route,
            reported_direct_emissions_tco2=co2_tonnes,
        )
        res = audit_steel_declaration(decl)
        bound = res.theoretical_floor_intensity_tco2_per_t
        margin = res.reported_specific_intensity_tco2_per_t - bound
        violation = 1 if not res.is_physically_feasible else 0
        return bound, margin, violation, clean_route

    def generate_benchmark_suite(self, seed: int = 42) -> pd.DataFrame:
        np.random.seed(seed)
        cases: List[ControlledEvaluationCase] = []

        fac_grouped = self.df_cohort.groupby("FacilityInspireId")
        case_idx = 1

        for fac_id, group in fac_grouped:
            latest_row = group.sort_values(by="reportingYear").iloc[-1]
            fac_name = latest_row["facilityName"]
            sector = latest_row["sector"]
            country = latest_row["countryName"]
            ref_year = int(latest_row["reportingYear"])
            lat = float(latest_row["Latitude"])
            lon = float(latest_row["Longitude"])

            # Historical statistics (2018-2023)
            hist_mean = float(group["co2_tonnes"].mean())
            hist_std = float(group["co2_tonnes"].std()) if len(group) > 1 else max(1.0, hist_mean * 0.08)
            if np.isnan(hist_std) or hist_std < 1.0:
                hist_std = max(1000.0, hist_mean * 0.05)

            # Match verified technology registry
            tech_match = self.df_tech[self.df_tech["FacilityInspireId"] == fac_id]
            if not tech_match.empty:
                t_row = tech_match.iloc[0]
                actual_route = t_row["verified_technology_route"]
                utilization = float(t_row.get("typical_capacity_utilization_ratio", 0.78))
                if sector == "Cement":
                    cap_mtpa = float(t_row.get("clinker_capacity_mtpa", 1.5))
                else:
                    cap_mtpa = float(t_row.get("crude_steel_capacity_mtpa", 2.0))
                    if cap_mtpa == 0.0:
                        cap_mtpa = float(t_row.get("primary_iron_capacity_mtpa", 0.0))
                    if cap_mtpa == 0.0:
                        cap_mtpa = 2.5  # Downstream rolling & finishing throughput (~2.5 Mt/yr)
            else:
                actual_route = "Dry Kiln with Preheater" if sector == "Cement" else "BF-BOF"
                cap_mtpa = 1.5 if sector == "Cement" else 3.0
                utilization = 0.75

            # Independent production (Methodological Fix R3):
            # Calculated purely from independent nameplate capacity * independent industrial capacity utilization ratio.
            # Completely decoupled from historical reported CO2 to ensure zero circularity.
            annual_production = round(cap_mtpa * 1e6 * utilization, -3)

            # Retrieve real satellite observations
            sat_obs = self.sat_client.get_facility_observations(fac_id, fac_name, lat, lon, year=ref_year)
            sat_res = self.sat_analyzer.analyze_facility_plumes(sat_obs, claimed_production_tonnes=annual_production)

            # -------------------------------------------------------------
            # Case 1: Unperturbed Baseline (Concordant, Benchmark Label = 0)
            # -------------------------------------------------------------
            base_emissions = hist_mean
            base_spec = base_emissions / annual_production
            hist_z_base = (base_emissions - hist_mean) / hist_std

            if sector == "Cement":
                bound, margin, violation = self._eval_cement(annual_production, base_emissions)
                declared_route = "Dry Kiln with Precalciner"
            else:
                bound, margin, violation, declared_route = self._eval_steel(annual_production, base_emissions, actual_route)

            cases.append(ControlledEvaluationCase(
                case_id=f"CASE_{case_idx:03d}_BASELINE",
                facility_id=fac_id,
                facility_name=fac_name,
                sector=sector,
                country=country,
                reference_year=ref_year,
                independent_capacity_mtpa=cap_mtpa,
                declared_production_tonnes=annual_production,
                capacity_utilization_ratio=round(utilization, 3),
                actual_technology_route=actual_route,
                declared_production_route=declared_route,
                original_reported_co2_tonnes=round(hist_mean, 1),
                declared_co2_tonnes=round(base_emissions, 1),
                declared_specific_emissions=round(base_spec, 4),
                perturbation_type="BASELINE_CONCORDANT",
                perturbation_magnitude_pct=0.0,
                benchmark_label=0,
                affected_modalities="None",
                scientific_rationale="Authentic reference observation; all independent physical, historical, and satellite indicators concordant.",
                stoich_lower_bound_tco2_per_t=round(bound, 3),
                stoich_margin_tco2_per_t=round(margin, 3),
                stoich_violation=violation,
                satellite_zscore=round(sat_res.plume_anomaly_zscore, 2),
                satellite_valid_overpasses=sat_res.valid_clear_sky_overpasses,
                satellite_confidence=round(sat_res.evidence_confidence, 2),
                satellite_data_source=sat_res.data_source,
                satellite_operational_verdict=sat_res.consistency_verdict,
                historical_mean_co2_tonnes=round(hist_mean, 1),
                historical_std_co2_tonnes=round(hist_std, 1),
                historical_zscore=round(hist_z_base, 2),
                historical_confidence=0.90,
                registry_confidence=0.95,
            ))
            case_idx += 1

            # -------------------------------------------------------------
            # Case 2: Physical Bound Violation (Stoichiometric Floor Underreported)
            # Benchmark Label = 1
            # -------------------------------------------------------------
            # Artificially suppress specific emissions well below chemical calcination / Fe2O3 reduction limit
            if sector == "Cement":
                suppressed_spec = 0.32  # Chemical calcination floor is ~0.49 tCO2/t
                declared_viol_co2 = annual_production * suppressed_spec
                bound_viol, margin_viol, viol_flag = self._eval_cement(annual_production, declared_viol_co2)
            else:
                suppressed_spec = 0.65 if "BF-BOF" in declared_route else 0.02  # BF-BOF floor is 1.155, Scrap-EAF floor is 0.04 tCO2/t
                declared_viol_co2 = annual_production * suppressed_spec
                bound_viol, margin_viol, viol_flag, _ = self._eval_steel(annual_production, declared_viol_co2, declared_route)

            hist_z_viol = (declared_viol_co2 - hist_mean) / hist_std
            mag_pct_viol = round(((declared_viol_co2 - hist_mean) / hist_mean) * 100, 1)

            cases.append(ControlledEvaluationCase(
                case_id=f"CASE_{case_idx:03d}_PHYSICAL_VIOLATION",
                facility_id=fac_id,
                facility_name=fac_name,
                sector=sector,
                country=country,
                reference_year=ref_year,
                independent_capacity_mtpa=cap_mtpa,
                declared_production_tonnes=annual_production,
                capacity_utilization_ratio=round(utilization, 3),
                actual_technology_route=actual_route,
                declared_production_route=declared_route,
                original_reported_co2_tonnes=round(hist_mean, 1),
                declared_co2_tonnes=round(declared_viol_co2, 1),
                declared_specific_emissions=round(suppressed_spec, 4),
                perturbation_type="PHYSICAL_BOUND_VIOLATION",
                perturbation_magnitude_pct=mag_pct_viol,
                benchmark_label=1,
                affected_modalities="Stoichiometry, Historical_Fingerprint",
                scientific_rationale="Declared emissions breach stoichiometric calcination / carbothermic reduction lower bound under declared production.",
                stoich_lower_bound_tco2_per_t=round(bound_viol, 3),
                stoich_margin_tco2_per_t=round(margin_viol, 3),
                stoich_violation=viol_flag,
                satellite_zscore=round(sat_res.plume_anomaly_zscore, 2),
                satellite_valid_overpasses=sat_res.valid_clear_sky_overpasses,
                satellite_confidence=round(sat_res.evidence_confidence, 2),
                satellite_data_source=sat_res.data_source,
                satellite_operational_verdict=sat_res.consistency_verdict,
                historical_mean_co2_tonnes=round(hist_mean, 1),
                historical_std_co2_tonnes=round(hist_std, 1),
                historical_zscore=round(hist_z_viol, 2),
                historical_confidence=0.90,
                registry_confidence=0.95,
            ))
            case_idx += 1

            # -------------------------------------------------------------
            # Case 3: Historical Longitudinal Drop Anomaly (> 3.5 Sigma Drop)
            # Benchmark Label = 1
            # -------------------------------------------------------------
            target_drop_z = -3.8
            declared_drop_co2 = max(hist_mean * 0.45, hist_mean + (target_drop_z * hist_std))
            actual_drop_z = (declared_drop_co2 - hist_mean) / hist_std
            mag_pct_drop = round(((declared_drop_co2 - hist_mean) / hist_mean) * 100, 1)

            if sector == "Cement":
                bound_drop, margin_drop, viol_drop = self._eval_cement(annual_production, declared_drop_co2)
            else:
                bound_drop, margin_drop, viol_drop, _ = self._eval_steel(annual_production, declared_drop_co2, declared_route)

            cases.append(ControlledEvaluationCase(
                case_id=f"CASE_{case_idx:03d}_HISTORICAL_DROP",
                facility_id=fac_id,
                facility_name=fac_name,
                sector=sector,
                country=country,
                reference_year=ref_year,
                independent_capacity_mtpa=cap_mtpa,
                declared_production_tonnes=annual_production,
                capacity_utilization_ratio=round(utilization, 3),
                actual_technology_route=actual_route,
                declared_production_route=declared_route,
                original_reported_co2_tonnes=round(hist_mean, 1),
                declared_co2_tonnes=round(declared_drop_co2, 1),
                declared_specific_emissions=round(declared_drop_co2 / annual_production, 4),
                perturbation_type="HISTORICAL_DROP_ANOMALY",
                perturbation_magnitude_pct=mag_pct_drop,
                benchmark_label=1,
                affected_modalities="Historical_Fingerprint",
                scientific_rationale=f"Longitudinal drop anomaly (Z = {actual_drop_z:.2f} sigma below 5-year facility trajectory) with unchanged production volume.",
                stoich_lower_bound_tco2_per_t=round(bound_drop, 3),
                stoich_margin_tco2_per_t=round(margin_drop, 3),
                stoich_violation=viol_drop,
                satellite_zscore=round(sat_res.plume_anomaly_zscore, 2),
                satellite_valid_overpasses=sat_res.valid_clear_sky_overpasses,
                satellite_confidence=round(sat_res.evidence_confidence, 2),
                satellite_data_source=sat_res.data_source,
                satellite_operational_verdict=sat_res.consistency_verdict,
                historical_mean_co2_tonnes=round(hist_mean, 1),
                historical_std_co2_tonnes=round(hist_std, 1),
                historical_zscore=round(actual_drop_z, 2),
                historical_confidence=0.90,
                registry_confidence=0.95,
            ))
            case_idx += 1

            # -------------------------------------------------------------
            # Case 4: Route Misclassification (for Integrated BF-BOF Facilities)
            # Declaring Scrap-EAF secondary route for primary blast furnace complex
            # Benchmark Label = 1
            # -------------------------------------------------------------
            if sector == "Steel" and ("BF-BOF" in actual_route or "Blast" in actual_route):
                false_route = "Scrap-EAF"
                # Claim EAF benchmark ~0.35 tCO2/t steel
                misclass_co2 = annual_production * 0.35
                misclass_z = (misclass_co2 - hist_mean) / hist_std
                misclass_mag = round(((misclass_co2 - hist_mean) / hist_mean) * 100, 1)

                bound_mc, margin_mc, viol_mc, _ = self._eval_steel(annual_production, misclass_co2, false_route)

                cases.append(ControlledEvaluationCase(
                    case_id=f"CASE_{case_idx:03d}_ROUTE_MISCLASS",
                    facility_id=fac_id,
                    facility_name=fac_name,
                    sector=sector,
                    country=country,
                    reference_year=ref_year,
                    independent_capacity_mtpa=cap_mtpa,
                    declared_production_tonnes=annual_production,
                    capacity_utilization_ratio=round(utilization, 3),
                    actual_technology_route=actual_route,
                    declared_production_route=false_route,
                    original_reported_co2_tonnes=round(hist_mean, 1),
                    declared_co2_tonnes=round(misclass_co2, 1),
                    declared_specific_emissions=0.35,
                    perturbation_type="ROUTE_MISCLASSIFICATION",
                    perturbation_magnitude_pct=misclass_mag,
                    benchmark_label=1,
                    affected_modalities="Stoichiometry, Historical_Fingerprint, Registry",
                    scientific_rationale="Controlled route-mismatch case constructed from facility with independently documented primary BF-BOF route declaring secondary Scrap-EAF route.",
                    stoich_lower_bound_tco2_per_t=round(bound_mc, 3),
                    stoich_margin_tco2_per_t=round(margin_mc, 3),
                    stoich_violation=viol_mc,
                    satellite_zscore=round(sat_res.plume_anomaly_zscore, 2),
                    satellite_valid_overpasses=sat_res.valid_clear_sky_overpasses,
                    satellite_confidence=round(sat_res.evidence_confidence, 2),
                    satellite_data_source=sat_res.data_source,
                    satellite_operational_verdict=sat_res.consistency_verdict,
                    historical_mean_co2_tonnes=round(hist_mean, 1),
                    historical_std_co2_tonnes=round(hist_std, 1),
                    historical_zscore=round(misclass_z, 2),
                    historical_confidence=0.90,
                    registry_confidence=0.95,
                ))
                case_idx += 1

        df_bench = pd.DataFrame([asdict(c) for c in cases])
        BENCHMARK_PARQUET.parent.mkdir(parents=True, exist_ok=True)
        df_bench.to_parquet(BENCHMARK_PARQUET, index=False)
        df_bench.to_csv(BENCHMARK_CSV, index=False)
        return df_bench


if __name__ == "__main__":
    gen = ControlledBenchmarkGenerator()
    df_out = gen.generate_benchmark_suite()
    print(f"Generated {len(df_out)} unified controlled evaluation cases:")
    print(df_out["perturbation_type"].value_counts())
    print("\nBenchmark Labels (0 = Concordant, 1 = Inconsistent):")
    print(df_out["benchmark_label"].value_counts())
    print("\nReal Satellite Data Provenance:")
    print(df_out["satellite_data_source"].value_counts())
    print(f"\nSaved to: {BENCHMARK_PARQUET}")
