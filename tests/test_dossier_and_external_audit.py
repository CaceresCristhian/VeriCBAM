"""
Unit & Integration Tests for Tab 1 Quick Audit:
- Automated 1-page PDF Pre-Audit Dossier generation (ReportLab)
- External third-country supplier screening using Stage 2 Multi-Sensor EO + Stoichiometry without prior EU registry history
"""

import io
import pypdf
from src.ui.dossier_pdf_generator import generate_dossier_pdf
from src.core.stoichiometry.steel_models import SteelDeclarationInput, audit_steel_declaration
from src.core.bayesian.evidence_fusion import ProbabilisticEvidenceFusionEngine, EvidenceInput


def test_pdf_dossier_generation_single_page_eu_plant():
    """Verifies that generate_dossier_pdf produces a valid, strictly 1-page PDF dossier."""
    audit_payload = {
        "facility_name": "Heidelberg Materials Burglengenfeld",
        "country": "Germany (DE)",
        "sector": "Cement",
        "route": "Dry-Process Rotary Kiln",
        "reporting_year": "2023",
        "risk_verdict": "CONSISTENT",
        "posterior_risk_pct": 6.4,
        "evidence_confidence_pct": 91.2,
        "audit_recommendation": "Expedited Desk Clearance",
        "declared_production_tonnes": 1250000.0,
        "declared_co2_tonnes": 950000.0,
        "declared_intensity": 0.760,
        "physical_floor_intensity": 0.651,
        "total_floor_co2": 813750.0,
        "is_physically_feasible": True,
        "physical_deficit_tco2": 0.0,
        "satellite_summary": "Landsat TIR +14.2°C | VIIRS 11/12 active months",
    }
    pdf_bytes = generate_dossier_pdf(audit_payload)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) == 1
    page_text = reader.pages[0].extract_text()
    assert "VeriCBAM Pre-Audit Consistency Screening Dossier" in page_text
    assert "Burglengenfeld" in page_text


def test_external_third_country_supplier_satellite_only_screening_and_dossier():
    """
    Tests Option B (External / Non-EU Supplier Screening without E-PRTR history):
    Simulates an overseas blast-furnace steel exporter declaring emissions below the BF-BOF floor (0.80 tCO2/t)
    while global satellite EO (Landsat 30m TIR +18.4°C, VIIRS 12/12 active months, VHR active rail yard)
    confirms continuous primary BF-BOF operations.
    """
    declared_prod = 2000000.0
    declared_co2 = 1600000.0  # 0.80 tCO2/t (below BF-BOF thermodynamic floor ~1.18 tCO2/t)

    decl = SteelDeclarationInput(
        facility_name="External Exporter — Iskenderun Integrated Works",
        reporting_year=2025,
        crude_steel_produced_tonnes=declared_prod,
        claimed_production_route="BF-BOF",
        reported_direct_emissions_tco2=declared_co2,
    )
    stoich_res = audit_steel_declaration(decl)
    assert not stoich_res.is_physically_feasible
    assert stoich_res.discrepancy_tco2 < 0.0

    engine = ProbabilisticEvidenceFusionEngine(prior_inconsistency_prob=0.15)
    ev = EvidenceInput(
        stoichiometric_discrepancy_sigma=-2.4,
        stoichiometric_violated=True,
        satellite_plume_anomaly_zscore=1.8,
        satellite_cloud_fraction=0.12,
        temporal_variance_zscore=None,
        years_reported_history=0,  # Third-country facility with zero E-PRTR history
        thermal_anomaly_zscore=3.1,
        thermal_operating_months_ratio=1.0,
        freight_logistics_zscore=2.5,
    )
    decision = engine.fuse_evidence(
        ev,
        reported_emissions_tco2=declared_co2,
        physical_min_tco2=stoich_res.total_physical_minimum_tco2,
    )
    assert decision.posterior_inconsistency_risk >= 0.90
    assert "High" in decision.audit_verdict

    pdf_bytes = generate_dossier_pdf({
        "facility_name": decl.facility_name,
        "country": "Non-EU Third Country (TR)",
        "sector": "Iron & Steel",
        "route": "Integrated BF-BOF",
        "reporting_year": "2025",
        "risk_verdict": decision.audit_verdict,
        "posterior_risk_pct": decision.posterior_inconsistency_risk * 100.0,
        "evidence_confidence_pct": decision.evidence_confidence_score * 100.0,
        "audit_recommendation": "Mandatory On-Site Physical Verification",
        "declared_production_tonnes": declared_prod,
        "declared_co2_tonnes": declared_co2,
        "declared_intensity": stoich_res.reported_specific_intensity_tco2_per_t,
        "physical_floor_intensity": stoich_res.theoretical_floor_intensity_tco2_per_t,
        "total_floor_co2": stoich_res.total_physical_minimum_tco2,
        "is_physically_feasible": stoich_res.is_physically_feasible,
        "physical_deficit_tco2": abs(stoich_res.discrepancy_tco2),
        "satellite_summary": "Landsat TIR +18.4°C | VIIRS 12/12 months (BF-BOF signature)",
    })
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) == 1
