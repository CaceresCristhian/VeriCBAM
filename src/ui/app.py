"""
VeriCBAM - Multimodal Decision Support System for CBAM Emissions Auditing
Master Capstone Interactive Dashboard (Tier A Improved)
University of Europe for Applied Sciences (UE Germany)
Master of Science in Data Science | Cristhian David Caceres Mateus
Supervisor: Dr. Humera Noor
"""

import html
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

# Stitch Design System Palette Injection (High-Contrast WCAG-Compliant Offline Theme)
STITCH_THEME_CSS = """
<style>
    /* Global canvas & typography */
    .stApp {
        background-color: #0f131c !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li {
        color: #f1f5f9;
    }

    /* Sidebar container */
    section[data-testid="stSidebar"], [data-testid="stSidebar"] {
        background-color: #161922 !important;
        border-right: 1px solid #2d3440 !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #161922 !important;
    }

    /* Sidebar Header & Brand typography */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] caption {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    /* Sidebar Radio Navigation */
    section[data-testid="stSidebar"] [data-testid="stRadio"] > label,
    section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-testid="stWidgetLabel"] p {
        color: #8ed5ff !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        margin-bottom: 8px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 4px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: rgba(28, 32, 40, 0.7) !important;
        border: 1px solid rgba(45, 52, 64, 0.8) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin-bottom: 4px !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p,
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label span,
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label div {
        color: #f1f5f9 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        line-height: 1.35 !important;
    }

    /* Sidebar Radio Hover */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background-color: rgba(142, 213, 255, 0.12) !important;
        border-color: rgba(142, 213, 255, 0.45) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover p {
        color: #8ed5ff !important;
    }

    /* Sidebar Radio Selected / Active */
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] {
        background-color: rgba(142, 213, 255, 0.18) !important;
        border: 1px solid #8ed5ff !important;
        border-left: 4px solid #8ed5ff !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Sidebar Student / Metadata Card */
    .sidebar-student-box {
        background: rgba(28, 32, 40, 0.95);
        border: 1px solid rgba(142, 213, 255, 0.35);
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 20px;
        font-size: 0.82rem;
        line-height: 1.6;
    }
    .sidebar-student-box .box-label {
        color: #8ed5ff !important;
        font-weight: 600;
    }
    .sidebar-student-box .box-val {
        color: #ffffff !important;
        font-weight: 500;
    }

    /* Main canvas widget labels (Select View Mode, dropdowns, sliders) */
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.94rem !important;
    }
    [data-testid="stRadio"] > label p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    /* Main canvas radio group controls */
    .stApp div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] div[data-testid="stRadio"]) div[role="radiogroup"] label {
        background-color: rgba(28, 32, 40, 0.7) !important;
        border: 1px solid rgba(45, 52, 64, 0.8) !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        transition: all 0.2s ease !important;
    }
    .stApp div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] div[data-testid="stRadio"]) div[role="radiogroup"] label p {
        color: #f1f5f9 !important;
        font-size: 0.90rem !important;
        font-weight: 500 !important;
    }
    .stApp div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] div[data-testid="stRadio"]) div[role="radiogroup"] label:hover {
        border-color: #8ed5ff !important;
        background-color: rgba(142, 213, 255, 0.1) !important;
    }
    .stApp div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] div[data-testid="stRadio"]) div[role="radiogroup"] label:hover p {
        color: #8ed5ff !important;
    }
    .stApp div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] div[data-testid="stRadio"]) div[role="radiogroup"] label:has(input:checked) {
        border-color: #8ed5ff !important;
        background-color: rgba(142, 213, 255, 0.18) !important;
    }
    .stApp div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] div[data-testid="stRadio"]) div[role="radiogroup"] label:has(input:checked) p {
        color: #ffffff !important;
        font-weight: 700 !important;
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
        color: #cbd5e1;
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
        font-size: 0.78rem;
        text-transform: uppercase;
        font-weight: 700;
        color: #cbd5e1 !important;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }

    .bento-value {
        font-size: 1.65rem;
        font-weight: 700;
        font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        color: #ffffff !important;
        margin-bottom: 4px;
    }

    .bento-sub {
        font-size: 0.82rem;
        color: #94a3b8 !important;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
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
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.4);
    }

    /* Formula Box */
    .formula-box {
        background: rgba(15, 19, 28, 0.8);
        border: 1px dashed #2d3440;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        font-size: 0.88rem;
        color: #8ed5ff;
        margin-bottom: 16px;
    }

    /* Expanders */
    [data-testid="stExpander"] details {
        background-color: #1c2028 !important;
        border: 1px solid #2d3440 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
    }
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #8ed5ff !important;
        border-color: #8ed5ff !important;
        background-color: rgba(142, 213, 255, 0.08) !important;
    }
    [data-testid="stExpander"] summary:hover p {
        color: #8ed5ff !important;
    }
    [data-testid="stExpander"] div[role="region"] {
        background-color: #141822 !important;
        border-top: 1px solid #2d3440 !important;
        color: #f1f5f9 !important;
    }

    /* Alert / Banner Boxes */
    [data-testid="stAlert"] {
        border-radius: 8px !important;
        border-width: 1px !important;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] strong,
    [data-testid="stAlert"] div {
        color: #f8fafc !important;
    }

    /* Inputs, Selectboxes, Sliders */
    div[data-baseweb="select"] > div {
        background-color: #161922 !important;
        border-color: #3b4252 !important;
        color: #f1f5f9 !important;
    }
    div[data-baseweb="select"] span {
        color: #f1f5f9 !important;
    }
    div[data-baseweb="input"] > input {
        background-color: #161922 !important;
        border-color: #3b4252 !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stSlider"] label p {
        color: #e2e8f0 !important;
    }
</style>
"""
st.markdown(STITCH_THEME_CSS, unsafe_allow_html=True)


