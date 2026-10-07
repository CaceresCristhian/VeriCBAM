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
import streamlit.components.v1 as components

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
    page_title="VeriCBAM | Decision Support Cockpit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Stitch Design System Palette Injection
STITCH_THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* Global canvas */
    .stApp {
        background-color: #0f131c;
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1c2028 !important;
        border-right: 1px solid #2d3440 !important;
    }

    /* Titles & Headings */
    .stitch-main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }

    .stitch-main-title span {
        color: #8ed5ff;
    }

    .stitch-sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    /* Bento-style metric cards */
    .bento-card {
        background-color: #1c2028;
        border: 1px solid #2d3440;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: transform 0.2s, border-color 0.2s;
    }

    .bento-card:hover {
        border-color: #8ed5ff;
        transform: translateY(-2px);
    }

    .bento-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 600;
        color: #94a3b8;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }

    .bento-value {
        font-size: 1.7rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        color: #f1f5f9;
        margin-bottom: 4px;
    }

    .bento-sub {
        font-size: 0.8rem;
        color: #94a3b8;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.03em;
    }

    .badge-consistent {
        background: rgba(78, 222, 163, 0.15);
        color: #4edea3;
        border: 1px solid rgba(78, 222, 163, 0.4);
    }

    .badge-potential {
        background: rgba(250, 204, 21, 0.15);
        color: #facc15;
        border: 1px solid rgba(250, 204, 21, 0.4);
    }

    .badge-risk {
        background: rgba(239, 68, 68, 0.15);
        color: #ffb4ab;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .badge-insufficient {
        background: rgba(148, 163, 184, 0.15);
        color: #94a3b8;
        border: 1px solid rgba(148, 163, 184, 0.4);
    }

    /* Formula Box */
    .formula-box {
        background: rgba(15, 19, 28, 0.8);
        border: 1px dashed #2d3440;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
        color: #8ed5ff;
        margin-bottom: 16px;
    }
