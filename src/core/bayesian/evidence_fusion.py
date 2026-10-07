"""
VeriCBAM Probabilistic Evidence-Fusion Engine
Implements calibrated Bayesian log-odds synthesis combining deterministic physical constraints,
satellite-derived operational indicators, historical facility fingerprints, and registry data.

Mathematical Formulation:
    logit P(H | E) = logit P(H) + sum_i [ C_i * log(LR_i) ]
    P(H | E) = sigmoid( logit P(H) + sum_i [ C_i * log(LR_i) ] )

Where:
    H   = Material inconsistency in CBAM declaration
    E_i = Independent evidence stream i
    P(H)= Base prior probability (~8% historical ETS discrepancy baseline)
    LR_i= Likelihood ratio P(E_i | H) / P(E_i | not H)
    C_i = Observational reliability / confidence factor in [0, 1]

Separates Inconsistency Risk P(H | E) from Evidence Confidence C_overall.
Distinguishes four explicit categorical outcomes:
    1. Consistent
    2. Potential Inconsistency
    3. High Inconsistency Risk
    4. Insufficient Evidence
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


@dataclass
class EvidenceStream:
    """Individual evidence stream with explicit likelihood ratio and observational confidence."""
    source_name: str
    likelihood_ratio: float  # P(E | H) / P(E | not H)
    confidence_factor: float  # C_i in [0.0, 1.0] (reflects data quality, cloud cover, completeness)
    weight: float = 1.0
    diagnostic_note: str = ""


@dataclass
class EvidenceInput:
    """Raw multi-source observations to be converted into calibrated likelihood streams."""
    stoichiometric_discrepancy_sigma: float  # Distance from physical floor in std deviations
    stoichiometric_violated: bool           # True if strictly below thermodynamic floor
    satellite_plume_anomaly_zscore: Optional[float] = None  # Sentinel-5P NO2/CO activity proxy
    satellite_cloud_fraction: float = 0.0   # 0.0 to 1.0 (Sentinel-5P cloud radiance fraction)
    temporal_variance_zscore: Optional[float] = None  # Deviation from historical baseline
    years_reported_history: int = 5         # Number of historical reference years available
    nox_co2_anomaly_zscore: Optional[float] = None    # Internal multi-pollutant consistency (combustion ratio anomaly)
    registry_capacity_ratio: Optional[float] = None   # Declared volume vs known capacity
    route_mismatch_detected: bool = False   # True if declared route contradicts verified technology registry


@dataclass
class FusionAuditDecision:
    """Calibrated audit decision separating Inconsistency Risk from Evidence Confidence."""
    posterior_inconsistency_risk: float      # P(H | E) in [0.0, 1.0]
    evidence_confidence_score: float         # C_overall in [0.0, 1.0]
    uncertainty_interval_95: Tuple[float, float]  # 95% uncertainty interval [P_low, P_high]
    audit_verdict: str  # "Consistent", "Potential Inconsistency", "High Inconsistency Risk", "Insufficient Evidence"
    evidence_likelihood_ratios: Dict[str, float]
    evidence_confidence_factors: Dict[str, float]
    primary_driver: str
    counterfactual_delta_tco2: float         # Delta tCO2 needed to reach consistency threshold
    explanation_summary: str


class ProbabilisticEvidenceFusionEngine:
    """
    Synthesizes independent physical, operational, and historical evidence streams
    using a confidence-weighted Bayesian log-odds formulation.
    """

    def __init__(self, prior_inconsistency_prob: float = 0.08):
        self.prior = prior_inconsistency_prob
        self.prior_logit = float(np.log(self.prior / (1.0 - self.prior)))

    @staticmethod
    def _sigmoid(x: float) -> float:
        return float(1.0 / (1.0 + np.exp(-np.clip(x, -25.0, 25.0))))

    def build_evidence_streams(self, ev: EvidenceInput) -> List[EvidenceStream]:
        streams = []

        # 1. Stoichiometric Physics Evidence
        # If physically violated: deterministic floor breach
        if ev.stoichiometric_violated:
            lr_stoich = 1e6  # Deterministic overrule
            c_stoich = 1.0   # Chemistry is 100% reliable
            note = "Deterministic physical bound violation (mass balance floor breach)"
        elif ev.stoichiometric_discrepancy_sigma < 0.5:
            lr_stoich = 2.2  # Suspiciously tight margin
            c_stoich = 0.95
            note = "Near-zero thermodynamic margin (<0.5 sigma)"
        elif ev.stoichiometric_discrepancy_sigma < 1.0:
            lr_stoich = 1.3
            c_stoich = 0.95
            note = "Moderate thermodynamic margin (0.5 - 1.0 sigma)"
        else:
            lr_stoich = 0.45  # Substantial comfortable margin
            c_stoich = 0.95
            note = "Comfortable thermodynamic margin (>1.0 sigma)"
        streams.append(EvidenceStream("Stoichiometry", lr_stoich, c_stoich, weight=1.5, diagnostic_note=note))

        # 2. Copernicus Satellite Operational Activity Evidence
        if ev.satellite_plume_anomaly_zscore is not None:
            # Confidence decreases with cloud fraction: C_sat = max(0, 1 - cloud)
            c_sat = float(np.clip(1.0 - ev.satellite_cloud_fraction, 0.0, 1.0))
            z = ev.satellite_plume_anomaly_zscore

            # If satellite shows strong combustion plume (z > 2) while declared production claimed low, or vice versa
            if z > 2.5:
                lr_sat = 6.5
                note = f"Elevated combustion plume contrast (+{z:.2f} sigma)"
            elif z > 1.5:
                lr_sat = 2.8
                note = f"Moderate plume contrast (+{z:.2f} sigma)"
            elif z < -1.5:
                lr_sat = 0.4
                note = f"Sub-background stack signal ({z:.2f} sigma)"
            else:
                lr_sat = 1.0
                note = f"Plume signal concordant with background ({z:.2f} sigma)"
            streams.append(EvidenceStream("Satellite_Operational", lr_sat, c_sat, weight=1.0, diagnostic_note=note))
        else:
            # Satellite unobserved / completely missing
            streams.append(EvidenceStream("Satellite_Operational", 1.0, 0.0, weight=1.0, diagnostic_note="Satellite observation missing"))

        # 3. Longitudinal Historical Fingerprint Evidence
        if ev.temporal_variance_zscore is not None:
            # Confidence scales with length of historical reference records
            c_temp = float(np.clip(ev.years_reported_history / 5.0, 0.2, 1.0))
            tz = ev.temporal_variance_zscore
            if tz > 3.0:
                lr_temp = 5.2
                note = f"Abrupt uncharacteristic historical shift (+{tz:.2f} sigma)"
            elif tz > 2.0:
                lr_temp = 2.4
                note = f"Moderate historical deviation (+{tz:.2f} sigma)"
            elif tz < 0.5:
                lr_temp = 0.5
                note = f"Historical trajectory highly consistent ({tz:.2f} sigma)"
            else:
                lr_temp = 1.0
                note = f"Historical trajectory within normal variation ({tz:.2f} sigma)"
            streams.append(EvidenceStream("Historical_Fingerprint", lr_temp, c_temp, weight=1.0, diagnostic_note=note))
        else:
            streams.append(EvidenceStream("Historical_Fingerprint", 1.0, 0.0, weight=1.0, diagnostic_note="Historical records missing"))

        # 4. Multi-Pollutant NOx/CO2 Internal Combustion Ratio Evidence
        if ev.nox_co2_anomaly_zscore is not None:
            nz = ev.nox_co2_anomaly_zscore
            c_nox = 0.85
            if nz > 3.0:
                lr_nox = 5.5
                note = f"Severe multi-pollutant ratio anomaly (+{nz:.2f} sigma): reported NOx remains high despite declared CO2 drop"
            elif nz > 2.0:
                lr_nox = 2.8
                note = f"Moderate multi-pollutant ratio anomaly (+{nz:.2f} sigma)"
            elif nz < -2.0:
                lr_nox = 1.5
                note = f"Low NOx/CO2 ratio anomaly ({nz:.2f} sigma)"
            else:
                lr_nox = 0.6
                note = f"NOx/CO2 combustion ratio concordant with baseline ({nz:.2f} sigma)"
            streams.append(EvidenceStream("MultiPollutant_NOx_CO2", lr_nox, c_nox, weight=1.2, diagnostic_note=note))

        # 5. Registry Capacity Ratio Evidence
        if ev.registry_capacity_ratio is not None:
            c_reg = 0.85
            ratio = ev.registry_capacity_ratio
            if ratio > 1.20:
                lr_reg = 4.5
                note = f"Declared production exceeds known nameplate capacity by >20% (Ratio={ratio:.2f})"
            elif ratio > 1.10:
                lr_reg = 2.0
                note = f"Declared production slightly above nameplate capacity (Ratio={ratio:.2f})"
            elif ratio < 0.20:
                lr_reg = 1.8
                note = f"Low capacity utilization (<20%) (Ratio={ratio:.2f})"
            else:
                lr_reg = 0.7
                note = f"Capacity utilization realistic (Ratio={ratio:.2f})"
            streams.append(EvidenceStream("Registry_Capacity", lr_reg, c_reg, weight=0.8, diagnostic_note=note))

        # 5. Technology Route Verification Evidence
        if ev.route_mismatch_detected:
            lr_route = 22.0  # Decisive evidence of declared route misclassification (e.g. BF-BOF declaring Scrap-EAF)
            c_route = 0.95
            note = "Declared production route directly contradicts verified facility technology registry"
            streams.append(EvidenceStream("Technology_Route", lr_route, c_route, weight=2.0, diagnostic_note=note))

        return streams

    def fuse_evidence(
        self,
        ev: EvidenceInput,
        reported_emissions_tco2: float,
        physical_min_tco2: float,
        n_mc_samples: int = 500,
    ) -> FusionAuditDecision:
        """
        Executes the confidence-weighted Bayesian log-odds update with Monte Carlo uncertainty propagation.
        """
        streams = self.build_evidence_streams(ev)
        stoich_violation_flag = bool(ev.stoichiometric_violated)
        delta_stoich = max(0.0, physical_min_tco2 - reported_emissions_tco2) if stoich_violation_flag else 0.0

        # 2. Calculate overall observational confidence score
        total_weight = sum(s.weight for s in streams)
        c_overall = sum(s.confidence_factor * s.weight for s in streams) / total_weight if total_weight > 0 else 0.0

        # Check Insufficient Evidence Condition:
        # If overall observational confidence is critically low (<0.50) due to cloud obscuration and missing baselines
        # BUT physical stoichiometry violations are never dismissed as 'insufficient evidence'
        if c_overall < 0.50 and not stoich_violation_flag:
            return FusionAuditDecision(
                posterior_inconsistency_risk=round(self.prior, 4),
                evidence_confidence_score=round(c_overall, 3),
                uncertainty_interval_95=(round(max(0.0, self.prior - 0.05), 3), round(min(1.0, self.prior + 0.20), 3)),
                audit_verdict="Insufficient Evidence",
                evidence_likelihood_ratios={s.source_name: round(s.likelihood_ratio, 2) for s in streams},
                evidence_confidence_factors={s.source_name: round(s.confidence_factor, 2) for s in streams},
                primary_driver="Cloud Obscuration / Missing Multi-Year Observational Evidence",
                counterfactual_delta_tco2=0.0,
                explanation_summary=(
                    f"Insufficient observational evidence (Confidence = {c_overall*100:.1f}%). "
                    f"Persistent cloud cover or absent historical reference records preclude automated screening. "
                    f"Categorized as 'Insufficient Evidence' for human verifier triage."
                ),
            )

        # 3. Logit synthesis: logit P(H|E) = logit P(H) + sum [ w_i * C_i * log(LR_i) ]
        weighted_log_lr_sum = sum(s.weight * s.confidence_factor * np.log(max(1e-4, s.likelihood_ratio)) for s in streams)
        posterior_logit = self.prior_logit + weighted_log_lr_sum
        posterior_risk = self._sigmoid(posterior_logit)

        # 4. Monte Carlo Sensitivity Interval Propagation (under likelihood ratio parameter uncertainty)
        rng = np.random.default_rng(42)
        mc_risks = []
        for _ in range(n_mc_samples):
            mc_sum = 0.0
            for s in streams:
                # Perturb log(LR) with noise proportional to (1 - confidence)
                noise_scale = max(0.05, (1.0 - s.confidence_factor) * 0.4)
                perturbed_log_lr = rng.normal(np.log(max(1e-4, s.likelihood_ratio)), noise_scale)
                mc_sum += s.weight * s.confidence_factor * perturbed_log_lr
            mc_logit = self.prior_logit + mc_sum
            mc_risks.append(self._sigmoid(mc_logit))

        ui_low = float(np.percentile(mc_risks, 2.5))
        ui_high = float(np.percentile(mc_risks, 97.5))

        # 5. Verdict Categorization
        if stoich_violation_flag:
            verdict = "High Inconsistency Risk"
            counterfactual = delta_stoich
        elif posterior_risk >= 0.70:
            verdict = "High Inconsistency Risk"
            counterfactual = max(0.0, physical_min_tco2 * 1.10 - reported_emissions_tco2)
        elif posterior_risk >= 0.25:
            verdict = "Potential Inconsistency"
            counterfactual = max(0.0, physical_min_tco2 * 1.05 - reported_emissions_tco2)
        else:
            verdict = "Consistent"
            counterfactual = 0.0

        # Find primary driver
        drivers = {s.source_name: s.likelihood_ratio for s in streams if s.confidence_factor >= 0.4}
        primary_driver_name = max(drivers, key=drivers.get) if drivers else "Baseline Prior"

        explanation = (
            f"Posterior inconsistency risk is {posterior_risk*100:.1f}% with evidence confidence of {c_overall*100:.1f}%. "
            f"95% uncertainty interval: [{ui_low*100:.1f}%, {ui_high*100:.1f}%]. "
            f"Primary contributing evidence channel: {primary_driver_name}."
        )

        return FusionAuditDecision(
            posterior_inconsistency_risk=round(posterior_risk, 4),
            evidence_confidence_score=round(c_overall, 3),
            uncertainty_interval_95=(round(ui_low, 3), round(ui_high, 3)),
            audit_verdict=verdict,
            evidence_likelihood_ratios={s.source_name: round(s.likelihood_ratio, 2) for s in streams},
            evidence_confidence_factors={s.source_name: round(s.confidence_factor, 2) for s in streams},
            primary_driver=primary_driver_name,
            counterfactual_delta_tco2=round(counterfactual, 1),
            explanation_summary=explanation,
        )

    def evaluate_prior_sensitivity(
        self,
        ev: EvidenceInput,
        reported_emissions_tco2: float,
        physical_min_tco2: float,
        candidate_priors: Optional[List[float]] = None,
    ) -> Dict[float, float]:
        """
        Evaluates the sensitivity of posterior inconsistency risk across different base priors P(H).
        Demonstrates ranking stability under varying prior assumptions (e.g., 2%, 5%, 8%, 15%).
        """
        priors = candidate_priors or [0.02, 0.05, 0.08, 0.12, 0.15]
        results = {}
        for p in priors:
            eng = ProbabilisticEvidenceFusionEngine(prior_inconsistency_prob=p)
            dec = eng.fuse_evidence(ev, reported_emissions_tco2, physical_min_tco2, n_mc_samples=50)
            results[p] = round(dec.posterior_inconsistency_risk, 4)
        return results


if __name__ == "__main__":
    engine = ProbabilisticEvidenceFusionEngine()

    # Scenario 1: Concordant plant with high confidence
    ev1 = EvidenceInput(
        stoichiometric_discrepancy_sigma=2.5,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=0.8,
        satellite_cloud_fraction=0.15,
        temporal_variance_zscore=0.3,
        years_reported_history=6,
    )
    d1 = engine.fuse_evidence(ev1, 800000, 650000)
    print("Scenario 1 (Concordant):")
    print(f" - Verdict: {d1.audit_verdict}")
    print(f" - Risk P(H|E): {d1.posterior_inconsistency_risk:.3f}")
    print(f" - Confidence: {d1.evidence_confidence_score:.3f}")
    print(f" - 95% UI: {d1.uncertainty_interval_95}")

    # Scenario 2: High satellite anomaly + moderate historical deviation
    ev2 = EvidenceInput(
        stoichiometric_discrepancy_sigma=0.7,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=3.1,
        satellite_cloud_fraction=0.20,
        temporal_variance_zscore=2.8,
        years_reported_history=6,
    )
    d2 = engine.fuse_evidence(ev2, 700000, 650000)
    print("\nScenario 2 (High Risk Anomaly):")
    print(f" - Verdict: {d2.audit_verdict}")
    print(f" - Risk P(H|E): {d2.posterior_inconsistency_risk:.3f}")
    print(f" - Confidence: {d2.evidence_confidence_score:.3f}")
    print(f" - 95% UI: {d2.uncertainty_interval_95}")

    # Scenario 3: Cloud obscured (Cloud fraction = 0.85) -> Insufficient Evidence
    ev3 = EvidenceInput(
        stoichiometric_discrepancy_sigma=1.5,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=None,
        satellite_cloud_fraction=0.85,
        temporal_variance_zscore=None,
        years_reported_history=1,
    )
    d3 = engine.fuse_evidence(ev3, 750000, 650000)
    print("\nScenario 3 (Cloud Obscured):")
    print(f" - Verdict: {d3.audit_verdict}")
    print(f" - Risk P(H|E): {d3.posterior_inconsistency_risk:.3f}")
    print(f" - Confidence: {d3.evidence_confidence_score:.3f}")