def scope_banner():
    """Renders the standard scope and screening boundary banner required on all pages."""
    st.info(
        "🛡️ **VeriCBAM Verification Scope & Screening Boundary:** "
        "Plant-level consistency screening evaluated on a controlled empirical benchmark. "
        "Functions as decision-support for accredited verifiers under Commission Delegated Regulation (EU) 2025/2551. "
        "Not an autonomous legal compliance certification."
    )


def apply_stitch_plotly_theme(fig, title_text=""):
    """Helper function to create dark Plotly layout with offline system fonts."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f131c",
        plot_bgcolor="#0f131c",
        font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", color="#94a3b8"),
        title=dict(text=title_text, font=dict(color="#f1f5f9", size=16)),
        xaxis=dict(gridcolor="#2d3440", zerolinecolor="#2d3440"),
        yaxis=dict(gridcolor="#2d3440", zerolinecolor="#2d3440"),
        margin=dict(l=20, r=20, t=45, b=20),
    )
    return fig


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

# Sidebar Navigation (Local Glyph, Clean Architecture)
st.sidebar.markdown("### 🛡️ VeriCBAM Audit Suite")
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
        "7. Empirical Benchmark Evaluation & Ablation",
        "8. Capstone Proposal, References & Roadmap",
    ],
)

st.sidebar.markdown(
    """
    <div class="sidebar-student-box">
        <div><span class="box-label">Student:</span> <span class="box-val">Cristhian David Cáceres Mateus</span></div>
        <div><span class="box-label">Program:</span> <span class="box-val">M.Sc. Data Science</span></div>
        <div><span class="box-label">University:</span> <span class="box-val">UE Germany (Berlin)</span></div>
        <div><span class="box-label">Supervisor:</span> <span class="box-val">Dr. Humera Noor</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW & COCKPIT