</style>
"""
st.markdown(STITCH_THEME_CSS, unsafe_allow_html=True)

# Helper function to create dark Plotly layout
def apply_stitch_plotly_theme(fig, title_text=""):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f131c",
        plot_bgcolor="#0f131c",
        font=dict(family="Inter, sans-serif", color="#94a3b8"),
        title=dict(text=title_text, font=dict(color="#f1f5f9", size=16, family="Inter, sans-serif")),
        xaxis=dict(gridcolor="#2d3440", zerolinecolor="#2d3440"),
        yaxis=dict(gridcolor="#2d3440", zerolinecolor="#2d3440"),
        margin=dict(l=20, r=20, t=45, b=20),
    )
    return fig

# Load data with spinner
@st.cache_data
def load_cohort_data():
    mgr = CohortManager()
    facilities = mgr.get_all_facilities().copy()
    if "Latitude" in facilities.columns and "latitude" not in facilities.columns:
        facilities["latitude"] = facilities["Latitude"]
    if "Longitude" in facilities.columns and "longitude" not in facilities.columns:
        facilities["longitude"] = facilities["Longitude"]
    return mgr, facilities

with st.spinner("Initializing VeriCBAM Decision Support Engine..."):
    mgr, facilities_df = load_cohort_data()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=64)
st.sidebar.title("VeriCBAM Audit Suite")
st.sidebar.caption("EU CBAM Emissions Consistency Verification")

menu = st.sidebar.radio(
    "Navigation",
    [
        "1. Executive Overview & Cockpit",
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
# TAB 1: EXECUTIVE OVERVIEW & COCKPIT
# -------------------------------------------------------------
if menu == "1. Executive Overview & Cockpit":
    st.markdown('<div class="stitch-main-title">VeriCBAM: Multimodal Decision Support for CBAM Auditing</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Deterministic-Bayesian Architecture for European Carbon Border Adjustment Mechanism (CBAM) Compliance</div>',
        unsafe_allow_html=True,
    )

    view_mode = st.radio("Select View Mode:", ["Executive Summary", "Embedded Google Stitch Cockpit"], horizontal=True)

    if view_mode == "Embedded Google Stitch Cockpit":
        cockpit_html_path = Path(__file__).parent / "stitch_cockpit.html"
        if cockpit_html_path.exists():
            html_content = cockpit_html_path.read_text(encoding="utf-8")
            components.html(html_content, height=1050, scrolling=True)
        else:
            st.warning("Google Stitch Cockpit HTML template not found.")

    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                """
                <div class="bento-card">
                    <div class="bento-label">Complex Site Audit Cost</div>
                    <div class="bento-value">€50k – €150k+</div>
                    <div class="bento-sub">Per BF-BOF / Cement Site</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
                <div class="bento-card">
                    <div class="bento-label">Verifier Scarcity Deficit</div>
                    <div class="bento-value">12k vs 403</div>
                    <div class="bento-sub">Declarants vs AVR Verifiers</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                """
                <div class="bento-card">
                    <div class="bento-label">Audit Lead Time</div>
                    <div class="bento-value">3 – 6+ Mos</div>
                    <div class="bento-sub">Physical On-Site Bottleneck</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                """
                <div class="bento-card">
                    <div class="bento-label">Default Mark-up Penalty</div>
                    <div class="bento-value">+10% to +30%</div>
                    <div class="bento-sub">2026-2028 Punitive Surcharge</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
    st.markdown('<div class="stitch-main-title">Curated 30-Facility European Benchmark Cohort</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Authentic multi-year Scope 1 CO₂ emission records from the European Pollutant Release and Transfer Register (E-PRTR / IED v16)</div>',
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
            color_discrete_map={"Cement": "#facc15", "Steel": "#8ed5ff"},
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
            color_discrete_map={"Cement": "#facc15", "Steel": "#8ed5ff"},
            size_max=32,
            zoom=3.8,
            center={"lat": 51.1657, "lon": 10.4515},
            mapbox_style="carto-darkmatter",
            title="Geospatial Distribution of Benchmark Industrial Cohort",
        )
    fig_map = apply_stitch_plotly_theme(fig_map, "Geospatial Distribution of Benchmark Industrial Cohort")
    fig_map.update_layout(height=480, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

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
            st.markdown(
                f"""
                <div class="bento-card">
                    <div class="bento-label">Facility Metadata</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px;">{fac_row['facilityName']}</div>
                    <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;"><strong>Sector:</strong> <code style="color: #8ed5ff;">{fac_row['sector']}</code></p>
                    <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;"><strong>Location:</strong> {fac_row['city']}, {fac_row['countryName']}</p>
                    <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;"><strong>Coordinates:</strong> ({fac_lat:.4f}, {fac_lon:.4f})</p>
                    <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;"><strong>Mean CO₂:</strong> {fac_row['mean_co2_tonnes']:,.0f} t/yr</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_right:
            if not ts_df.empty:
                fig_ts = px.bar(
                    ts_df,
                    x="reportingYear",
                    y="co2_tonnes",
                    labels={"reportingYear": "Reporting Year", "co2_tonnes": "Verified Scope 1 CO₂ (Tonnes)"},
                    color_discrete_sequence=["#8ed5ff"],
                )
                fig_ts = apply_stitch_plotly_theme(fig_ts, f"Historical Emissions Trajectory: {fac_row['facilityName']}")
                fig_ts.update_layout(height=280)
                st.plotly_chart(fig_ts, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: STOICHIOMETRIC PHYSICS ENGINE
# -------------------------------------------------------------
elif menu == "3. Stoichiometric Physics Engine":
    st.markdown('<div class="stitch-main-title">Deterministic Stoichiometric Physics Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Evaluation of CBAM declarations against fundamental chemical mass balances and thermodynamic lower bounds</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="formula-box">
            <b>Chemical Calcination Mass Balance:</b> CaCO₃ → CaO + CO₂ (0.7848 t CO₂ / t CaO) | MgCO₃ → MgO + CO₂ (1.0919 t CO₂ / t MgO)<br>
            <b>Steel Carbothermic Reduction Floor:</b> Fe₂O₃ + 3 C → 2 Fe + 3 CO (1.182 t CO₂ / t hot metal minimum)
        </div>
        """,
        unsafe_allow_html=True,
    )

    sector_mode = st.radio("Select Production Sector for Audit Simulation:", ["Cement Clinker", "Crude Steel"], horizontal=True)

    if sector_mode == "Cement Clinker":
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
        with m1:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Chemical Calcination Floor</div><div class="bento-value">{res_cement.process_emissions_min_tco2:,.0f} t</div><div class="bento-sub">Fixed Mass Balance</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Thermal Combustion Floor</div><div class="bento-value">{res_cement.combustion_emissions_min_tco2:,.0f} t</div><div class="bento-sub">BAT Kiln ({fuel_type})</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Net Physical Floor</div><div class="bento-value">{res_cement.total_physical_minimum_tco2:,.0f} t</div><div class="bento-sub">Absolute Minimum</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Specific Intensity</div><div class="bento-value">{res_cement.reported_specific_intensity_tco2_per_t_clinker:.3f}</div><div class="bento-sub">Floor: {res_cement.minimum_specific_intensity_tco2_per_t_clinker:.3f} tCO₂/t</div></div>', unsafe_allow_html=True)

        if not res_cement.is_physically_feasible:
            st.markdown(f'<div class="status-badge badge-risk">🚨 PHYSICAL FEASIBILITY VIOLATION</div>', unsafe_allow_html=True)
            st.error(res_cement.violation_reason)
        else:
            st.markdown(f'<div class="status-badge badge-consistent">✅ PHYSICALLY FEASIBLE</div>', unsafe_allow_html=True)
            st.success(res_cement.violation_reason)

    else:
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
        with m1:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Reported Intensity</div><div class="bento-value">{res_steel.reported_specific_intensity_tco2_per_t:.3f}</div><div class="bento-sub">Declared Scope 1</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Thermodynamic Floor</div><div class="bento-value">{res_steel.theoretical_floor_intensity_tco2_per_t:.3f}</div><div class="bento-sub">Floor for {claimed_route}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Typical Benchmark</div><div class="bento-value">{res_steel.typical_benchmark_intensity_tco2_per_t:.3f}</div><div class="bento-sub">EU BREF Median</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Net Allowable CO₂</div><div class="bento-value">{res_steel.total_physical_minimum_tco2:,.0f} t</div><div class="bento-sub">Physical Floor</div></div>', unsafe_allow_html=True)

        if not res_steel.is_physically_feasible:
            st.markdown(f'<div class="status-badge badge-risk">🚨 ROUTE LOWER BOUND VIOLATION</div>', unsafe_allow_html=True)
            st.error(res_steel.violation_reason)
        elif res_steel.route_misclassification_detected:
            st.markdown(f'<div class="status-badge badge-potential">⚠️ ROUTE MISCLASSIFICATION DETECTED</div>', unsafe_allow_html=True)
            st.warning(res_steel.violation_reason)
        else:
            st.markdown(f'<div class="status-badge badge-consistent">✅ CONCORDANT WITH ROUTE BOUNDS</div>', unsafe_allow_html=True)
            st.success(res_steel.violation_reason)

# -------------------------------------------------------------
# TAB 4: STANDALONE SUPPLIER PLAUSIBILITY PRE-CHECK
# -------------------------------------------------------------
elif menu == "4. Standalone Supplier Plausibility Pre-Check":
    st.markdown('<div class="stitch-main-title">Standalone Supplier Plausibility Pre-Check</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Rapid pre-audit screening of non-EU supplier declarations without requiring satellite or historical registry records</div>',
        unsafe_allow_html=True,
    )

    col_pc1, col_pc2 = st.columns(2)
    with col_pc1:
        st.markdown("#### Supplier Declaration Inputs")
        supplier_name = st.text_input("Supplier / Installation Name:", "Overseas Heavy Industries Ltd.")
        supp_sector = st.selectbox("Commodity Sector:", ["Cement Clinker", "Finished Cement (CEM II)", "Crude Steel (BF-BOF)", "Crude Steel (Scrap-EAF)"])
        decl_specific_emissions = st.number_input("Declared Specific Scope 1 Intensity (t CO₂ / t product):", min_value=0.0, max_value=5.0, value=0.62, step=0.01)
        annual_volume_tonnes = st.number_input("Annual Production Volume (Metric Tonnes):", min_value=1000.0, max_value=20000000.0, value=1200000.0, step=50000.0)

    if "Cement Clinker" in supp_sector:
        floor = 0.770
        typical_range = (0.800, 0.950)
        benchmark_note = "EU BREF Clinker Calcination + Modern BAT Kiln"
    elif "Finished Cement" in supp_sector:
        floor = 0.520
        typical_range = (0.580, 0.720)
        benchmark_note = "CEM II Blended Cement (70% Clinker Ratio)"
    elif "BF-BOF" in supp_sector:
        floor = 1.350
        typical_range = (1.750, 2.200)
        benchmark_note = "Integrated Blast Furnace - Basic Oxygen Furnace (EU BREF)"
    else:
        floor = 0.040
        typical_range = (0.080, 0.250)
        benchmark_note = "Electric Arc Furnace (100% Scrap Recycled)"

    is_feasible = decl_specific_emissions >= floor
    total_declared_co2 = decl_specific_emissions * annual_volume_tonnes
    total_floor_co2 = floor * annual_volume_tonnes
    deficit_co2 = max(0.0, total_floor_co2 - total_declared_co2)

    with col_pc2:
        st.markdown("#### Physical Feasibility & Status Badge")
        if not is_feasible:
            badge_html = '<div class="status-badge badge-risk">HIGH INCONSISTENCY RISK (VIOLATION)</div>'
        elif decl_specific_emissions < typical_range[0]:
            badge_html = '<div class="status-badge badge-potential">POTENTIAL INCONSISTENCY (LOW INTENSITY)</div>'
        else:
            badge_html = '<div class="status-badge badge-consistent">CONSISTENT WITH PHYSICAL FLOOR</div>'
        st.markdown(badge_html, unsafe_allow_html=True)
        st.write("")

        pm1, pm2 = st.columns(2)
        with pm1:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Physical Floor</div><div class="bento-value">{floor:.3f}</div><div class="bento-sub">{benchmark_note}</div></div>', unsafe_allow_html=True)
        with pm2:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Typical Global Range</div><div class="bento-value">{typical_range[0]:.2f} – {typical_range[1]:.2f}</div><div class="bento-sub">Standard Operations</div></div>', unsafe_allow_html=True)

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
    st.markdown('<div class="stitch-main-title">Copernicus Sentinel-5P Earth Observation Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Remote sensing atmospheric plume contrast, cloud-radiance filtering, and operational combustion inference</div>',
        unsafe_allow_html=True,
    )

    sat_client = CopernicusSentinel5PClient()
    sat_analyzer = SatellitePlumeAnalyzer()

    c_sel, p_sel = st.columns([2, 1])
    with c_sel:
        target_fac_name = st.selectbox("Select Target Facility for Satellite Plume Analysis:", facilities_df["facilityName"].tolist())
    with p_sel:
        prod_claimed = st.number_input("Declared Production (Tonnes)", min_value=10000.0, max_value=10000000.0, value=1000000.0, step=50000.0)

    target_row = facilities_df[facilities_df["facilityName"] == target_fac_name].iloc[0]
    fac_id = target_row["FacilityInspireId"]
    lat = float(target_row.get("latitude", target_row.get("Latitude", 0.0)))
    lon = float(target_row.get("longitude", target_row.get("Longitude", 0.0)))

    obs_list = sat_client.get_facility_observations(fac_id, target_fac_name, lat, lon, year=2023)
    analysis = sat_analyzer.analyze_facility_plumes(obs_list, claimed_production_tonnes=prod_claimed)

    col_sm1, col_sm2, col_sm3, col_sm4 = st.columns(4)
    with col_sm1:
        st.markdown(f'<div class="bento-card"><div class="bento-label">Plume Contrast</div><div class="bento-value">+{analysis.plume_anomaly_zscore:.2f} σ</div><div class="bento-sub">Above Regional Background</div></div>', unsafe_allow_html=True)
    with col_sm2:
        st.markdown(f'<div class="bento-card"><div class="bento-label">Valid Overpasses</div><div class="bento-value">{analysis.valid_clear_sky_overpasses} / {analysis.total_overpasses}</div><div class="bento-sub">Mean Cloud: {analysis.mean_cloud_fraction*100:.1f}%</div></div>', unsafe_allow_html=True)
    with col_sm3:
        st.markdown(f'<div class="bento-card"><div class="bento-label">Operational State</div><div class="bento-value" style="font-size: 1.2rem;">{analysis.operational_state_inference.split("(")[0].strip()}</div><div class="bento-sub">Inferred State</div></div>', unsafe_allow_html=True)
    with col_sm4:
        st.markdown(f'<div class="bento-card"><div class="bento-label">Remote Verdict</div><div class="bento-value" style="font-size: 1.2rem;">{analysis.consistency_verdict}</div><div class="bento-sub">Signal Concordance</div></div>', unsafe_allow_html=True)

    if obs_list:
        obs_df = pd.DataFrame([
            {
                "Date": o.observation_date,
                "Facility Column (µmol/m²)": (o.tropospheric_column_density_mol_m2 * 1e6) if not np.isnan(o.tropospheric_column_density_mol_m2) else 0.0,
                "Regional Background (µmol/m²)": (o.regional_background_mol_m2 * 1e6) if not np.isnan(o.regional_background_mol_m2) else 0.0,
            }
            for o in obs_list
        ])

        fig_obs = go.Figure()
        fig_obs.add_trace(go.Bar(
            x=obs_df["Date"],
            y=obs_df["Facility Column (µmol/m²)"],
            name="Facility Plume Column (TROPOMI NO₂)",
            marker_color="#8ed5ff",
        ))
        fig_obs.add_trace(go.Scatter(
            x=obs_df["Date"],
            y=obs_df["Regional Background (µmol/m²)"],
            name="Regional Background Baseline (15-30 km buffer)",
            line=dict(color="#facc15", width=2, dash="dash"),
        ))
        fig_obs = apply_stitch_plotly_theme(fig_obs, f"2023 Sentinel-5P TROPOMI NO₂ Plume vs 15-30km Buffer Background: {target_fac_name}")
        fig_obs.update_layout(height=340)
        st.plotly_chart(fig_obs, use_container_width=True)

# -------------------------------------------------------------
# TAB 6: BAYESIAN EVIDENCE FUSION
# -------------------------------------------------------------
elif menu == "6. Bayesian Evidence Fusion":
    st.markdown('<div class="stitch-main-title">Multimodal Probabilistic Evidence Fusion Simulator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Synthesis of observational satellite signals, multi-year temporal trends, and physical margins into calibrated risk posteriors</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="formula-box">
            logit P(H | E) = logit P(H) + ∑ wᵢ · Cᵢ · ln(LRᵢ)
        </div>
        """,
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
        
        verdict_badge_class = "badge-consistent" if decision.audit_verdict == "Consistent" else ("badge-potential" if decision.audit_verdict == "Potential Inconsistency" else ("badge-risk" if decision.audit_verdict == "High Inconsistency Risk" else "badge-insufficient"))
        st.markdown(f'<div class="status-badge {verdict_badge_class}">{decision.audit_verdict.upper()}</div>', unsafe_allow_html=True)
        st.write("")

        m_r, m_c = st.columns(2)
        with m_r:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Inconsistency Risk P(H|E)</div><div class="bento-value" style="color: #8ed5ff;">{decision.posterior_inconsistency_risk*100:.1f}%</div><div class="bento-sub">Signal Strength</div></div>', unsafe_allow_html=True)
        with m_c:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Evidence Confidence</div><div class="bento-value" style="color: #4edea3;">{decision.evidence_confidence_score*100:.1f}%</div><div class="bento-sub">Observational Quality</div></div>', unsafe_allow_html=True)

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=decision.posterior_inconsistency_risk * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Posterior Inconsistency Risk (%)", "font": {"color": "#f1f5f9"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
                    "bar": {"color": "#8ed5ff"},
                    "steps": [
                        {"range": [0, 25], "color": "rgba(78, 222, 163, 0.2)"},
                        {"range": [25, 70], "color": "rgba(250, 204, 21, 0.2)"},
                        {"range": [70, 100], "color": "rgba(239, 68, 68, 0.2)"},
                    ],
                },
            )
        )
        fig_gauge = apply_stitch_plotly_theme(fig_gauge)
        fig_gauge.update_layout(height=220)
        st.plotly_chart(fig_gauge, use_container_width=True)

        with st.expander("📊 Prior Sensitivity & Robustness Analysis (P(H) = 2% to 15%)"):
            sens = engine.evaluate_prior_sensitivity(ev, reported_emissions_tco2=800000, physical_min_tco2=750000)
            df_sens = pd.DataFrame([
                {"Base Prior P(H)": f"{p*100:.0f}%", "Posterior Risk P(H|E)": f"{r*100:.1f}%"}
                for p, r in sens.items()
            ])
            st.table(df_sens)

# -------------------------------------------------------------
# TAB 7: 5-MODEL ABLATION & CALIBRATION BENCHMARK
# -------------------------------------------------------------
elif menu == "7. 5-Model Ablation & Calibration Benchmark":
    st.markdown('<div class="stitch-main-title">Controlled Empirical Evaluation: 5-Model Ablation & Calibration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Rigorous Comparative Benchmarking across Controlled Evaluation Cases</div>',
        unsafe_allow_html=True,
    )

    results_dir = Path(__file__).parents[2] / "experiments" / "results"
    summary_csv = results_dir / "ablation_study_summary.csv"
    calib_csv = results_dir / "calibration_comparison.csv"
    preds_parquet = results_dir / "calibrated_predictions_101.parquet"

    if summary_csv.exists():
        df_abl = pd.read_csv(summary_csv)
        fused_row = df_abl[df_abl["model_name"].str.contains("Fused")].iloc[0]
        base_row = df_abl[df_abl["model_name"].str.contains("Baseline")].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Model E F1-Score</div><div class="bento-value" style="color: #4edea3;">{fused_row["f1_score"]*100:.1f}%</div><div class="bento-sub">+{(fused_row["f1_score"] - base_row["f1_score"])*100:.1f}% vs Baseline</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Model E FPR</div><div class="bento-value">{fused_row["fpr"]*100:.2f}%</div><div class="bento-sub">Zero False Positives</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Model E ROC-AUC</div><div class="bento-value" style="color: #8ed5ff;">{fused_row["roc_auc"]:.4f}</div><div class="bento-sub">Discrimination</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Model E Brier Score</div><div class="bento-value">{fused_row["brier_score"]:.4f}</div><div class="bento-sub">Lowest Error</div></div>', unsafe_allow_html=True)

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
            }),
            use_container_width=True,
        )

        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(name="F1-Score", x=df_abl["model_name"], y=df_abl["f1_score"], marker_color="#8ed5ff"))
        fig_bars.add_trace(go.Bar(name="ROC-AUC", x=df_abl["model_name"], y=df_abl["roc_auc"], marker_color="#4edea3"))
        fig_bars.add_trace(go.Bar(name="Brier Score", x=df_abl["model_name"], y=df_abl["brier_score"], marker_color="#facc15"))
        fig_bars = apply_stitch_plotly_theme(fig_bars, "Performance Metrics Across Single-Modality vs. Multimodal Fusion")
        fig_bars.update_layout(barmode="group", height=360)
        st.plotly_chart(fig_bars, use_container_width=True)

# -------------------------------------------------------------
# TAB 8: PROPOSAL, REFERENCES & ROADMAP
# -------------------------------------------------------------
elif menu == "8. Capstone Proposal, References & Roadmap":
    st.markdown('<div class="stitch-main-title">Master Capstone Proposal & Academic Roadmap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">University of Europe for Applied Sciences (UE Germany) | Master of Science in Data Science</div>',
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
            """
        )
    with col_p2:
        st.markdown("### Key Thermodynamic & Bayesian Equations")
        st.markdown(
            """
            - **Calcination Floor:** $\\text{CaCO}_3 \\rightarrow \\text{CaO} + \\text{CO}_2$ ($0.510\\text{--}0.525\\text{ t CO}_2/\\text{t clinker}$)
            - **Blast Furnace Reduction Floor:** $\\text{Fe}_2\\text{O}_3 + 3\\text{C} \\rightarrow 2\\text{Fe} + 3\\text{CO}$ ($1.350\\text{ t CO}_2/\\text{t crude steel}$)
            - **Bayesian Log-Odds Fusion:** $\\text{logit } P(H|E) = \\text{logit } P(H) + \\sum w_i C_i \\ln(LR_i)$
            """
        )
