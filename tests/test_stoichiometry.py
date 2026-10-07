"""
Unit tests for deterministic stoichiometric engines (Cement & Steel).
"""
import pytest
from src.core.stoichiometry.cement_models import (
    CementDeclarationInput,
    audit_cement_declaration,
    compute_cement_process_emissions_minimum,
)
from src.core.stoichiometry.steel_models import (
    SteelDeclarationInput,
    audit_steel_declaration,
)


def test_cement_chemical_calcination_minimum():
    """Verify that pure chemical CaCO3 -> CaO + CO2 mass balance cannot be circumvented."""
    clinker = 1000.0  # tonnes
    min_proc = compute_cement_process_emissions_minimum(clinker, cao_fraction=0.650, mgo_fraction=0.015)
    # 0.65 * 0.7848 + 0.015 * 1.0919 = 0.5101 + 0.0164 = 0.5265 tCO2 / t clinker
    assert 520.0 <= min_proc <= 535.0


def test_cement_underreporting_violation():
    """A cement plant declaring emissions below chemical calcination floor must fail."""
    decl = CementDeclarationInput(
        facility_name="Test Violating Cement Works",
        reporting_year=2023,
        clinker_produced_tonnes=100000.0,
        cement_produced_tonnes=125000.0,
        clinker_ratio=0.80,
        reported_direct_emissions_tco2=30000.0,  # 0.30 tCO2/t (chemically impossible)
    )
    result = audit_cement_declaration(decl)
    assert not result.is_physically_feasible
    assert result.discrepancy_tco2 < 0.0
    assert "Physical Impossibility Violation" in result.violation_reason


def test_cement_compliant_declaration():
    """A realistic cement plant declaration must pass physical feasibility."""
    decl = CementDeclarationInput(
        facility_name="Test Compliant Cement Works",
        reporting_year=2023,
        clinker_produced_tonnes=100000.0,
        cement_produced_tonnes=125000.0,
        clinker_ratio=0.80,
        reported_direct_emissions_tco2=82000.0,  # 0.82 tCO2/t (typical modern BAT dry kiln)
    )
    result = audit_cement_declaration(decl)
    assert result.is_physically_feasible
    assert result.reported_specific_intensity_tco2_per_t_clinker >= result.minimum_specific_intensity_tco2_per_t_clinker


def test_steel_bf_bof_stoichiometric_floor():
    """BF-BOF iron ore reduction (Fe2O3 + 3C -> 2Fe + 3CO) has a stoichiometric carbon floor."""
    decl = SteelDeclarationInput(
        facility_name="Test Blast Furnace Complex",
        reporting_year=2023,
        crude_steel_produced_tonnes=1000000.0,
        claimed_production_route="BF-BOF",
        reported_direct_emissions_tco2=800000.0,  # 0.80 tCO2/t (below BF-BOF thermodynamic floor ~1.18 tCO2/t)
    )
    result = audit_steel_declaration(decl)
    assert not result.is_physically_feasible
    assert "Physical Impossibility Violation" in result.violation_reason or "below the physical minimum" in result.violation_reason


def test_steel_route_misclassification_detection():
    """Declaring Scrap-EAF while emitting at BF-BOF levels triggers route misclassification warning."""
    decl = SteelDeclarationInput(
        facility_name="Suspect Mill",
        reporting_year=2023,
        crude_steel_produced_tonnes=1000000.0,
        claimed_production_route="Scrap-EAF",
        reported_direct_emissions_tco2=1750000.0,  # 1.75 tCO2/t (clearly a BF-BOF facility)
    )
    result = audit_steel_declaration(decl)
    assert result.route_misclassification_detected
    assert "BF-BOF" in result.suspected_actual_route