# -------------------------------------------------------------
if menu == "1. Executive Overview & Cockpit":
    scope_banner()
    st.markdown('<div class="stitch-main-title">VeriCBAM: Multimodal Decision Support for CBAM Auditing</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Deterministic-Bayesian Architecture for European Carbon Border Adjustment Mechanism (CBAM) Consistency Screening</div>',
        unsafe_allow_html=True,
    )

    view_mode = st.radio("Select View Mode:", ["Executive Summary", "Embedded Regulatory Cockpit"], horizontal=True)

    if view_mode == "Embedded Regulatory Cockpit":
        cockpit_html_path = Path(__file__).parent / "stitch_cockpit.html"
        if cockpit_html_path.exists():
            html_content = cockpit_html_path.read_text(encoding="utf-8")
            components.html(html_content, height=1050, scrolling=True)
        else:
            st.warning("Regulatory Cockpit HTML template not found.")

    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                """
                <div class="bento-card">
                    <div class="bento-label">Benchmark Cohort</div>
                    <div class="bento-value">30 Sites</div>
                    <div class="bento-sub">15 Cement • 15 Steel</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
                <div class="bento-card">
                    <div class="bento-label">Authentic Panel</div>
                    <div class="bento-value">177 Plant-Yrs</div>
                    <div class="bento-sub">2018–2023 Real Negatives</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                """
                <div class="bento-card">
                    <div class="bento-label">Graded Benchmark</div>
                    <div class="bento-value">325 Cases</div>
                    <div class="bento-sub">177 Real Neg. • 148 Inconsistencies</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                """
                <div class="bento-card">
                    <div class="bento-label">Evidence Modalities</div>
                    <div class="bento-value">5 Streams</div>
                    <div class="bento-sub">Physics, Sat, Hist, NOx, Reg</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("### The Regulatory Mandate: Verification Decision Support")
        st.markdown(
            """
            Under **Regulation (EU) 2023/956**, **Commission Implementing Regulation (EU) 2025/2546** (verification rules),
            **Commission Delegated Regulation (EU) 2025/2551** (verifier accreditation), and **Commission Implementing Regulation (EU) 2025/2547**
            (calculation of embedded emissions), EU importers of heavy industrial commodities (**Cement and Steel**)
            reporting actual emissions must undergo independent verification by accredited verification bodies.

            Physical on-site inspections serve as the regulatory baseline for complex installations. VeriCBAM provides
            an open, mathematically grounded screening co-pilot that flags declarations violating stoichiometric lower bounds,
            exhibiting severe historical drops, or contradicting verified technology registries, allowing verifiers to prioritize
            audit resources objectively.
            """
        )

        with st.expander("📚 View Supporting Regulatory & Academic Frameworks"):
            st.markdown(
                """
                - **Regulation (EU) 2023/956:** Establishing a carbon border adjustment mechanism (Articles 8 & 9).
                - **Commission Implementing Regulation (EU) 2025/2546:** Rules for verification of CBAM declarations. [ELI Link](http://data.europa.eu/eli/reg_impl/2025/2546/oj)
                - **Commission Delegated Regulation (EU) 2025/2551:** Rules for accreditation and oversight of verifiers. [ELI Link](http://data.europa.eu/eli/reg_del/2025/2551/oj)
                - **Commission Implementing Regulation (EU) 2025/2547:** Rules for calculation of embedded direct and indirect emissions. [ELI Link](http://data.europa.eu/eli/reg_impl/2025/2547/oj)
                - **European Environment Agency (2026):** *EEA Industrial Reporting Database (E-PRTR / IED v16)* (Authentic baseline reference panel).
                """
            )

# -------------------------------------------------------------
# TAB 2: BENCHMARK COHORT
# -------------------------------------------------------------
elif menu == "2. 30-Facility Benchmark Cohort":
    scope_banner()
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
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px;">{html.escape(str(fac_row['facilityName']))}</div>
                    <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;"><strong>Sector:</strong> <code style="color: #8ed5ff;">{html.escape(str(fac_row['sector']))}</code></p>
                    <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;"><strong>Location:</strong> {html.escape(str(fac_row['city']))}, {html.escape(str(fac_row['countryName']))}</p>
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
                fig_ts = apply_stitch_plotly_theme(fig_ts, f"Historical Emissions Trajectory: {html.escape(str(fac_row['facilityName']))}")
                fig_ts.update_layout(height=280)
                st.plotly_chart(fig_ts, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: STOICHIOMETRIC PHYSICS ENGINE
# -------------------------------------------------------------
elif menu == "3. Stoichiometric Physics Engine":
    scope_banner()
    st.markdown('<div class="stitch-main-title">Deterministic Stoichiometric Physics Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Evaluation of CBAM declarations against chemical mass balances and route-specific engineering lower bounds</div>',
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
            st.markdown(f'<div class="bento-card"><div class="bento-label">Thermal Combustion Floor</div><div class="bento-value">{res_cement.combustion_emissions_min_tco2:,.0f} t</div><div class="bento-sub">BAT Kiln ({html.escape(str(fuel_type))})</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Net Physical Floor</div><div class="bento-value">{res_cement.total_physical_minimum_tco2:,.0f} t</div><div class="bento-sub">Stoichiometric Minimum</div></div>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="bento-card"><div class="bento-label">Stoichiometric Floor</div><div class="bento-value">{res_steel.theoretical_floor_intensity_tco2_per_t:.3f}</div><div class="bento-sub">Floor for {html.escape(str(claimed_route))}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Typical Benchmark</div><div class="bento-value">{res_steel.typical_benchmark_intensity_tco2_per_t:.3f}</div><div class="bento-sub">EU BREF Median</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Net Allowable CO₂</div><div class="bento-value">{res_steel.total_physical_minimum_tco2:,.0f} t</div><div class="bento-sub">Engineering Bound</div></div>', unsafe_allow_html=True)

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
    scope_banner()
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
            st.markdown(f'<div class="bento-card"><div class="bento-label">Physical Lower Bound</div><div class="bento-value">{floor:.3f}</div><div class="bento-sub">{html.escape(benchmark_note)}</div></div>', unsafe_allow_html=True)
        with pm2:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Typical Global Range</div><div class="bento-value">{typical_range[0]:.2f} – {typical_range[1]:.2f}</div><div class="bento-sub">Standard Operations</div></div>', unsafe_allow_html=True)

        dossier_text = f"""# VeriCBAM Pre-Audit Screening Dossier
Installation: {supplier_name}
Commodity: {supp_sector}
Declared Specific Intensity: {decl_specific_emissions:.3f} t CO2/t product
Declared Annual Production: {annual_volume_tonnes:,.0f} tonnes
Total Declared Scope 1: {total_declared_co2:,.0f} t CO2
Stoichiometric Lower Bound: {floor:.3f} t CO2/t ({total_floor_co2:,.0f} t CO2 total)
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
    scope_banner()
    st.markdown('<div class="stitch-main-title">Copernicus Sentinel-5P Earth Observation Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Remote sensing atmospheric plume contrast, cloud-radiance filtering, and auxiliary combustion inference</div>',
        unsafe_allow_html=True,
    )

    st.caption("ℹ️ **Scientific Status (Inconclusive / Underpowered Pilot Evidence):** Multi-year analysis (2019–2023) indicates that Sentinel-5P tropospheric NO₂ column density is not a reliable quantitative proxy for annual plant-level CO₂ (mean within-plant Spearman ρ = -0.100). Orbital remote sensing is strictly designated as an auxiliary operational qualitative indicator.")

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
        st.markdown(f'<div class="bento-card"><div class="bento-label">Operational State</div><div class="bento-value" style="font-size: 1.1rem;">{html.escape(analysis.operational_state_inference.split("(")[0].strip())}</div><div class="bento-sub">Inferred State</div></div>', unsafe_allow_html=True)
    with col_sm4:
        st.markdown(f'<div class="bento-card"><div class="bento-label">Remote Verdict</div><div class="bento-value" style="font-size: 1.1rem;">{html.escape(analysis.consistency_verdict)}</div><div class="bento-sub">Signal Concordance</div></div>', unsafe_allow_html=True)

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
        fig_obs = apply_stitch_plotly_theme(fig_obs, f"2023 Sentinel-5P TROPOMI NO₂ Plume vs 15-30km Buffer Background: {html.escape(target_fac_name)}")
        fig_obs.update_layout(height=340)
        st.plotly_chart(fig_obs, use_container_width=True)

# -------------------------------------------------------------
# TAB 6: BAYESIAN EVIDENCE FUSION
# -------------------------------------------------------------
elif menu == "6. Bayesian Evidence Fusion":
    scope_banner()
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

        has_satellite = st.checkbox("Include Copernicus Sentinel-5P Satellite Data (Auxiliary)", True)
        if has_satellite:
            sat_zscore = st.slider("Satellite Plume Anomaly Z-Score (vs Regional Background)", -2.0, 4.0, 1.8, 0.1)
            sat_cloud = st.slider("Satellite Cloud Obscuration Fraction", 0.0, 1.0, 0.25, 0.05)
        else:
            sat_zscore = None
            sat_cloud = 1.0

        has_temporal = st.checkbox("Include Historical Time Series Baseline", True)
        if has_temporal:
            temp_zscore = st.slider("Sudden Emission Drop Anomaly max(0, -z)", 0.0, 4.0, 0.8, 0.1)
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
        st.markdown(f'<div class="status-badge {verdict_badge_class}">{html.escape(decision.audit_verdict.upper())}</div>', unsafe_allow_html=True)
        st.write("")

        m_r, m_c = st.columns(2)
        with m_r:
            st.markdown(f'<div class="bento-card"><div class="bento-label">Inconsistency Risk P(H|E)</div><div class="bento-value" style="color: #8ed5ff;">{decision.posterior_inconsistency_risk*100:.1f}%</div><div class="bento-sub">Posterior Probability</div></div>', unsafe_allow_html=True)
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
# TAB 7: EMPIRICAL BENCHMARK EVALUATION & ABLATION
# -------------------------------------------------------------
elif menu == "7. Empirical Benchmark Evaluation & Ablation":
    scope_banner()
    st.markdown('<div class="stitch-main-title">Empirical Benchmark Evaluation: Primary 325-Case Graded Suite</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Rigorous Evaluation of Single-Stream and Multimodal Decision Models across 325 Graded Scenarios</div>',
        unsafe_allow_html=True,
    )

    results_dir = Path(__file__).parents[2] / "experiments" / "results"
    graded_summary_csv = results_dir / "graded_model_comparison_summary.csv"
    graded_sens_csv = results_dir / "graded_label_sensitivity.csv"
    m5_ablation_csv = results_dir / "m5_historical_score_ablation.csv"
    triage_csv = results_dir / "triage_auditor_simulation.csv"
    attr_csv = results_dir / "attribution_study.csv"

    # Legacy files
    legacy_abl_csv = results_dir / "ablation_study_summary.csv"
    legacy_calib_csv = results_dir / "calibration_comparison.csv"

    if graded_summary_csv.exists():
        df_summary = pd.read_csv(graded_summary_csv)
        row_e1 = df_summary[df_summary["model_name"].str.contains("Bayesian")].iloc[0]
        row_e2 = df_summary[df_summary["model_name"].str.contains("Logistic")].iloc[0]
        row_d = df_summary[df_summary["model_name"].str.contains("Historical Alone")].iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f'<div class="bento-card"><div class="bento-label">Model E1 Bayesian AUC</div>'
                f'<div class="bento-value" style="color: #8ed5ff;">{row_e1["roc_auc"]:.4f}</div>'
                f'<div class="bento-sub">95% CI [{row_e1["roc_auc_ci_low"]:.3f}, {row_e1["roc_auc_ci_high"]:.3f}]</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="bento-card"><div class="bento-label">Model E2 Logistic AUC</div>'
                f'<div class="bento-value" style="color: #4edea3;">{row_e2["roc_auc"]:.4f}</div>'
                f'<div class="bento-sub">95% CI [{row_e2["roc_auc_ci_low"]:.3f}, {row_e2["roc_auc_ci_high"]:.3f}]</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="bento-card"><div class="bento-label">Model D Historical AUC</div>'
                f'<div class="bento-value">{row_d["roc_auc"]:.4f}</div>'
                f'<div class="bento-sub">Dominant Single Modality</div></div>',
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f'<div class="bento-card"><div class="bento-label">Evaluated Benchmark</div>'
                f'<div class="bento-value">325 Cases</div>'
                f'<div class="bento-sub">177 Negatives • 148 Inconsistencies</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("### 1. Primary Model Comparison on Graded Benchmark (325 Cases)")
        st.caption("Evaluated across 177 authentic real-year negatives, 140 graded understatements, and 8 route mismatches. 95% CIs derived from 1,000 facility-level bootstrap resamples.")

        display_df = df_summary[["model_name", "roc_auc", "pr_auc", "brier_score", "ece", "fpr_authentic"]].copy()
        display_df.columns = ["Model Architecture", "ROC-AUC", "PR-AUC", "Brier Score", "ECE", "Authentic FPR"]
        st.dataframe(
            display_df.style.format({
                "ROC-AUC": "{:.4f}",
                "PR-AUC": "{:.4f}",
                "Brier Score": "{:.4f}",
                "ECE": "{:.4f}",
                "Authentic FPR": "{:.2%}",
            }),
            use_container_width=True,
        )

        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(name="ROC-AUC", x=df_summary["model_name"], y=df_summary["roc_auc"], marker_color="#8ed5ff"))
        fig_bars.add_trace(go.Bar(name="PR-AUC", x=df_summary["model_name"], y=df_summary["pr_auc"], marker_color="#4edea3"))
        fig_bars.add_trace(go.Bar(name="Brier Score", x=df_summary["model_name"], y=df_summary["brier_score"], marker_color="#facc15"))
        fig_bars = apply_stitch_plotly_theme(fig_bars, "Discrimination & Error Across Evaluated Architectures")
        fig_bars.update_layout(barmode="group", height=350)
        st.plotly_chart(fig_bars, use_container_width=True)

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if m5_ablation_csv.exists():
                st.markdown("### 2. M5 Historical Score Sign Ablation")
                st.caption("Methodological comparison: one-sided max(0, -z) avoids penalizing legitimate production growth.")
                df_m5 = pd.read_csv(m5_ablation_csv)
                st.dataframe(
                    df_m5.style.format({
                        "roc_auc": "{:.4f}",
                        "pr_auc": "{:.4f}",
                        "brier_score": "{:.4f}",
                        "ece": "{:.4f}",
                        "fpr_authentic": "{:.2%}",
                    }),
                    use_container_width=True,
                )

        with col_t2:
            if graded_sens_csv.exists():
                st.markdown("### 3. M1 Screening Threshold Sensitivity")
                st.caption("Primary (delta >= 10%) vs Sensitivity (delta >= 5%) screening rules.")
                df_sens = pd.read_csv(graded_sens_csv)
                st.dataframe(
                    df_sens[["threshold", "model", "prevalence", "roc_auc", "pr_auc"]].style.format({
                        "prevalence": "{:.1%}",
                        "roc_auc": "{:.4f}",
                        "pr_auc": "{:.4f}",
                    }),
                    use_container_width=True,
                )

        if triage_csv.exists():
            st.markdown("### 4. Auditor Triage Efficiency (Resource Constraint Simulation)")
            st.caption("Simulating customs capacity constraint: audit top k% highest-risk declarations.")
            df_triage = pd.read_csv(triage_csv)
            st.dataframe(
                df_triage[[
                    "k_pct", "k_cases",
                    "e1_bayes_caught", "e1_bayes_precision", "e1_bayes_recall",
                    "e2_logistic_caught", "e2_logistic_precision", "e2_logistic_recall"
                ]].style.format({
                    "k_pct": "Top {}%",
                    "e1_bayes_precision": "{:.1%}",
                    "e1_bayes_recall": "{:.1%}",
                    "e2_logistic_precision": "{:.1%}",
                    "e2_logistic_recall": "{:.1%}",
                }),
                use_container_width=True,
            )

        if attr_csv.exists():
            st.markdown("### 5. Step-by-Step Methodological Attribution")
            df_attr = pd.read_csv(attr_csv)
            st.dataframe(
                df_attr.style.format({
                    "roc_auc": "{:.4f}",
                    "pr_auc": "{:.4f}",
                    "brier": "{:.4f}",
                    "ece": "{:.4f}",
                }),
                use_container_width=True,
            )

        # Legacy Expander
        with st.expander("📁 Legacy 101-Case Controlled Benchmark (Regression & Calibration Testing Only)"):
            st.warning("Notice: The 101-case benchmark is retained exclusively for regression tracking. The 325-case graded benchmark above represents the primary scientific finding.")
            if legacy_abl_csv.exists():
                df_leg = pd.read_csv(legacy_abl_csv)
                st.dataframe(df_leg, use_container_width=True)
            if legacy_calib_csv.exists():
                df_cal = pd.read_csv(legacy_calib_csv)
                st.dataframe(df_cal, use_container_width=True)

# -------------------------------------------------------------
# TAB 8: PROPOSAL, REFERENCES & ROADMAP
# -------------------------------------------------------------
elif menu == "8. Capstone Proposal, References & Roadmap":
    scope_banner()
    st.markdown('<div class="stitch-main-title">Master Capstone Proposal & Academic Roadmap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">University of Europe for Applied Sciences (UE Germany) | Master of Science in Data Science</div>',
        unsafe_allow_html=True,
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("### Author & Project Metadata")
        st.markdown(
            """
            - **Author:** Cristhian David Cáceres Mateus
            - **Study Program:** Master of Science in Data Science
            - **Institution:** University of Europe for Applied Sciences (UE Germany), Berlin Campus
            - **Supervisor:** Dr. Humera Noor
            - **Working Title:** *VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment*
            - **Official Application:** Form filled & approved under Commission Delegated Regulation (EU) 2025/2551.
            """
        )
    with col_p2:
        st.markdown("### Key Scientific & Mathematical Formulations")
        st.markdown(
            """
            - **Stoichiometric Calcination Floor:** $\\text{CaCO}_3 \\rightarrow \\text{CaO} + \\text{CO}_2$ ($0.495\\text{--}0.525\\text{ t CO}_2/\\text{t clinker}$)
            - **Blast Furnace Reduction Floor:** $\\text{Fe}_2\\text{O}_3 + 3\\text{C} \\rightarrow 2\\text{Fe} + 3\\text{CO}$ ($1.350\\text{ t CO}_2/\\text{t crude steel}$)
            - **Bayesian Log-Odds Fusion:** $\\text{logit } P(H|E) = \\text{logit } P(H) + \\sum w_i C_i \\ln(LR_i)$
            - **Robust Historical Scale:** Pooled MAD $\\sigma_{\\text{pooled}} = 0.0911$ over 177 plant-years.
            """
        )

    st.markdown("---")
    st.markdown("### Regulatory Framework & ELI Links")
    st.markdown(
        """
        - **Regulation (EU) 2023/956:** Establishing the CBAM mechanism.
        - **Commission Implementing Regulation (EU) 2025/2546:** Verification principles and rules. [ELI Link](http://data.europa.eu/eli/reg_impl/2025/2546/oj)
        - **Commission Delegated Regulation (EU) 2025/2551:** Verifier accreditation requirements. [ELI Link](http://data.europa.eu/eli/reg_del/2025/2551/oj)
        - **Commission Implementing Regulation (EU) 2025/2547:** Rules for calculation of embedded emissions. [ELI Link](http://data.europa.eu/eli/reg_impl/2025/2547/oj)
        """
    )
