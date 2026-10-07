"""
VeriCBAM - Multimodal Decision Support System for CBAM Emissions Auditing
Master Capstone Interactive Dashboard
University of Europe for Applied Sciences (UE Germany)
Master of Science in Data Science | Cristhian David Caceres Mateus
Supervisor: Dr. Humera Noor
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Add src to python path
src_dir = Path(__file__).parents[1]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from data_loaders.cohort_manager import CohortManager
from core.stoichiometry.cement_models import CementDeclarationInput, audit_cement_declaration
from core.stoichiometry.steel_models import SteelDeclarationInput, audit_steel_declaration
from core.bayesian.evidence_fusion import ProbabilisticEvidenceFusionEngine, EvidenceInput
from satellite.copernicus_client import CopernicusSentinel5PClient
from satellite.plume_analyzer import SatellitePlumeAnalyzer

st.set_page_config(
    page_title="VeriCBAM | Decision Support System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #E2E8F0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load data
@st.cache_data
def load_cohort_data():
    mgr = CohortManager()
    facilities = mgr.get_all_facilities().copy()
    if "Latitude" in facilities.columns and "latitude" not in facilities.columns:
        facilities["latitude"] = facilities["Latitude"]
    if "Longitude" in facilities.columns and "longitude" not in facilities.columns:
        facilities["longitude"] = facilities["Longitude"]
    return mgr, facilities

mgr, facilities_df = load_cohort_data()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=64)
st.sidebar.title("VeriCBAM Audit Suite")
st.sidebar.caption("EU CBAM Emissions Consistency Verification")

menu = st.sidebar.radio(
    "Navigation",
    [
        "1. Executive Overview",
        "2. 30-Facility Benchmark Cohort",
        "3. Stoichiometric Physics Engine",
        "4. Standalone Supplier Plausibility Pre-Check",
        "5. Copernicus Satellite Engine (Sentinel-5P)",
        "6. Bayesian Evidence Fusion",
        "7. 5-Model Ablation & Calibration Benchmark",
        "8. Capstone Proposal, References & Roadmap",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Student:** Cristhian David Cáceres Mateus\n\n"
    "**Program:** M.Sc. Data Science\n\n"
    "**University:** UE Germany (Berlin)\n\n"
    "**Supervisor:** Dr. Humera Noor"
)

# -------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
if menu == "1. Executive Overview":
    st.markdown('<div class="main-title">VeriCBAM: Multimodal Evidence Fusion for Carbon Border Auditing</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">A Deterministic-Bayesian Decision Support Architecture for European Carbon Border Adjustment Mechanism (CBAM) Compliance</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Complex Site Audit Cost", "€50k – €150k+", "Per BF-BOF / Cement Site")
    with col2:
        st.metric("Verifier Scarcity", "12k Declarants vs 403 Verifiers", "Global AVR Deficit")
    with col3:
        st.metric("Audit Lead Time", "3 – 6+ Months", "Physical On-Site Bottleneck")
    with col4:
        st.metric("Default Mark-up Penalty", "+10% to +30%", "2026-2028 Punitive Surcharge")

    st.markdown("### The Empirical Problem: The Verification Bottleneck")
    st.markdown(
        """
        Under **Regulation (EU) 2023/956**, **Implementing Regulation (EU) 2025/2546** (verification rules), 
        **Implementing Regulation (EU) 2025/2551** (verifier accreditation), and **Implementing Regulation (EU) 2025/2547** 
        (calculation of embedded emissions), EU importers of heavy industrial commodities (primarily **Cement and Steel**) 
        who report actual embedded emissions must undergo mandatory third-party verification, including an initial physical on-site inspection.
        
        This introduces a severe operational and economic market failure:
        1. **Steep Verification Costs:** Standard facility audits cost **€15,000–€50,000**, escalating to **€50,000–€150,000+** per site for complex integrated metallurgical complexes (BF-BOF) and cement kilns when factoring in international auditor travel to third countries (India, China, Turkey, Brazil), laboratory assays, and MRV infrastructure (GMK Center, 2024; EC SWD(2021) 643).
        2. **The "Arithmetic of Scarcity":** Approximately **12,000 EU import entities** are seeking authorized CBAM declarant status, yet only **~403 verification bodies globally** hold accreditation under the EU Accreditation and Verification Regulation (**AVR 2018/2067** / **(EU) 2025/2551**).
        3. **Administrative Deadlocks:** Complete audit cycles require **3 to 6 months**. Importers unable to schedule verifiers are forced to declare default values carrying punitive mark-ups (**+10% in 2026, +20% in 2027, +30% in 2028**), costing importers millions in excess certificate surcharges.
        
        **VeriCBAM** directly resolves this crisis by providing automated, deterministic, and satellite-corroborated pre-audit screening, 
        allowing customs authorities and buyers to triage physical audits to high-risk installations while prioritizing declarations for further verification.
        """
    )

    with st.expander("📚 View Supporting Regulatory & Academic References"):
        st.markdown(
            """
            - **European Commission (2021):** *Impact Assessment Report on CBAM*, SWD(2021) 643 final (Section 6.6 & Annex 6).
            - **Regulation (EU) 2023/956:** Establishing a carbon border adjustment mechanism (Articles 8 & 9).
            - **Commission Implementing Regulation (EU) 2025/2546:** Principles and rules for verification of emissions declarations.
            - **Commission Implementing Regulation (EU) 2025/2551:** Rules for accreditation of verifiers.
            - **Commission Implementing Regulation (EU) 2025/2547:** Rules for calculation of embedded direct and indirect emissions.
            - **Commission Implementing Regulation (EU) 2018/2067:** General rules on accreditation and verification (AVR).
            - **GMK Center (2024):** *CBAM Verification: Requirements, Costs and Industry Bottlenecks in the Steel Sector*.
            - **European Environment Agency (2026):** *EEA Industrial Reporting Database (E-PRTR / IED v16)* (100% empirical validation cohort).
            - **OECD (2023):** *Carbon-Related Border Adjustments and Developing Country Exporters*, OECD Trade & Environment Papers.
            """
        )


# -------------------------------------------------------------
# TAB 2: BENCHMARK COHORT
# -------------------------------------------------------------
elif menu == "2. 30-Facility Benchmark Cohort":
    st.markdown('<div class="main-title">Curated 30-Facility European Benchmark Cohort</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Authentic multi-year Scope 1 CO₂ emission records from the European Pollutant Release and Transfer Register (E-PRTR / IED v16)</div>',
        unsafe_allow_html=True,
    )

    c_filter, s_filter = st.columns([1, 3])
    with c_filter:
        sector_choice = st.selectbox("Select Sector", ["All Sectors", "Cement", "Steel"])
    with s_filter:
        country_choice = st.selectbox("Select Country Filter", ["All Countries"] + sorted(facilities_df["countryName"].unique().tolist()))

    filtered_facilities = facilities_df.copy()
    if sector_choice != "All Sectors":
        filtered_facilities = filtered_facilities[filtered_facilities["sector"] == sector_choice]
    if country_choice != "All Countries":
        filtered_facilities = filtered_facilities[filtered_facilities["countryName"] == country_choice]

    # Map Visualization
    # Ensure coordinates exist in filtered_facilities
    if "latitude" not in filtered_facilities.columns and "Latitude" in filtered_facilities.columns:
        filtered_facilities["latitude"] = filtered_facilities["Latitude"]
    if "longitude" not in filtered_facilities.columns and "Longitude" in filtered_facilities.columns:
        filtered_facilities["longitude"] = filtered_facilities["Longitude"]

    try:
        fig_map = px.scatter_map(
            filtered_facilities,
            lat="latitude",
            lon="longitude",
            hover_name="facilityName",
            hover_data={"city": True, "countryName": True, "mean_co2_tonnes": ":,.0f", "sector": True, "latitude": False, "longitude": False},
            color="sector",
            size="mean_co2_tonnes",
            color_discrete_map={"Cement": "#F59E0B", "Steel": "#3B82F6"},
            size_max=32,
            zoom=3.8,
            center={"lat": 51.1657, "lon": 10.4515},
            title="Geospatial Distribution of Benchmark Industrial Cohort",
        )
    except Exception:
        fig_map = px.scatter_mapbox(
            filtered_facilities,
            lat="latitude",
            lon="longitude",
            hover_name="facilityName",
            hover_data={"city": True, "countryName": True, "mean_co2_tonnes": ":,.0f", "sector": True, "latitude": False, "longitude": False},
            color="sector",
            size="mean_co2_tonnes",
            color_discrete_map={"Cement": "#F59E0B", "Steel": "#3B82F6"},
            size_max=32,
            zoom=3.8,
            center={"lat": 51.1657, "lon": 10.4515},
            mapbox_style="carto-positron",
            title="Geospatial Distribution of Benchmark Industrial Cohort",
        )
    fig_map.update_layout(height=480, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    # Detailed Table & Time Series
    st.markdown("### Facility Inspection & Multi-Year Emission Time Series")
    selected_facility_name = st.selectbox("Select Facility to Inspect Historical Emissions:", filtered_facilities["facilityName"].tolist())

    if selected_facility_name:
        fac_row = filtered_facilities[filtered_facilities["facilityName"] == selected_facility_name].iloc[0]
        fac_id = fac_row["FacilityInspireId"]
        ts_df = mgr.get_facility_time_series(fac_id)
        fac_lat = float(fac_row.get("latitude", fac_row.get("Latitude", 0.0)))
        fac_lon = float(fac_row.get("longitude", fac_row.get("Longitude", 0.0)))

        col_left, col_right = st.columns([1, 2])
        with col_left:
            st.markdown(f"**Facility:** {fac_row['facilityName']}")
            st.markdown(f"**Sector:** `{fac_row['sector']}`")
            st.markdown(f"**Location:** {fac_row['city']}, {fac_row['countryName']}")
            if "verified_technology_route" in fac_row and pd.notna(fac_row["verified_technology_route"]):
                st.markdown(f"**Verified Route:** `{fac_row['verified_technology_route']}`")
            if "clinker_capacity_mtpa" in fac_row and pd.notna(fac_row["clinker_capacity_mtpa"]) and fac_row["clinker_capacity_mtpa"] > 0:
                st.markdown(f"**Clinker Capacity:** {fac_row['clinker_capacity_mtpa']:.2f} Mt/yr")
            if "crude_steel_capacity_mtpa" in fac_row and pd.notna(fac_row["crude_steel_capacity_mtpa"]) and fac_row["crude_steel_capacity_mtpa"] > 0:
                st.markdown(f"**Crude Steel Capacity:** {fac_row['crude_steel_capacity_mtpa']:.2f} Mt/yr")
            if "technology_source" in fac_row and pd.notna(fac_row["technology_source"]):
                st.caption(f"Source: {fac_row['technology_source']}")
            st.markdown(f"**Mean Annual CO₂:** {fac_row['mean_co2_tonnes']:,.0f} metric tonnes/yr")
            st.markdown(f"**Coordinates:** ({fac_lat:.4f}, {fac_lon:.4f})")
            st.markdown(f"**INSPIRE ID:** `{fac_id}`")

        with col_right:
            if not ts_df.empty:
                fig_ts = px.bar(
                    ts_df,
                    x="reportingYear",
                    y="co2_tonnes",
                    labels={"reportingYear": "Reporting Year", "co2_tonnes": "Verified Scope 1 CO₂ (Tonnes)"},
                    title=f"Historical Emissions Trajectory: {fac_row['facilityName']}",
                    color_discrete_sequence=["#1E293B"],
                )
                fig_ts.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_ts, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: STOICHIOMETRIC PHYSICS ENGINE
# -------------------------------------------------------------
elif menu == "3. Stoichiometric Physics Engine":
    st.markdown('<div class="main-title">Deterministic Stoichiometric Physics Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Evaluation of CBAM declarations against fundamental chemical mass balances and thermodynamic lower bounds</div>',
        unsafe_allow_html=True,
    )

    sector_mode = st.radio("Select Production Sector for Audit Simulation:", ["Cement Clinker", "Crude Steel"], horizontal=True)

    if sector_mode == "Cement Clinker":
        st.markdown("#### Cement Audit: Calcination Reaction $\\text{CaCO}_3 \\xrightarrow{\\Delta} \\text{CaO} + \\text{CO}_2$")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            clinker_tonnes = st.number_input("Clinker Produced (Metric Tonnes)", min_value=10000.0, max_value=5000000.0, value=1000000.0, step=50000.0)
            cement_tonnes = st.number_input("Total Cement Produced (Tonnes)", min_value=10000.0, max_value=6000000.0, value=1150000.0, step=50000.0)
        with col_c2:
            clinker_ratio = st.slider("Clinker-to-Cement Ratio", min_value=0.40, max_value=1.0, value=0.87, step=0.01)
            fuel_type = st.selectbox("Primary Kiln Fuel", ["coal", "petcoke", "natural_gas", "waste_derived_fuel_50pct_bio"])
        with col_c3:
            reported_co2 = st.number_input("Reported Direct Scope 1 CO₂ (Tonnes)", min_value=0.0, max_value=5000000.0, value=810000.0, step=25000.0)
            ccus_tco2 = st.number_input("Verified CCUS Captured CO₂ (Tonnes)", min_value=0.0, max_value=1000000.0, value=0.0, step=10000.0)

        decl_cement = CementDeclarationInput(
            facility_name="Audit Candidate Kiln",
            reporting_year=2024,
            clinker_produced_tonnes=clinker_tonnes,
            cement_produced_tonnes=cement_tonnes,
            clinker_ratio=clinker_ratio,
            reported_direct_emissions_tco2=reported_co2,
            reported_fuel_type=fuel_type,
            ccus_captured_tco2=ccus_tco2,
        )
        res_cement = audit_cement_declaration(decl_cement)

        st.markdown("---")
        st.markdown("### Audit Diagnostic Output")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Chemical Calcination Floor", f"{res_cement.process_emissions_min_tco2:,.0f} tCO₂", "Fixed Mass Balance")
        m2.metric("Thermal Combustion Floor", f"{res_cement.combustion_emissions_min_tco2:,.0f} tCO₂", f"BAT Kiln ({fuel_type})")
        m3.metric("Net Physical Floor", f"{res_cement.total_physical_minimum_tco2:,.0f} tCO₂", "Absolute Minimum")
        
        status_color = "normal" if res_cement.is_physically_feasible else "inverse"
        m4.metric("Specific Intensity", f"{res_cement.reported_specific_intensity_tco2_per_t_clinker:.3f} tCO₂/t", f"Floor: {res_cement.minimum_specific_intensity_tco2_per_t_clinker:.3f} tCO₂/t")

        if not res_cement.is_physically_feasible:
            st.error(f"🚨 **AUDIT FLAG: PHYSICAL FEASIBILITY VIOLATION**\n\n{res_cement.violation_reason}")
        else:
            st.success(f"✅ **PHYSICALLY FEASIBLE UNDER MODEL ASSUMPTIONS:** {res_cement.violation_reason}")

    else:
        st.markdown("#### Iron & Steel Audit: Blast Furnace Reduction vs DRI vs EAF")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            steel_tonnes = st.number_input("Crude Steel Produced (Tonnes)", min_value=10000.0, max_value=10000000.0, value=2000000.0, step=50000.0)
            claimed_route = st.selectbox("Claimed Production Route", ["BF-BOF", "DRI-NG-EAF", "DRI-H2-EAF", "Scrap-EAF"])
        with col_s2:
            scrap_ratio = st.slider("Scrap Ratio (Dilution)", min_value=0.05, max_value=1.0, value=0.18, step=0.01)
            reported_steel_co2 = st.number_input("Reported Scope 1 CO₂ (Tonnes)", min_value=0.0, max_value=10000000.0, value=3600000.0, step=50000.0)
        with col_s3:
            steel_ccus = st.number_input("Verified CCUS Captured CO₂ (Tonnes)", min_value=0.0, max_value=2000000.0, value=0.0, step=10000.0)

        decl_steel = SteelDeclarationInput(
            facility_name="Audit Candidate Steelwork",
            reporting_year=2024,
            crude_steel_produced_tonnes=steel_tonnes,
            claimed_production_route=claimed_route,
            reported_direct_emissions_tco2=reported_steel_co2,
            scrap_ratio=scrap_ratio,
            ccus_captured_tco2=steel_ccus,
        )
        res_steel = audit_steel_declaration(decl_steel)

        st.markdown("---")
        st.markdown("### Audit Diagnostic Output")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Reported Specific Intensity", f"{res_steel.reported_specific_intensity_tco2_per_t:.3f} tCO₂/t", "Declared Scope 1")
        m2.metric("Route Thermodynamic Floor", f"{res_steel.theoretical_floor_intensity_tco2_per_t:.3f} tCO₂/t", f"Floor for {claimed_route}")
        m3.metric("Typical Benchmark", f"{res_steel.typical_benchmark_intensity_tco2_per_t:.3f} tCO₂/t", "EU BREF Median")
        m4.metric("Net Minimum Allowable", f"{res_steel.total_physical_minimum_tco2:,.0f} tCO₂", "Physical Threshold")

        if not res_steel.is_physically_feasible:
            st.error(f"🚨 **AUDIT FLAG: ROUTE ENGINEERING LOWER BOUND VIOLATION**\n\n{res_steel.violation_reason}")
        elif res_steel.route_misclassification_detected:
            st.warning(f"⚠️ **ROUTE MISCLASSIFICATION SUSPECTED**\n\n{res_steel.violation_reason}")
        else:
            st.success(f"✅ **NO ROUTE INCONSISTENCY DETECTED UNDER CURRENT EVIDENCE:** {res_steel.violation_reason}")

# -------------------------------------------------------------
# TAB 4: STANDALONE SUPPLIER PLAUSIBILITY PRE-CHECK
# -------------------------------------------------------------
elif menu == "4. Standalone Supplier Plausibility Pre-Check":
    st.markdown('<div class="main-title">Standalone Supplier Plausibility Pre-Check</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Rapid pre-audit screening of non-EU supplier declarations without requiring satellite or historical registry records</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "💡 **Immediate Practical Value:** Verifies thermodynamic feasibility for third-country exporters (e.g., India, Turkey, China) "
        "before contract execution or physical audit dispatch, flagging stoichiometric impossibilities and route misclassifications."
    )

    col_pc1, col_pc2 = st.columns(2)
    with col_pc1:
        st.markdown("#### Supplier Declaration Inputs")
        supplier_name = st.text_input("Supplier / Installation Name:", "Overseas Heavy Industries Ltd.")
        supp_sector = st.selectbox("Commodity Sector:", ["Cement Clinker", "Finished Cement (CEM II)", "Crude Steel (BF-BOF)", "Crude Steel (Scrap-EAF)"])
        decl_specific_emissions = st.number_input("Declared Specific Scope 1 Intensity (t CO₂ / t product):", min_value=0.0, max_value=5.0, value=0.62, step=0.01)
        annual_volume_tonnes = st.number_input("Annual Production Volume (Metric Tonnes):", min_value=1000.0, max_value=20000000.0, value=1200000.0, step=50000.0)

    # Determine bounds based on sector
    if "Cement Clinker" in supp_sector:
        floor = 0.770  # calcination 0.495 + BAT fuel 0.275
        typical_range = (0.800, 0.950)
        benchmark_note = "EU BREF Clinker Calcination + Modern BAT Kiln"
    elif "Finished Cement" in supp_sector:
        floor = 0.520  # CEM II blended with 70% clinker
        typical_range = (0.580, 0.720)
        benchmark_note = "CEM II Blended Cement (70% Clinker Ratio)"
    elif "BF-BOF" in supp_sector:
        floor = 1.350  # Absolute thermodynamic reduction floor + hot metal
        typical_range = (1.750, 2.200)
        benchmark_note = "Integrated Blast Furnace - Basic Oxygen Furnace (EU BREF)"
    else:
        floor = 0.040  # Secondary electric arc scrap melting
        typical_range = (0.080, 0.250)
        benchmark_note = "Electric Arc Furnace (100% Scrap Recycled)"

    is_feasible = decl_specific_emissions >= floor
    total_declared_co2 = decl_specific_emissions * annual_volume_tonnes
    total_floor_co2 = floor * annual_volume_tonnes
    deficit_co2 = max(0.0, total_floor_co2 - total_declared_co2)

    with col_pc2:
        st.markdown("#### Physical Feasibility & Benchmark Diagnostics")
        pm1, pm2 = st.columns(2)
        pm1.metric("Physical Minimum Floor", f"{floor:.3f} t CO₂/t", benchmark_note)
        pm2.metric("Typical Global Range", f"{typical_range[0]:.2f} – {typical_range[1]:.2f} t CO₂/t", "Standard Operations")

        if not is_feasible:
            st.error(
                f"🚨 **IMPOSSIBLE UNDER-DECLARATION FLAGGED**\n\n"
                f"Declared intensity (`{decl_specific_emissions:.3f} t CO₂/t`) breaches the absolute thermodynamic floor "
                f"(`{floor:.3f} t CO₂/t`).\n\n"
                f"- **Emissions Deficit:** Understated by at least **{deficit_co2:,.0f} t CO₂/year**.\n"
                f"- **Action:** Immediate audit priority; reject declaration until lab assay or process proof provided."
            )
        elif decl_specific_emissions < typical_range[0]:
            st.warning(
                f"⚠️ **UNUSUALLY LOW INTENSITY (REVIEW RECOMMENDED)**\n\n"
                f"Declared intensity (`{decl_specific_emissions:.3f} t CO₂/t`) is physically possible but sits below standard industry best practice "
                f"(`{typical_range[0]:.2f} t CO₂/t`). Requires documentation of CCUS or high bio-fuel replacement."
            )
        else:
            st.success(
                f"✅ **PLAUSIBLE SPECIFIC INTENSITY**\n\n"
                f"Declared intensity (`{decl_specific_emissions:.3f} t CO₂/t`) sits comfortably within plausible industrial operating ranges."
            )

        # Downloadable dossier button
        dossier_text = f"""# VeriCBAM Pre-Audit Screening Dossier
