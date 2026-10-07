"""
VeriCBAM Stoichiometry - Cement Sector Models
Implements first-principles chemical calcination mass balance and thermodynamic minimum energy constraints
for cement clinker production, adhering to EU CBAM Annex IV and IPCC Tier 3 guidelines.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple


# Physical and chemical constants
MOLAR_MASS_CACO3 = 100.0869  # g/mol
MOLAR_MASS_CAO = 56.0774    # g/mol
MOLAR_MASS_CO2 = 44.0095    # g/mol
MOLAR_MASS_MGCO3 = 84.3139  # g/mol
MOLAR_MASS_MGO = 40.3044    # g/mol

# Stoichiometric conversion factors (t CO2 / t oxide)
RATIO_CO2_CAO = MOLAR_MASS_CO2 / MOLAR_MASS_CAO   # ~0.7848 t CO2 / t CaO
RATIO_CO2_MGO = MOLAR_MASS_CO2 / MOLAR_MASS_MGO   # ~1.0919 t CO2 / t MgO

# Best Available Technology (BAT) thermodynamic limits (EU BREF Cement, Lime & MgO)
BAT_THERMAL_CONSUMPTION_DRY_MJ_T = 3000.0  # MJ/tonne clinker (theoretical modern preheater/precalciner BAT)
BEST_EFFICIENCY_THERMAL_MJ_T = 2900.0      # Absolute physical minimum with best raw meal reactivity
POOR_EFFICIENCY_THERMAL_MJ_T = 4500.0      # Older long wet kiln

# Typical fuel emission factors (kg CO2 / GJ = t CO2 / TJ)
FUEL_EMISSION_FACTORS_T_CO2_PER_GJ = {
    "natural_gas": 0.0561,
    "heavy_fuel_oil": 0.0774,
    "coal": 0.0946,
    "petcoke": 0.1009,
    "waste_derived_fuel_50pct_bio": 0.0450,  # fossil fraction only
    "zero_carbon_hydrogen": 0.0,
}


@dataclass
class CementDeclarationInput:
    """Represents a CBAM declaration for cement clinker or cement."""
    facility_name: str
    reporting_year: int
    clinker_produced_tonnes: float
    cement_produced_tonnes: float
    clinker_ratio: float  # e.g. 0.95 for CEM I, 0.70 for CEM II
    cao_content_clinker: float = 0.650  # fraction CaO in clinker (default 65.0%)
    mgo_content_clinker: float = 0.015  # fraction MgO in clinker (default 1.5%)
    reported_direct_emissions_tco2: float = 0.0  # Scope 1 reported
    reported_fuel_type: str = "coal"
    ccus_captured_tco2: float = 0.0  # verified permanently sequestered CO2


@dataclass
class StoichiometricAuditResult:
    """Result of first-principles physical validation."""
    process_emissions_min_tco2: float
    combustion_emissions_min_tco2: float
    total_physical_minimum_tco2: float
    reported_specific_intensity_tco2_per_t_clinker: float
    minimum_specific_intensity_tco2_per_t_clinker: float
    is_physically_feasible: bool
    discrepancy_tco2: float
    discrepancy_percentage: float
    confidence_level: str
    violation_reason: str


def compute_cement_process_emissions_minimum(
    clinker_tonnes: float,
    cao_fraction: float = 0.650,
    mgo_fraction: float = 0.015,
) -> float:
    """Computes stoichiometric minimum CO2 released purely from raw limestone calcination.

    Chemical calcination reactions:
        CaCO3 -> CaO + CO2 (0.7848 t CO2 / t CaO)
        MgCO3 -> MgO + CO2 (1.0919 t CO2 / t MgO)

    This represents a fixed chemical mass balance that cannot be eliminated without altering clinker mineralogy.

    Args:
        clinker_tonnes (float): Total mass of clinker produced in tonnes.
        cao_fraction (float, optional): Fraction of CaO in clinker (default: 0.650, i.e., 65.0%).
        mgo_fraction (float, optional): Fraction of MgO in clinker (default: 0.015, i.e., 1.5%).

    Returns:
        float: Minimum process CO2 emissions in tonnes (t CO2).
    """
    process_factor = (cao_fraction * RATIO_CO2_CAO) + (mgo_fraction * RATIO_CO2_MGO)
    return clinker_tonnes * process_factor


def compute_cement_thermal_combustion_minimum(
    clinker_tonnes: float,
    fuel_type: str = "coal",
    efficiency_mj_per_tonne: float = BAT_THERMAL_CONSUMPTION_DRY_MJ_T,
) -> float:
    """Computes thermodynamic minimum combustion CO2 required to supply kiln thermal energy.

    Supplies the endothermic calcination enthalpy (CaCO3 -> CaO + CO2, Delta H = +178.2 kJ/mol CaCO3)
    plus thermodynamic heat losses in state-of-the-art kilns.

    Args:
        clinker_tonnes (float): Total mass of clinker produced in tonnes.
        fuel_type (str, optional): Fuel type used for combustion (default: "coal").
            Supported types include 'natural_gas', 'heavy_fuel_oil', 'coal', 'petcoke',
            'waste_derived_fuel_50pct_bio', and 'zero_carbon_hydrogen'.
        efficiency_mj_per_tonne (float, optional): Thermal energy consumption efficiency in MJ per tonne of clinker
            (default: 3000.0 MJ/t representing BAT preheater/precalciner kiln).

    Returns:
        float: Minimum thermal combustion CO2 emissions in tonnes (t CO2).
    """
    fuel_ef = FUEL_EMISSION_FACTORS_T_CO2_PER_GJ.get(fuel_type.lower(), 0.0946)
    # Energy per tonne in GJ = MJ / 1000
    energy_gj_per_tonne = efficiency_mj_per_tonne / 1000.0
    combustion_ef_per_tonne = energy_gj_per_tonne * fuel_ef
    return clinker_tonnes * combustion_ef_per_tonne


def audit_cement_declaration(declaration: CementDeclarationInput) -> StoichiometricAuditResult:
    """Audits a CBAM cement declaration against stoichiometric and thermodynamic bounds.

    Calculates minimum process emissions from limestone calcination (CaCO3 -> CaO + CO2 and MgCO3 -> MgO + CO2)
    and minimum combustion emissions based on kiln thermal requirements to verify physical compliance.

    Args:
        declaration (CementDeclarationInput): The CBAM declaration input containing facility, production,
            oxide fractions, reported emissions, fuel type, and CCUS details.

    Returns:
        StoichiometricAuditResult: Audit result detailing minimum process emissions, minimum combustion
            emissions, total physical floor, specific intensities, discrepancy, and compliance status.
    """
    clinker = declaration.clinker_produced_tonnes
    if clinker <= 0 and declaration.cement_produced_tonnes > 0:
        clinker = declaration.cement_produced_tonnes * declaration.clinker_ratio

    # 1. Chemical process minimum
    min_process = compute_cement_process_emissions_minimum(
        clinker_tonnes=clinker,
        cao_fraction=declaration.cao_content_clinker,
        mgo_fraction=declaration.mgo_content_clinker,
    )

    # 2. Thermodynamic combustion minimum (using best available technology as conservative lower bound)
    min_combustion = compute_cement_thermal_combustion_minimum(
        clinker_tonnes=clinker,
        fuel_type=declaration.reported_fuel_type,
        efficiency_mj_per_tonne=BAT_THERMAL_CONSUMPTION_DRY_MJ_T,
    )

    total_min_before_ccus = min_process + min_combustion
    net_min_expected = max(0.0, total_min_before_ccus - declaration.ccus_captured_tco2)

    reported_emissions = declaration.reported_direct_emissions_tco2
    reported_intensity = (reported_emissions / clinker) if clinker > 0 else 0.0
    min_intensity = (net_min_expected / clinker) if clinker > 0 else 0.0

    discrepancy = reported_emissions - net_min_expected
    discrepancy_pct = (discrepancy / net_min_expected * 100.0) if net_min_expected > 0 else 0.0

    # Margin of tolerance (measurement uncertainty under EU ETS / ISO 14064 is typically +/- 2.5%)
    tolerance_threshold = -0.025 * net_min_expected

    if discrepancy < tolerance_threshold:
        is_feasible = False
        reason = (
            f"Physical Impossibility Violation: Reported direct emissions ({reported_emissions:,.0f} t CO2) "
            f"fall below the thermodynamic & stoichiometric lower bound ({net_min_expected:,.0f} t CO2). "
            f"Under-reporting margin: {abs(discrepancy):,.0f} t CO2 ({abs(discrepancy_pct):.1f}% below physical floor)."
        )
        confidence = "High (Deterministic Stoichiometric Proof)"
    else:
        is_feasible = True
        reason = "Complies with thermodynamic and mass balance lower bounds."
        confidence = "High (Physically Verified)"

    return StoichiometricAuditResult(
        process_emissions_min_tco2=min_process,
        combustion_emissions_min_tco2=min_combustion,
        total_physical_minimum_tco2=net_min_expected,
        reported_specific_intensity_tco2_per_t_clinker=reported_intensity,
        minimum_specific_intensity_tco2_per_t_clinker=min_intensity,
        is_physically_feasible=is_feasible,
        discrepancy_tco2=discrepancy,
        discrepancy_percentage=discrepancy_pct,
        confidence_level=confidence,
        violation_reason=reason,
    )


if __name__ == "__main__":
    # Test case: CEMEX Rüdersdorf style plant producing 1,000,000 tonnes clinker
    # Legitimate reporting (~780 kg CO2 / t clinker)
    legit = CementDeclarationInput(
        facility_name="CEMEX Rüdersdorf",
        reporting_year=2023,
        clinker_produced_tonnes=1000000.0,
        cement_produced_tonnes=1150000.0,
        clinker_ratio=0.87,
        reported_direct_emissions_tco2=810000.0,
        reported_fuel_type="coal",
    )
    res_legit = audit_cement_declaration(legit)
    print("Legitimate Plant Audit:")
    print(" - Feasible:", res_legit.is_physically_feasible)
    print(f" - Min Intensity: {res_legit.minimum_specific_intensity_tco2_per_t_clinker:.3f} tCO2/t")
    print(f" - Reported Intensity: {res_legit.reported_specific_intensity_tco2_per_t_clinker:.3f} tCO2/t")

    # Fraudulent / Greenwashed declaration: claiming 350 kg CO2 / t clinker without CCUS
    fraud = CementDeclarationInput(
        facility_name="Suspicious Importer Clinker",
        reporting_year=2023,
        clinker_produced_tonnes=1000000.0,
        cement_produced_tonnes=1150000.0,
        clinker_ratio=0.87,
        reported_direct_emissions_tco2=350000.0,
        reported_fuel_type="coal",
    )
    res_fraud = audit_cement_declaration(fraud)
    print("\nFraudulent Claim Audit:")
    print(" - Feasible:", res_fraud.is_physically_feasible)
    print(" - Reason:", res_fraud.violation_reason)
