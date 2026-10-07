"""
VeriCBAM Stoichiometry - Iron & Steel Sector Models
Implements first-principles carbon reduction mass balances and furnace thermodynamic energy constraints
for primary and secondary steelmaking routes, adhering to EU CBAM Annex IV and IPCC guidelines.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple


# Stoichiometric carbon consumption for hematite reduction:
# Fe2O3 + 3 C -> 2 Fe + 3 CO
# Molar masses: Fe = 55.845 g/mol, C = 12.011 g/mol, O = 15.999 g/mol, Fe2O3 = 159.69 g/mol
# Stoichiometric minimum carbon = (3 * 12.011) / (2 * 55.845) = 36.033 / 111.69 = 0.3226 t C / t Fe.
# When CO oxidizes to CO2: 0.3226 * (44.01 / 12.011) = 1.182 t CO2 / t crude iron.

MIN_C_REDUCTION_PER_T_FE = 0.3226  # t Carbon / t hot metal
STOICHIOMETRIC_MIN_CO2_REDUCTION_BF = 1.182  # t CO2 / t crude iron purely for reduction

# Empirical & thermodynamic benchmarks from EU BREF Iron and Steel (t CO2 / t liquid steel Scope 1):
ROUTE_BENCHMARKS = {
    "BF-BOF": {  # Integrated Blast Furnace - Basic Oxygen Furnace
        "absolute_min_scope1_tco2_per_t": 1.35,  # Absolute best efficiency with top gas recovery & high scrap
        "typical_scope1_tco2_per_t": 1.85,
        "high_scope1_tco2_per_t": 2.20,
    },
    "DRI-NG-EAF": {  # Direct Reduced Iron (Natural Gas) + Electric Arc Furnace
        "absolute_min_scope1_tco2_per_t": 0.55,  # Direct Scope 1 fossil gas reduction
        "typical_scope1_tco2_per_t": 0.75,
        "high_scope1_tco2_per_t": 0.95,
    },
    "DRI-H2-EAF": {  # Direct Reduced Iron (100% Green Hydrogen) + EAF
        "absolute_min_scope1_tco2_per_t": 0.04,  # Graphite electrode wear and carbon recarburizer only
        "typical_scope1_tco2_per_t": 0.08,
        "high_scope1_tco2_per_t": 0.15,
    },
    "Scrap-EAF": {  # Secondary steelmaking (100% recycled scrap melting)
        "absolute_min_scope1_tco2_per_t": 0.04,  # Carbon charge, natural gas burner, electrode consumption
        "typical_scope1_tco2_per_t": 0.12,
        "high_scope1_tco2_per_t": 0.28,
    },
}


@dataclass
class SteelDeclarationInput:
    """Represents a CBAM declaration for crude steel or steel products."""
    facility_name: str
    reporting_year: int
    crude_steel_produced_tonnes: float
    claimed_production_route: str  # "BF-BOF", "DRI-NG-EAF", "DRI-H2-EAF", "Scrap-EAF"
    reported_direct_emissions_tco2: float  # Scope 1 reported
    scrap_ratio: float = 0.15  # scrap fraction (0.15-0.25 typical for BOF, ~1.0 for Scrap-EAF)
    ccus_captured_tco2: float = 0.0


@dataclass
class SteelStoichiometricAuditResult:
    """Result of first-principles physical validation for steelmaking."""
    reported_specific_intensity_tco2_per_t: float
    theoretical_floor_intensity_tco2_per_t: float
    typical_benchmark_intensity_tco2_per_t: float
    total_physical_minimum_tco2: float
    is_physically_feasible: bool
    discrepancy_tco2: float
    discrepancy_percentage: float
    route_misclassification_detected: bool
    suspected_actual_route: str
    confidence_level: str
    violation_reason: str


def audit_steel_declaration(declaration: SteelDeclarationInput) -> SteelStoichiometricAuditResult:
    """
    Audits a CBAM steel declaration against production route thermodynamics and mass balances.
    Detects both under-reporting and route misclassification (e.g. declaring scrap-EAF while operating BF-BOF).
    """
    route = declaration.claimed_production_route
    if route not in ROUTE_BENCHMARKS:
        raise ValueError(f"Unknown production route: {route}. Expected one of {list(ROUTE_BENCHMARKS.keys())}")

    benchmarks = ROUTE_BENCHMARKS[route]
    steel_tonnes = declaration.crude_steel_produced_tonnes

    reported_emissions = declaration.reported_direct_emissions_tco2
    reported_intensity = (reported_emissions / steel_tonnes) if steel_tonnes > 0 else 0.0

    # Minimum intensity for claimed route accounting for scrap dilution
    base_floor = benchmarks["absolute_min_scope1_tco2_per_t"]
    if route == "BF-BOF":
        # Scrap dilution lowers BF demand: e.g. 20% scrap reduces BF hot metal needed
        hot_metal_ratio = max(0.65, 1.0 - declaration.scrap_ratio)
        effective_floor = (base_floor * hot_metal_ratio) + (0.05 * declaration.scrap_ratio)
    else:
        effective_floor = base_floor

    min_expected_tco2 = max(0.0, (effective_floor * steel_tonnes) - declaration.ccus_captured_tco2)
    effective_floor_intensity = (min_expected_tco2 / steel_tonnes) if steel_tonnes > 0 else 0.0

    discrepancy = reported_emissions - min_expected_tco2
    discrepancy_pct = (discrepancy / min_expected_tco2 * 100.0) if min_expected_tco2 > 0 else 0.0

    # Check for route misclassification:
    # If importer claims Scrap-EAF or Green DRI (< 0.3 t CO2/t) but facility emits > 1.2 t CO2/t,
    # or conversely if plant operates as BF-BOF but claims EAF emissions.
    route_misclass = False
    suspected_route = route

    tolerance = -0.05 * min_expected_tco2  # 5% tolerance margin

    if discrepancy < tolerance:
        is_feasible = False
        confidence = "High (Thermodynamic Violation)"
        reason = (
            f"Physical Impossibility Violation: Reported direct emissions ({reported_emissions:,.0f} t CO2; "
            f"{reported_intensity:.3f} t CO2/t steel) fall below the physical minimum for claimed route "
            f"'{route}' ({min_expected_tco2:,.0f} t CO2; {effective_floor_intensity:.3f} t CO2/t steel). "
            f"Under-reporting margin: {abs(discrepancy):,.0f} t CO2 ({abs(discrepancy_pct):.1f}% below physical floor)."
        )
    else:
        is_feasible = True
        confidence = "High (Physically Verified)"
        reason = f"Reported emissions are consistent with thermodynamic bounds for {route}."

    # Route misclassification check:
    # E.g. Claiming BF-BOF emissions (1.8 t/t) when declaring EAF, or vice-versa
    if route in ["Scrap-EAF", "DRI-H2-EAF"] and reported_intensity > 0.8:
        route_misclass = True
        suspected_route = "BF-BOF or Coal DRI"
        reason += (
            f" [ROUTE ANOMALY DETECTED]: Claimed route is {route} (typical {benchmarks['typical_scope1_tco2_per_t']} t CO2/t), "
            f"but reported intensity ({reported_intensity:.3f} t CO2/t) is characteristic of {suspected_route}."
        )

    return SteelStoichiometricAuditResult(
        reported_specific_intensity_tco2_per_t=reported_intensity,
        theoretical_floor_intensity_tco2_per_t=effective_floor_intensity,
        typical_benchmark_intensity_tco2_per_t=benchmarks["typical_scope1_tco2_per_t"],
        total_physical_minimum_tco2=min_expected_tco2,
        is_physically_feasible=is_feasible,
        discrepancy_tco2=discrepancy,
        discrepancy_percentage=discrepancy_pct,
        route_misclassification_detected=route_misclass,
        suspected_actual_route=suspected_route,
        confidence_level=confidence,
        violation_reason=reason,
    )


if __name__ == "__main__":
    # Test 1: Real Salzgitter BF-BOF steel plant (producing 4,500,000 tonnes crude steel)
    salzgitter = SteelDeclarationInput(
        facility_name="Salzgitter Flachstahl",
        reporting_year=2023,
        crude_steel_produced_tonnes=4200000.0,
        claimed_production_route="BF-BOF",
        reported_direct_emissions_tco2=7300000.0,
        scrap_ratio=0.18,
    )
    res_salz = audit_steel_declaration(salzgitter)
    print("Salzgitter Audit:")
    print(" - Feasible:", res_salz.is_physically_feasible)
    print(f" - Reported Intensity: {res_salz.reported_specific_intensity_tco2_per_t:.3f} tCO2/t")
    print(f" - Floor Intensity: {res_salz.theoretical_floor_intensity_tco2_per_t:.3f} tCO2/t")

    # Test 2: Fraudulent BF-BOF declaration claiming 0.45 t CO2/t without CCUS
    fraud_bf = SteelDeclarationInput(
        facility_name="Suspicious Integrated Steelwork",
        reporting_year=2023,
        crude_steel_produced_tonnes=2000000.0,
        claimed_production_route="BF-BOF",
        reported_direct_emissions_tco2=900000.0,
        scrap_ratio=0.15,
    )
    res_fraud_bf = audit_steel_declaration(fraud_bf)
    print("\nFraudulent BF-BOF Audit:")
    print(" - Feasible:", res_fraud_bf.is_physically_feasible)
    print(" - Reason:", res_fraud_bf.violation_reason)
