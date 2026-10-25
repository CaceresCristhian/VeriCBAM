"""
Unit tests for Probabilistic Evidence Fusion Engine.
"""
import pytest
from src.core.bayesian.evidence_fusion import (
    ProbabilisticEvidenceFusionEngine,
    EvidenceInput,
    EvidenceStream,
)


def test_fusion_concordant_low_risk():
    """Concordant evidence across all streams should produce low posterior inconsistency risk."""
    engine = ProbabilisticEvidenceFusionEngine(prior_inconsistency_prob=0.08)
    ev = EvidenceInput(
        stoichiometric_discrepancy_sigma=2.5,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=0.5,
        satellite_cloud_fraction=0.10,
        temporal_variance_zscore=0.2,
        years_reported_history=6,
        registry_capacity_ratio=0.85,
    )
    decision = engine.fuse_evidence(ev, reported_emissions_tco2=850000, physical_min_tco2=700000)
    assert decision.audit_verdict == "Consistent"
    assert decision.posterior_inconsistency_risk < 0.10
    assert decision.evidence_confidence_score > 0.85


def test_fusion_physical_violation_overrule():
    """Physical mass balance floor breach must result in high inconsistency risk."""
    engine = ProbabilisticEvidenceFusionEngine()
    ev = EvidenceInput(
        stoichiometric_discrepancy_sigma=-2.0,
        stoichiometric_violated=True,
    )
    decision = engine.fuse_evidence(ev, reported_emissions_tco2=400000, physical_min_tco2=700000)
    assert decision.audit_verdict == "High Inconsistency Risk"
    assert decision.posterior_inconsistency_risk >= 0.99
    assert decision.counterfactual_delta_tco2 == 300000.0


def test_fusion_insufficient_evidence():
    """Low observational confidence due to cloud cover must result in Insufficient Evidence."""
    engine = ProbabilisticEvidenceFusionEngine()
    ev = EvidenceInput(
        stoichiometric_discrepancy_sigma=1.2,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=None,
        satellite_cloud_fraction=1.0,
        temporal_variance_zscore=None,
        years_reported_history=0,
    )
    decision = engine.fuse_evidence(ev, reported_emissions_tco2=800000, physical_min_tco2=700000)
    assert decision.audit_verdict == "Insufficient Evidence"
    assert decision.evidence_confidence_score < 0.50


def test_prior_sensitivity_monotonicity():
    """Posterior risk should increase monotonically with higher prior probability assumptions."""
    engine = ProbabilisticEvidenceFusionEngine()
    ev = EvidenceInput(
        stoichiometric_discrepancy_sigma=0.6,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=2.2,
        satellite_cloud_fraction=0.15,
        temporal_variance_zscore=2.5,
        years_reported_history=5,
    )
    sens = engine.evaluate_prior_sensitivity(ev, 750000, 700000, candidate_priors=[0.02, 0.05, 0.08, 0.15])
    assert sens[0.02] < sens[0.05] < sens[0.08] < sens[0.15]


def test_stage2_multisensor_thermal_and_freight_fusion():
    """Stage 2 thermal infrared (Landsat/VIIRS) and freight logistics (Planet/VHR) streams should elevate posterior risk."""
    engine = ProbabilisticEvidenceFusionEngine(prior_inconsistency_prob=0.08)
    ev_base = EvidenceInput(
        stoichiometric_discrepancy_sigma=0.8,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=1.0,
        satellite_cloud_fraction=0.15,
        temporal_variance_zscore=1.2,
        years_reported_history=5,
    )
    ev_stage2 = EvidenceInput(
        stoichiometric_discrepancy_sigma=0.8,
        stoichiometric_violated=False,
        satellite_plume_anomaly_zscore=1.0,
        satellite_cloud_fraction=0.15,
        temporal_variance_zscore=1.2,
        years_reported_history=5,
        thermal_anomaly_zscore=2.8,
        thermal_operating_months_ratio=1.0,
        freight_logistics_zscore=2.3,
    )
    dec_base = engine.fuse_evidence(ev_base, reported_emissions_tco2=720000, physical_min_tco2=680000)
    dec_stage2 = engine.fuse_evidence(ev_stage2, reported_emissions_tco2=720000, physical_min_tco2=680000)

    assert "Thermal_Infrared_Kiln" in dec_stage2.evidence_likelihood_ratios
    assert "Optical_Freight_Logistics" in dec_stage2.evidence_likelihood_ratios
    assert dec_stage2.posterior_inconsistency_risk > dec_base.posterior_inconsistency_risk
    assert dec_stage2.evidence_likelihood_ratios["Thermal_Infrared_Kiln"] >= 4.0
    assert dec_stage2.evidence_likelihood_ratios["Optical_Freight_Logistics"] >= 3.0

