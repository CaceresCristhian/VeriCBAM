"""
VeriCBAM Satellite Engine - Plume Contrast & Anomaly Analyzer
Computes spatial plume contrast Z-scores, cloud-radiance filtering, and operational consistency
between self-reported declaration production and Copernicus Sentinel-5P tropospheric gas enhancements.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np
from .copernicus_client import SatelliteObservation


@dataclass
class PlumeAnalysisResult:
    """Summary of remote sensing atmospheric plume analysis over a facility."""
    facility_id: str
    facility_name: str
    reporting_year: int
    total_overpasses: int
    valid_clear_sky_overpasses: int
    mean_cloud_fraction: float
    mean_facility_column_mol_m2: float
    mean_background_column_mol_m2: float
    plume_enhancement_delta_mol_m2: float
    plume_anomaly_zscore: float
    is_insufficient_evidence: bool  # True if too few clear-sky overpasses
    operational_state_inference: str  # "Active Combustion Plume", "Low Activity / Idle", "Indeterminate (Cloud Obscured)"
    consistency_verdict: str
    verdict_explanation: str
    data_source: str = "real_sentinel5p"
    evidence_confidence: float = 0.85


class SatellitePlumeAnalyzer:
    """
    Analyzes Sentinel-5P atmospheric observations to evaluate combustion operational state.
    """

    def __init__(self, min_valid_overpasses: int = 2, cloud_cutoff: float = 0.60):
        self.min_valid_overpasses = min_valid_overpasses
        self.cloud_cutoff = cloud_cutoff

    def analyze_facility_plumes(
        self,
        observations: List[SatelliteObservation],
        claimed_production_tonnes: float,
        claimed_operating_hours: Optional[float] = None,
    ) -> PlumeAnalysisResult:
        if not observations:
            return PlumeAnalysisResult(
                facility_id="UNKNOWN",
                facility_name="UNKNOWN",
                reporting_year=2023,
                total_overpasses=0,
                valid_clear_sky_overpasses=0,
                mean_cloud_fraction=1.0,
                mean_facility_column_mol_m2=0.0,
                mean_background_column_mol_m2=0.0,
                plume_enhancement_delta_mol_m2=0.0,
                plume_anomaly_zscore=0.0,
                is_insufficient_evidence=True,
                operational_state_inference="Indeterminate (No Real Data)",
                consistency_verdict="INSUFFICIENT_EVIDENCE",
                verdict_explanation="No real Sentinel-5P observations available for this facility coordinate in the local repository cache.",
                data_source="no_data",
                evidence_confidence=0.0,
            )

        fac_id = observations[0].facility_id
        fac_name = observations[0].facility_name
        year = int(observations[0].observation_date.split("-")[0])
        data_source = getattr(observations[0], "data_source", "real_sentinel5p")

        # Filter valid clear-sky observations passing official QA
        valid_obs = [
            o for o in observations
            if o.is_valid_qa and not np.isnan(o.tropospheric_column_density_mol_m2) and not np.isnan(o.regional_background_mol_m2)
        ]
        cloud_vals = [o.cloud_fraction for o in observations if not np.isnan(o.cloud_fraction)]
        mean_cloud = float(np.mean(cloud_vals)) if cloud_vals else 1.0

        # Check Insufficient Evidence condition (persistent cloud cover / missing data)
        if len(valid_obs) < self.min_valid_overpasses:
            return PlumeAnalysisResult(
                facility_id=fac_id,
                facility_name=fac_name,
                reporting_year=year,
                total_overpasses=len(observations),
                valid_clear_sky_overpasses=len(valid_obs),
                mean_cloud_fraction=round(mean_cloud, 3),
                mean_facility_column_mol_m2=0.0,
                mean_background_column_mol_m2=0.0,
                plume_enhancement_delta_mol_m2=0.0,
                plume_anomaly_zscore=0.0,
                is_insufficient_evidence=True,
                operational_state_inference="Indeterminate (Cloud Obscured / Insufficient Overpasses)",
                consistency_verdict="INSUFFICIENT_EVIDENCE",
                verdict_explanation=(
                    f"Insufficient clear-sky Sentinel-5P observations ({len(valid_obs)} valid overpasses, minimum {self.min_valid_overpasses} required). "
                    f"Persistent cloud obscuration or low QA precludes reliable operational inference."
                ),
                data_source=data_source,
                evidence_confidence=round(len(valid_obs) / max(1, self.min_valid_overpasses * 2), 2),
            )

        # Compute plume statistics
        fac_columns = [o.tropospheric_column_density_mol_m2 for o in valid_obs]
        bg_columns = [o.regional_background_mol_m2 for o in valid_obs]
        bg_stds = [o.background_std_mol_m2 for o in valid_obs if not np.isnan(o.background_std_mol_m2)]

        mean_fac = float(np.mean(fac_columns))
        mean_bg = float(np.mean(bg_columns))
        mean_std = float(np.mean(bg_stds)) if np.mean(bg_stds) > 0 else 1.0e-5

        enhancement = mean_fac - mean_bg
        # Standardized contrast Z-score relative to regional background variability
        z_score = enhancement / mean_std

        # Infer operational state
        if z_score >= 1.5:
            op_state = "Active Combustion Plume (High Continuous Operations)"
        elif z_score >= 0.5:
            op_state = "Moderate Combustion Activity"
        else:
            op_state = "Low Activity / Idle Furnace State"

        # Check consistency with claimed production
        # Example: Declaring 0 or near-zero production while Z-score >= 2.5
        if claimed_production_tonnes <= 50000 and z_score >= 2.0:
            verdict = "ANOMALY_HIGH_ACTIVITY_REPORTED_IDLE"
            explanation = (
                f"Satellite observation anomaly: Declared low production ({claimed_production_tonnes:,.0f} tonnes), "
                f"but Sentinel-5P detected strong combustion plume enhancement (Z = +{z_score:.2f}, {enhancement*1e5:.2f} µmol/m² above background). "
                f"Indicates active undeclared operations or misreported facility activity."
            )
        elif claimed_production_tonnes > 500000 and z_score < 0.2:
            verdict = "ANOMALY_LOW_ACTIVITY_REPORTED_FULL"
            explanation = (
                f"Satellite observation anomaly: Declared high-volume industrial operations ({claimed_production_tonnes:,.0f} tonnes), "
                f"yet Sentinel-5P plume enhancement is negligible (Z = {z_score:.2f} relative to background). "
                f"Suggests potential production route misclassification or off-site sourcing."
            )
        else:
            verdict = "SATELLITE_CONCORDANT"
            explanation = (
                f"Sentinel-5P atmospheric observations are concordant with declared operational state. "
                f"Observed plume enhancement Z-score: +{z_score:.2f} across {len(valid_obs)} cloud-free overpasses."
            )

        return PlumeAnalysisResult(
            facility_id=fac_id,
            facility_name=fac_name,
            reporting_year=year,
            total_overpasses=len(observations),
            valid_clear_sky_overpasses=len(valid_obs),
            mean_cloud_fraction=round(mean_cloud, 3),
            mean_facility_column_mol_m2=round(mean_fac, 8),
            mean_background_column_mol_m2=round(mean_bg, 8),
            plume_enhancement_delta_mol_m2=round(enhancement, 8),
            plume_anomaly_zscore=round(z_score, 2),
            is_insufficient_evidence=False,
            operational_state_inference=op_state,
            consistency_verdict=verdict,
            verdict_explanation=explanation,
            data_source=data_source,
            evidence_confidence=round(min(1.0, 0.5 + (len(valid_obs) / 10.0)), 2),
        )


if __name__ == "__main__":
    from .copernicus_client import CopernicusSentinel5PClient
    client = CopernicusSentinel5PClient()
    analyzer = SatellitePlumeAnalyzer()

    # Test 1: Real active plant
    obs_active = client.get_facility_observations("DE.EEA/110000000.FACILITY", "CEMEX Rüdersdorf", 52.4891, 13.8369, 2023)
    res_active = analyzer.analyze_facility_plumes(obs_active, claimed_production_tonnes=1000000.0)
    print("Test 1: Active Plant Analysis:")
    print(f" - State: {res_active.operational_state_inference}")
    print(f" - Z-Score: {res_active.plume_anomaly_zscore}")
    print(f" - Verdict: {res_active.consistency_verdict}")
    print(f" - Explanation: {res_active.verdict_explanation}")