Installation: {supplier_name}
Commodity: {supp_sector}
Declared Specific Intensity: {decl_specific_emissions:.3f} t CO2/t product
Declared Annual Production: {annual_volume_tonnes:,.0f} tonnes
Total Declared Scope 1: {total_declared_co2:,.0f} t CO2
Thermodynamic Lower Bound: {floor:.3f} t CO2/t ({total_floor_co2:,.0f} t CO2 total)
Physical Feasibility Verdict: {'FEASIBLE' if is_feasible else 'VIOLATION DETECTED'}
Emissions Deficit: {deficit_co2:,.0f} t CO2
Audit Recommendation: {'Clear for expedited desk check' if is_feasible else 'HIGH AUDIT PRIORITY - Dispatch Physical Inspection'}
Generated by VeriCBAM Decision Support Cockpit.
"""
        st.download_button("📥 Download Supplier Screening Dossier (Markdown)", dossier_text, file_name=f"vericbam_dossier_{supplier_name.lower().replace(' ', '_')}.md")

# -------------------------------------------------------------
# TAB 5: COPERNICUS SATELLITE ENGINE
# -------------------------------------------------------------
elif menu == "5. Copernicus Satellite Engine (Sentinel-5P)":
    st.markdown('<div class="main-title">Copernicus Sentinel-5P Earth Observation Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Remote sensing atmospheric plume contrast, cloud-radiance filtering, and operational combustion inference</div>',
        unsafe_allow_html=True,
    )

    sat_client = CopernicusSentinel5PClient()
    sat_analyzer = SatellitePlumeAnalyzer()

    # Facility selector
    st.markdown("### Facility Remote Sensing Inspection")
    c_sel, p_sel = st.columns([2, 1])
    with c_sel:
        target_fac_name = st.selectbox("Select Target Facility for Satellite Plume Analysis:", facilities_df["facilityName"].tolist())
    with p_sel:
        prod_claimed = st.number_input("Declared Production (Tonnes)", min_value=10000.0, max_value=10000000.0, value=1000000.0, step=50000.0)

    target_row = facilities_df[facilities_df["facilityName"] == target_fac_name].iloc[0]
    fac_id = target_row["FacilityInspireId"]
    lat = float(target_row.get("latitude", target_row.get("Latitude", 0.0)))
    lon = float(target_row.get("longitude", target_row.get("Longitude", 0.0)))

    # Fetch observations
    obs_list = sat_client.get_facility_observations(fac_id, target_fac_name, lat, lon, year=2023)
    analysis = sat_analyzer.analyze_facility_plumes(obs_list, claimed_production_tonnes=prod_claimed)

    col_sm1, col_sm2, col_sm3, col_sm4 = st.columns(4)
    with col_sm1:
        st.metric("Plume Contrast Z-Score", f"+{analysis.plume_anomaly_zscore:.2f} σ", "Above Regional Background")
    with col_sm2:
        st.metric("Valid Clear-Sky Overpasses", f"{analysis.valid_clear_sky_overpasses} / {analysis.total_overpasses}", f"Mean Cloud: {analysis.mean_cloud_fraction*100:.1f}%")
    with col_sm3:
        st.metric("Operational State", analysis.operational_state_inference.split("(")[0].strip(), "Inferred Combustion State")
    with col_sm4:
        st.metric("Remote Sensing Verdict", analysis.consistency_verdict, "Signal Concordance")

    st.caption(f"🛰️ **Data Provenance:** `{analysis.data_source.upper()}` (ESA/Copernicus Sentinel-5P TROPOMI Level-2 tropospheric NO₂ OFFL product, range-read from planetary archive)")

    if obs_list:
        # Time series chart of facility column vs regional background
        obs_df = pd.DataFrame([
            {
                "Date": o.observation_date,
                "Facility Column (µmol/m²)": (o.tropospheric_column_density_mol_m2 * 1e6) if not np.isnan(o.tropospheric_column_density_mol_m2) else 0.0,
                "Regional Background (µmol/m²)": (o.regional_background_mol_m2 * 1e6) if not np.isnan(o.regional_background_mol_m2) else 0.0,
                "Cloud Fraction (%)": (o.cloud_fraction * 100.0) if not np.isnan(o.cloud_fraction) else 0.0,
                "Status": "Clear Sky (QA Valid)" if o.is_valid_qa else "Low QA / Cloud Obscured",
            }
            for o in obs_list
        ])

        fig_obs = go.Figure()
        fig_obs.add_trace(go.Bar(
            x=obs_df["Date"],
            y=obs_df["Facility Column (µmol/m²)"],
            name="Facility Plume Column (TROPOMI NO₂)",
            marker_color="#F59E0B",
        ))
        fig_obs.add_trace(go.Scatter(
            x=obs_df["Date"],
            y=obs_df["Regional Background (µmol/m²)"],
            name="Regional Background Baseline",
            line=dict(color="#3B82F6", width=2, dash="dash"),
        ))
        fig_obs.update_layout(
            title=f"2023 Sentinel-5P TROPOMI Tropospheric NO₂ Plume Density: {target_fac_name}",
            xaxis_title="Observation Date",
            yaxis_title="Tropospheric Column Density (µmol/m²)",
            height=340,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_obs, use_container_width=True)
    else:
        st.warning("No real satellite observations cached for this facility in 2023. Real data mode active: zero synthetic data generated.")

    if analysis.is_insufficient_evidence:
        st.warning(f"⚠️ **INSUFFICIENT REMOTE SENSING EVIDENCE:** {analysis.verdict_explanation}")
    else:
        st.info(f"🛰️ **OPERATIONAL ACTIVITY ASSESSMENT:** {analysis.verdict_explanation}")

# -------------------------------------------------------------
# TAB 6: BAYESIAN EVIDENCE FUSION
# -------------------------------------------------------------
elif menu == "6. Bayesian Evidence Fusion":
    st.markdown('<div class="main-title">Multimodal Probabilistic Evidence Fusion Simulator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Synthesis of observational satellite signals, multi-year temporal trends, and physical margins into calibrated risk posteriors and confidence scores</div>',
        unsafe_allow_html=True,
    )

    engine = ProbabilisticEvidenceFusionEngine()

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("#### Input Evidence Streams")
        stoich_margin_sigma = st.slider("Stoichiometric Safety Margin (Sigma above lower bound)", 0.0, 5.0, 1.2, 0.1)
        stoich_violated = st.checkbox("Simulate Stoichiometric Physical Floor Violation", False)

        has_satellite = st.checkbox("Include Copernicus Sentinel-5P Satellite Data", True)
        if has_satellite:
            sat_zscore = st.slider("Satellite Plume Anomaly Z-Score (vs Regional Background)", -2.0, 4.0, 1.8, 0.1)
            sat_cloud = st.slider("Satellite Cloud Obscuration Fraction", 0.0, 1.0, 0.25, 0.05)
        else:
            sat_zscore = None
            sat_cloud = 1.0

        has_temporal = st.checkbox("Include 5-Year Historical Time Series Baseline", True)
        if has_temporal:
            temp_zscore = st.slider("Sudden Emission Drop Anomaly (Z-Score)", 0.0, 4.0, 0.8, 0.1)
            years_hist = st.slider("Available Historical Reference Years", 1, 6, 5)
        else:
            temp_zscore = None
            years_hist = 0

        has_registry = st.checkbox("Include Registry Capacity Check", False)
        reg_ratio = st.slider("Claimed Production vs GEM Registry Capacity Ratio", 0.5, 1.5, 1.0, 0.05) if has_registry else 1.0

    ev = EvidenceInput(
        stoichiometric_discrepancy_sigma=stoich_margin_sigma,
        stoichiometric_violated=stoich_violated,
        satellite_plume_anomaly_zscore=sat_zscore,
        satellite_cloud_fraction=sat_cloud,
        temporal_variance_zscore=temp_zscore,
        years_reported_history=years_hist,
        registry_capacity_ratio=reg_ratio if has_registry else None,
    )

    decision = engine.fuse_evidence(ev, reported_emissions_tco2=800000, physical_min_tco2=750000)

    with col_e2:
        st.markdown("#### Probabilistic Decision Synthesis")
        
        # Display Outcome Card
        verdict_colors = {
            "Consistent": "✅ #22C55E",
            "Potential Inconsistency": "⚠️ #EAB308",
            "High Inconsistency Risk": "🚨 #EF4444",
            "Insufficient Evidence": "☁️ #64748B",
        }
        st.markdown(f"### Outcome: **{decision.audit_verdict}**")

        # Two Key Decoupled Metrics
        m_r, m_c = st.columns(2)
        m_r.metric("Inconsistency Risk P(H|E)", f"{decision.posterior_inconsistency_risk*100:.1f}%", "Signal Strength")
        m_c.metric("Evidence Confidence Score", f"{decision.evidence_confidence_score*100:.1f}%", "Observational Quality")

        # Gauge Chart for Inconsistency Risk
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=decision.posterior_inconsistency_risk * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Posterior Inconsistency Risk (%)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#1E293B"},
                    "steps": [
                        {"range": [0, 25], "color": "#86EFAC"},
                        {"range": [25, 70], "color": "#FDE047"},
                        {"range": [70, 100], "color": "#FCA5A5"},
                    ],
                },
            )
        )
        fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=35, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown(f"**95% Sensitivity Interval:** `[{decision.uncertainty_interval_95[0]*100:.1f}%, {decision.uncertainty_interval_95[1]*100:.1f}%]` (Monte Carlo propagated under LR uncertainty)")
        st.markdown(f"**Primary Contributing Evidence Driver:** `{decision.primary_driver}`")
        if decision.counterfactual_delta_tco2 > 0:
            st.markdown(f"**Counterfactual Feasibility Delta:** `+{decision.counterfactual_delta_tco2:,.0f} tCO₂` needed to resolve inconsistency.")
        st.info(decision.explanation_summary)

        with st.expander("📊 Prior Sensitivity & Robustness Analysis (Testing P(H) = 2% to 15%)"):
            sens = engine.evaluate_prior_sensitivity(ev, reported_emissions_tco2=800000, physical_min_tco2=750000)
            df_sens = pd.DataFrame([
                {"Base Prior P(H)": f"{p*100:.0f}%", "Posterior Risk P(H|E)": f"{r*100:.1f}%", "Verdict": "High Risk" if r >= 0.7 else ("Potential" if r >= 0.25 else "Consistent")}
                for p, r in sens.items()
            ])
            st.table(df_sens)
            st.caption("Demonstrates ranking stability under varying prior discrepancy assumptions (Critical Finding #6).")

# -------------------------------------------------------------
# TAB 7: 5-MODEL ABLATION & CALIBRATION BENCHMARK
# -------------------------------------------------------------
elif menu == "7. 5-Model Ablation & Calibration Benchmark":
    st.markdown('<div class="main-title">Controlled Empirical Evaluation: 5-Model Ablation & Calibration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Rigorous Comparative Benchmarking across 101 Controlled Cases (30 Baseline, 30 Physical, 30 Historical, 11 Route Misclassifications)</div>',
        unsafe_allow_html=True,
    )

    results_dir = Path(__file__).parents[2] / "experiments" / "results"
    summary_csv = results_dir / "ablation_study_summary.csv"
    calib_csv = results_dir / "calibration_comparison.csv"
    preds_parquet = results_dir / "calibrated_predictions_101.parquet"

    if summary_csv.exists():
        df_abl = pd.read_csv(summary_csv)
        
        # High-level metric highlights
        fused_row = df_abl[df_abl["model_name"].str.contains("Fused")].iloc[0]
        base_row = df_abl[df_abl["model_name"].str.contains("Baseline")].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Model E (Fused) F1-Score", f"{fused_row['f1_score']*100:.1f}%", f"+{(fused_row['f1_score'] - base_row['f1_score'])*100:.1f}% vs Baseline")
        with c2:
            st.metric("Model E False Positive Rate", f"{fused_row['fpr']*100:.2f}%", "-3.3% vs Baseline (Zero FP)")
        with c3:
            st.metric("Model E ROC-AUC", f"{fused_row['roc_auc']:.4f}", f"+{(fused_row['roc_auc'] - base_row['roc_auc']):.4f} Discrimination")
        with c4:
            st.metric("Model E Brier Score", f"{fused_row['brier_score']:.4f}", "Lowest Probability Error")

        st.markdown("### 1. 5-Model Quantitative Performance Comparison")
        st.dataframe(
            df_abl[["model_name", "precision", "recall", "f1_score", "fpr", "roc_auc", "pr_auc", "brier_score", "ece"]].style.format({
                "precision": "{:.3f}",
                "recall": "{:.3f}",
                "f1_score": "{:.3f}",
                "fpr": "{:.3f}",
                "roc_auc": "{:.4f}",
                "pr_auc": "{:.4f}",
                "brier_score": "{:.4f}",
                "ece": "{:.4f}",
            }).highlight_max(subset=["f1_score", "roc_auc", "pr_auc"], color="#DCFCE7")
            .highlight_min(subset=["fpr", "brier_score", "ece"], color="#DCFCE7"),
            use_container_width=True,
        )

        # Plotly comparison bar chart
        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(name="F1-Score", x=df_abl["model_name"], y=df_abl["f1_score"], marker_color="#3B82F6"))
        fig_bars.add_trace(go.Bar(name="ROC-AUC", x=df_abl["model_name"], y=df_abl["roc_auc"], marker_color="#10B981"))
        fig_bars.add_trace(go.Bar(name="Brier Score", x=df_abl["model_name"], y=df_abl["brier_score"], marker_color="#F59E0B"))
        fig_bars.update_layout(
            title="<b>Performance Metrics Across Single-Modality vs. Multimodal Fusion</b>",
            barmode="group",
            yaxis=dict(range=[0, 1.05], title="Metric Score"),
            template="plotly_white",
            height=380,
            margin=dict(l=20, r=20, t=50, b=30),
        )
        st.plotly_chart(fig_bars, use_container_width=True)

        st.markdown("### 2. Subgroup Detection Sensitivity by Anomaly Category")
        col_sg1, col_sg2 = st.columns(2)
        with col_sg1:
            st.markdown(
                """
                - **Physical Calcination / Reduction Violations (30 cases):**
                  - Model B (Stoichiometry Alone): **100.0% Detection**
                  - Model E (VeriCBAM Fused): **100.0% Detection**
                  - *Finding:* Chemical mass balances deterministically catch thermodynamic impossibilities.
                - **Historical Drop Anomalies (>3.5 Sigma Shift, 30 cases):**
                  - Model A (Baseline Intensity): 83.3%
                  - Model B (Stoichiometry Alone): 60.0%
                  - Model E (VeriCBAM Fused): **76.7% Detection** (Identifies subtle drops while preserving clean baselines)
                """
            )
        with col_sg2:
            st.markdown(
                """
                - **Route Misclassifications (BF-BOF declaring Scrap-EAF, 11 cases):**
                  - Model A (Baseline Intensity): **0.0%** (Fooled by secondary EAF benchmark!)
                  - Model B (Stoichiometry Alone): **0.0%** (EAF declared emissions are physically feasible for EAF!)
                  - Model E (VeriCBAM Fused): **100.0% Detection** (Registry & multi-source evidence exposes route mismatch!)
                - **Baseline Concordant Specificity (30 clean cases):**
                  - Model A: 96.7% (1 False Positive)
                  - Model E (VeriCBAM Fused): **100.0% (Zero False Positives)**
                """
            )

        st.markdown("---")
        st.markdown("### 3. Probability Calibration & Facility-Grouped Cross-Validation")
        st.markdown(
            "> **Methodological Note (Review Finding #10 & #12):** Calibration is evaluated against the controlled evaluation benchmark "
            "(101 cases constructed across 30 European industrial facilities). Because public datasets of real-world confirmed CBAM fraudulent declarations "
            "do not currently exist, real-world prevalence calibration remains a research limitation. Probability outputs represent calibrated likelihoods "
            "relative to the controlled benchmark under specified model assumptions."
        )

        col_cal1, col_cal2 = st.columns(2)
        with col_cal1:
            st.markdown("**Stratified 5-Fold Cross-Validation:**")
            if calib_csv.exists():
                df_cal = pd.read_csv(calib_csv)
                st.dataframe(
                    df_cal[["calibration_method", "brier_score", "ece", "log_loss", "f1_score", "roc_auc"]].style.format({
                        "brier_score": "{:.4f}",
                        "ece": "{:.4f}",
                        "log_loss": "{:.4f}",
                        "f1_score": "{:.3f}",
                        "roc_auc": "{:.4f}",
                    }).highlight_min(subset=["brier_score", "ece", "log_loss"], color="#DCFCE7"),
                    use_container_width=True,
                )

        grouped_csv = results_dir / "grouped_validation_summary.csv"
        with col_cal2:
            st.markdown("**Facility-Grouped Validation (`GroupKFold`, groups=`facility_id`):**")
            if grouped_csv.exists():
                df_grp = pd.read_csv(grouped_csv)
                st.dataframe(
                    df_grp[["calibration_method", "brier_score", "ece", "f1_score", "roc_auc"]].style.format({
                        "brier_score": "{:.4f}",
                        "ece": "{:.4f}",
                        "f1_score": "{:.3f}",
                        "roc_auc": "{:.4f}",
                    }).highlight_min(subset=["brier_score", "ece"], color="#DCFCE7"),
                    use_container_width=True,
                )
                st.caption("Holds out entire facilities across folds; verifies that calibration generalizes to unseen plants without facility data leakage.")

        if preds_parquet.exists():
            st.markdown("---")
            st.markdown("### 4. Interactive Benchmark Case Inspector (101 Controlled Cases)")
            df_preds = pd.read_parquet(preds_parquet)
            selected_ptype = st.selectbox(
                "Filter by Perturbation Type:",
                ["All Cases"] + sorted(df_preds["perturbation_type"].unique().tolist()),
            )
            filtered_df = df_preds if selected_ptype == "All Cases" else df_preds[df_preds["perturbation_type"] == selected_ptype]
            
            case_options = [f"{r['case_id']} | {r['facility_name']} ({r['perturbation_type']})" for _, r in filtered_df.iterrows()]
            selected_case_str = st.selectbox("Select Evaluation Case:", case_options)
            sel_case_id = selected_case_str.split(" | ")[0]
            case_row = filtered_df[filtered_df["case_id"] == sel_case_id].iloc[0]

            col_c1, col_c2, col_c3 = st.columns([1, 1, 1.2])
            with col_c1:
                st.markdown(f"**Facility:** {case_row['facility_name']}")
                st.markdown(f"**Sector:** {case_row['sector']} ({case_row['country']})")
                st.markdown(f"**Actual Route:** `{case_row['actual_technology_route'][:30]}`")
                st.markdown(f"**Declared Route:** `{case_row['declared_production_route']}`")
                st.markdown(f"**Benchmark Label:** `{'1 (Inconsistent)' if case_row['benchmark_label'] == 1 else '0 (Concordant)'}`")
            with col_c2:
                st.markdown(f"**Declared Production:** `{case_row['declared_production_tonnes']:,.0f} t`")
                st.markdown(f"**Declared CO₂:** `{case_row['declared_co2_tonnes']:,.0f} t`")
                st.markdown(f"**Declared Specific Emissions:** `{case_row['declared_specific_emissions']:.3f} tCO₂/t`")
                st.markdown(f"**Stoichiometric Bound:** `{case_row['stoich_lower_bound_tco2_per_t']:.3f} tCO₂/t`")
                st.markdown(f"**Satellite Z-Score:** `{case_row['satellite_zscore']:+.2f} σ`")
                st.markdown(f"**Historical Z-Score:** `{case_row['historical_zscore']:+.2f} σ`")
            with col_c3:
                st.markdown("**Predicted Inconsistency Probabilities:**")
                st.progress(float(case_row.get("prob_model_a", 0.0)), text=f"Model A (Baseline): {case_row.get('prob_model_a', 0.0)*100:.1f}%")
                st.progress(float(case_row.get("prob_model_b", 0.0)), text=f"Model B (Stoichiometry): {case_row.get('prob_model_b', 0.0)*100:.1f}%")
                st.progress(float(case_row.get("prob_model_c", 0.0)), text=f"Model C (Satellite): {case_row.get('prob_model_c', 0.0)*100:.1f}%")
                st.progress(float(case_row.get("prob_model_d", 0.0)), text=f"Model D (Historical): {case_row.get('prob_model_d', 0.0)*100:.1f}%")
                st.progress(float(case_row.get("prob_model_e", 0.0)), text=f"Model E (VeriCBAM Fused): {case_row.get('prob_model_e', 0.0)*100:.1f}%")
                if "prob_platt" in case_row:
                    st.progress(float(case_row["prob_platt"]), text=f"Model E (Platt Calibrated): {case_row['prob_platt']*100:.1f}%")

            st.info(f"**Scientific Rationale:** {case_row['scientific_rationale']}")

    else:
        st.warning("Ablation study summary not found. Run `python experiments/run_ablation_study.py` to generate results.")

# -------------------------------------------------------------
# TAB 8: PROPOSAL, REFERENCES & ROADMAP
# -------------------------------------------------------------
elif menu == "8. Capstone Proposal, References & Roadmap":
    st.markdown('<div class="main-title">Master Capstone Proposal & Academic Roadmap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">University of Europe for Applied Sciences (UE Germany) | Master of Science in Data Science</div>',
        unsafe_allow_html=True,
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("### Proposal Metadata")
        st.markdown(
            """
            - **Candidate:** Cristhian David Cáceres Mateus
            - **Study Program:** M.Sc. Data Science
            - **Academic Supervisor:** Dr. Humera Noor
            - **Working Title:** *VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment*
            - **Milestone 1 (Topic Approval):** October 12, 2026
            - **Milestone 2 (Proposal Approval):** October 26, 2026
            - **Form Status:** Completed (`admin/VeriCBAM_Capstone_Application_Form_Filled_v2.pdf`)
            """
        )
    with col_p2:
        st.markdown("### 6-Sprint Execution Timeline")
        st.markdown(
            """
            - **Sprint 1 (Weeks 1–2):** Authentic Empirical Data Ingestion (E-PRTR 30-plant cohort complete, GEM registries).
            - **Sprint 2 (Weeks 3–4):** Deterministic Stoichiometric Verification Engine (Cement calcination & Steel reduction mass balance).
            - **Sprint 3 (Weeks 5–6):** Satellite Plume Extraction (Copernicus Sentinel-5P real Level-2 tropospheric NO₂ overpasses).
            - **Sprint 4 (Weeks 7–8):** Probabilistic Evidence Fusion & Calibration ($P(\\text{Inconsistency}\\mid E)$).
            - **Sprint 5 (Weeks 9–10):** Streamlit Decision Support Interface & Counterfactual Audit Dossier Generator.
            - **Sprint 6 (Weeks 11–12):** Rigorous 5-Model Ablation Study & Thesis Defense Writing.
            """
        )

    st.markdown("### Scientific Maturity & Implementation Status (Review Alignment)")
    st.markdown(
        """
        | Component | Maturity Level | Data Provenance & Operational Nature |
        | :--- | :---: | :--- |
        | **Stoichiometric Models** | **Implemented** | EU BREF / IPCC Tier 3 chemical calcination and carbothermic iron reduction bounds. |
        | **30-Facility Cohort (Layer A)** | **Acquired & Processed** | 177 authentic annual records from EEA Industrial Reporting (E-PRTR / IED v16, 2018–2023). |
        | **Technology & Capacity Registry**| **Verified Real Data** | Real nameplate capacities & verified process routes from GEM Trackers and environmental permits. |
        | **Sentinel-5P EO Client** | **Real Data Pipeline** | 301 real overpasses extracted via Microsoft Planetary Computer STAC / HDF5 range reads (Zero synthetic fallback). |
        | **Controlled Evaluation Suite (Layer B)** | **Generated (101 Cases)** | Independent capacity benchmarks + Real Sentinel-5P observations + Exact Z-scores. |
        | **Probabilistic Evidence Fusion**| **Implemented Prototype** | Log-odds synthesis decoupling Inconsistency Risk from Evidence Confidence. |
        | **Streamlit Cockpit** | **Operational Prototype** | Interactive human verifier decision-support interface. |
        """
    )

    st.markdown("---")
    st.markdown("### 📚 Dedicated Academic & Regulatory Reference Bibliography")
    st.markdown(
        """
        1. **European Commission (2021):** *Commission Staff Working Document: Impact Assessment Report on CBAM*, **SWD(2021) 643 final**, Brussels.
           - *Key Empirical Data:* Section 6.6 & Annex 6 document MRV compliance costs, administrative authority budgets (€15M/yr), and installation audit burdens.
        2. **European Union (2023):** *Regulation (EU) 2023/956 establishing a carbon border adjustment mechanism*, Official Journal L 130/52.
           - *Key Statutory Basis:* Articles 8 & 9 mandate independent third-party verification and physical site visits.
        3. **European Commission (2025):** *CBAM Implementing Regulations*, Implementing Regulations (EU) 2025/2546 (verification rules), (EU) 2025/2551 (verifier accreditation), and (EU) 2025/2547 (calculation methodology).
           - *Key Constraint:* Defines ISO 14065 requirements and documents the global verifier deficit (~12,000 declarants vs ~403 accredited verifiers).
        4. **GMK Center (2024):** *CBAM Verification: Requirements, Costs and Industry Bottlenecks in the Steel Sector*, Kyiv/Brussels.
           - *Key Industry Findings:* Documents the €50,000–€150,000+ verification cost per site for integrated BF-BOF plants and verifier travel bottlenecks.
        5. **European Environment Agency (2026):** *EEA Industrial Reporting Database (E-PRTR / IED v16.0)*, Copenhagen. DOI: 10.2909/657ac3cb-affa-4295-a4a9-27b4f539adab.
           - *Empirical Cohort:* Source of the verified 30-facility industrial validation baseline (177 annual records, 2018–2023).
        6. **ERCST (2023):** *Implementation of the EU Carbon Border Adjustment Mechanism*, Brussels.
        7. **OECD (2023):** *Carbon-Related Border Adjustments and Developing Country Exporters*, OECD Publishing, Paris. DOI: 10.1787/5jlv2348-en.
        8. **European Commission Joint Research Centre (JRC) (2013 & 2022):** *BAT Reference Documents for Cement/Lime (2013) and Iron & Steel (2022)*, Seville.
           - *Stoichiometric Floor:* Calcination chemical floor ($0.510–0.525\text{ t }CO_2/\text{t clinker}$), BAT energy ($3,000\text{ MJ/t}$), and reduction floor ($1.182\text{ t }CO_2/\text{t iron}$).
        """
    )

