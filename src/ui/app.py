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
WORKSPACE_ROOT = Path(__file__).parents[2]
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
    /* ========================================================
       GLOBAL CANVAS & ROOT TOKENS
       ======================================================== */
    :root {
        --text-color: #f1f5f9 !important;
        --background-color: #0f131c !important;
        --secondary-background-color: #161922 !important;
    }

    .stApp {
        background-color: #0f131c !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li {
        color: #f1f5f9 !important;
    }

    /* ========================================================
       SIDEBAR UNIVERSAL HIGH-CONTRAST OVERRIDES
       ======================================================== */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    section[data-testid="stSidebar"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarUserContent"] {
        background-color: #161922 !important;
        border-right: 1px solid #2d3440 !important;
    }

    /* Sidebar Headings */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.01em !important;
    }

    /* Sidebar Captions and Secondary Text */
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,
    [data-testid="stSidebar"] caption,
    [data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    /* Sidebar Navigation Header */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,
    [data-testid="stSidebar"] [data-testid="stRadio"] > label *,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {
        color: #8ed5ff !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    /* Sidebar Radio Item Cards */
    [data-testid="stSidebar"] div[role="radiogroup"] > label,
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label,
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: #1e2533 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 9px 12px !important;
        margin-bottom: 5px !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label *,
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label * {
        color: #ffffff !important;
        font-size: 0.90rem !important;
        font-weight: 500 !important;
        line-height: 1.35 !important;
    }

    /* Sidebar Radio Hover */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover,
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background-color: #253347 !important;
        border-color: #8ed5ff !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover * {
        color: #8ed5ff !important;
    }

    /* Sidebar Radio Selected */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked),
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background-color: #1c3552 !important;
        border: 1px solid #8ed5ff !important;
        border-left: 5px solid #8ed5ff !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) *,
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Sidebar Metadata Card */
    .sidebar-student-box {
        background: #1a2230 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        margin-top: 20px !important;
        font-size: 0.82rem !important;
        line-height: 1.6 !important;
    }
    .sidebar-student-box .box-label {
        color: #8ed5ff !important;
        font-weight: 700 !important;
    }
    .sidebar-student-box .box-val {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* Sidebar Alerts / Info */
    [data-testid="stSidebar"] [data-testid="stAlert"],
    section[data-testid="stSidebar"] [data-testid="stAlert"] {
        background: #1a2230 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] * {
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] strong {
        color: #8ed5ff !important;
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
st.sidebar.markdown(STITCH_THEME_CSS, unsafe_allow_html=True)


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

# Sidebar Navigation (Brand Identity & Clean Architecture)
shield_icon_path = Path(__file__).parent / "shield.png"
if shield_icon_path.exists():
    st.sidebar.image(str(shield_icon_path), width=56)
st.sidebar.markdown("### VeriCBAM Audit Suite")
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
        <div><span class="box-label">University:</span> <span class="box-val">UE Germany (Potsdam)</span></div>
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

    view_mode = st.radio(
        "Select View Mode:",
        ["Executive Summary", "Embedded Regulatory Cockpit"],
        horizontal=True,
        help="Switch between high-level executive cards or the full interactive Google Stitch decision cockpit view.",
    )

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
                <div class="bento-card" title="Curated European industrial installations from EEA E-PRTR database">
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
                <div class="bento-card" title="Authentic annual facility reporting records spanning 2018 through 2023">
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
                <div class="bento-card" title="Rigorous evaluation benchmark with authentic cases and graded understatement perturbations">
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
                <div class="bento-card" title="Multi-modal evidence streams fused by the decision support engine">
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

    st.markdown("---")
    with st.expander("📋 Decision Matrix: Summary of VeriCBAM Screening Outcomes & Actions", expanded=True):
        st.markdown(
            r"""
            | Screening Verdict | System Status Badge | Triggering Condition | Meaning for Non-Technical Stakeholders | Recommended Regulatory Action |
            | :--- | :---: | :--- | :--- | :--- |
            | **Consistent** | `CONSISTENT` | Posterior Risk $P(H \mid E) < 25\%$ | Declared emissions are fully aligned with chemical stoichiometry, verified capacity, and historical trajectories. | **Clear for Expedited Desk Verification.** No physical on-site inspection required. |
            | **Potential Inconsistency** | `POTENTIAL INCONSISTENCY` | $25\% \le P(H \mid E) \le 70\%$ | The declaration exhibits unusual energy efficiency or minor deviations from historical plant patterns. | **Technical Clarification Request.** Ask importer to supply raw fuel purchase invoices and clinker-to-cement ratios. |
            | **High Inconsistency Risk** | `HIGH RISK (VIOLATION)` | $P(H \mid E) > 70\%$ or Chemical Violation | The declaration claims physically impossible emission levels or exhibits massive uncharacteristic drop anomalies ($>3.5\sigma$). | **Mandatory On-Site Physical Inspection.** Flag declaration to customs authorities; freeze CBAM certificate clearance. |
            | **Insufficient Evidence** | `INSUFFICIENT EVIDENCE` | Overall Confidence $C_{\text{overall}} < 50\%$ | Observational data is compromised (heavy cloud cover, missing historical records). System refuses to guess. | **Defer Remote Conclusion.** Do not penalize supplier; request accredited third-party on-site verification records. |
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

    c_filter, s_filter, f_filter = st.columns([1, 1, 2])
    with c_filter:
        sector_choice = st.selectbox(
            "Filter Sector:",
            ["All Sectors", "Cement", "Steel"],
            help="Filter the industrial cohort by manufacturing sector (Cement or Steel).",
        )
    with s_filter:
        country_choice = st.selectbox(
            "Filter Country:",
            ["All Countries"] + sorted(facilities_df["countryName"].unique().tolist()),
            help="Filter facilities geographically by host European country.",
        )

    filtered_facilities = facilities_df.copy()
    if sector_choice != "All Sectors":
        filtered_facilities = filtered_facilities[filtered_facilities["sector"] == sector_choice]
    if country_choice != "All Countries":
        filtered_facilities = filtered_facilities[filtered_facilities["countryName"] == country_choice]

    with f_filter:
        facility_options = filtered_facilities["facilityName"].tolist()
        if not facility_options:
            facility_options = facilities_df["facilityName"].tolist()
            filtered_facilities = facilities_df.copy()
        selected_facility_name = st.selectbox(
            "Select Target Facility to Inspect & Highlight on Map:",
            facility_options,
            help="Choose an industrial plant to center and highlight on the map and display its multi-year emissions timeline.",
        )

    if "latitude" not in filtered_facilities.columns and "Latitude" in filtered_facilities.columns:
        filtered_facilities["latitude"] = filtered_facilities["Latitude"]
    if "longitude" not in filtered_facilities.columns and "Longitude" in filtered_facilities.columns:
        filtered_facilities["longitude"] = filtered_facilities["Longitude"]

    fac_row = filtered_facilities[filtered_facilities["facilityName"] == selected_facility_name].iloc[0]
    fac_id = fac_row["FacilityInspireId"]
    fac_lat = float(fac_row.get("latitude", fac_row.get("Latitude", 51.1657)))
    fac_lon = float(fac_row.get("longitude", fac_row.get("Longitude", 10.4515)))
    ts_df = mgr.get_facility_time_series(fac_id)

    # Calculate Legal Permit Limit / Capacity Ceiling
    sector = str(fac_row.get("sector", "Cement"))
    if sector == "Cement":
        cap_mtpa = float(fac_row.get("clinker_capacity_mtpa", 0.0) or 0.0)
        if cap_mtpa <= 0.0:
            cap_mtpa = float(fac_row.get("cement_capacity_mtpa", 1.5) or 1.5)
        legal_limit_tco2 = cap_mtpa * 1e6 * 0.950
        legal_basis = f"Licensed Clinker Capacity ({cap_mtpa:.2f} Mt/yr) × 0.950 t CO₂/t BAT Upper Limit"
    else:
        cap_mtpa = float(fac_row.get("crude_steel_capacity_mtpa", 0.0) or 0.0)
        if cap_mtpa <= 0.0:
            cap_mtpa = float(fac_row.get("primary_iron_capacity_mtpa", 0.0) or 0.0)
        if cap_mtpa <= 0.0:
            cap_mtpa = 2.5
        route_desc = str(fac_row.get("verified_technology_route", ""))
        if "Scrap" in route_desc or "EAF" in route_desc:
            legal_limit_tco2 = cap_mtpa * 1e6 * 0.350
            legal_basis = f"Licensed EAF Steel Capacity ({cap_mtpa:.2f} Mt/yr) × 0.350 t CO₂/t Scrap-EAF Envelope"
        else:
            legal_limit_tco2 = cap_mtpa * 1e6 * 2.200
            legal_basis = f"Licensed BF-BOF Capacity ({cap_mtpa:.2f} Mt/yr) × 2.200 t CO₂/t Integrated Ceiling"

    if legal_limit_tco2 <= 0.0 or np.isnan(legal_limit_tco2):
        legal_limit_tco2 = float(fac_row.get("max_co2_tonnes", 1000000.0)) * 1.15
        legal_basis = "115% Historical Peak Environmental Baseline"

    # Map with highlighted selected facility pin
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
            size_max=30,
            zoom=4.0,
            center={"lat": fac_lat, "lon": fac_lon},
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
            size_max=30,
            zoom=4.0,
            center={"lat": fac_lat, "lon": fac_lon},
            mapbox_style="carto-darkmatter",
            title="Geospatial Distribution of Benchmark Industrial Cohort",
        )

    # Highlight overlay trace for selected facility
    try:
        fig_map.add_trace(go.Scattermap(
            lat=[fac_lat],
            lon=[fac_lon],
            mode="markers+text",
            marker=dict(size=26, color="#ef4444", opacity=0.95),
            text=[f"📍 {selected_facility_name}"],
            textposition="top center",
            name=f"Selected: {selected_facility_name}",
            hovertext=f"<b>📍 Selected: {selected_facility_name}</b><br>Sector: {fac_row['sector']}<br>City: {fac_row['city']}<br>Permit Limit: {legal_limit_tco2:,.0f} t CO₂/yr",
            hoverinfo="text",
        ))
    except Exception:
        fig_map.add_trace(go.Scattermapbox(
            lat=[fac_lat],
            lon=[fac_lon],
            mode="markers+text",
            marker=dict(size=26, color="#ef4444", opacity=0.95),
            text=[f"📍 {selected_facility_name}"],
            textposition="top center",
            name=f"Selected: {selected_facility_name}",
            hovertext=f"<b>📍 Selected: {selected_facility_name}</b><br>Sector: {fac_row['sector']}<br>City: {fac_row['city']}<br>Permit Limit: {legal_limit_tco2:,.0f} t CO₂/yr",
            hoverinfo="text",
        ))

    fig_map = apply_stitch_plotly_theme(fig_map, f"Geospatial Cohort (Highlighting: {html.escape(selected_facility_name)})")
    fig_map.update_layout(height=480, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown(
            f"""
            <div class="bento-card">
                <div class="bento-label">Facility Metadata & Licensed Permit</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px;">{html.escape(str(fac_row['facilityName']))}</div>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 4px 0;"><strong>Sector:</strong> <code style="color: #8ed5ff;">{html.escape(str(fac_row['sector']))}</code></p>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 4px 0;"><strong>Location:</strong> {html.escape(str(fac_row['city']))}, {html.escape(str(fac_row['countryName']))}</p>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 4px 0;"><strong>Coordinates:</strong> ({fac_lat:.4f}, {fac_lon:.4f})</p>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 4px 0;"><strong>Verified Route:</strong> {html.escape(str(fac_row.get('verified_technology_route', 'N/A')))}</p>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 4px 0;"><strong>Historical Mean CO₂:</strong> {fac_row['mean_co2_tonnes']:,.0f} t/yr</p>
                <div style="margin-top: 10px; padding: 8px 10px; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 6px;">
                    <span style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #ffb4ab;">Legal Permit Emissions Limit:</span>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #ef4444; font-family: monospace;">{legal_limit_tco2:,.0f} t CO₂/yr</div>
                    <div style="font-size: 0.72rem; color: #cbd5e1;">Basis: {html.escape(legal_basis)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        if not ts_df.empty:
            ts_sorted = ts_df.sort_values("reportingYear").copy()
            fig_ts = go.Figure()

            # Timeline of verified emissions
            fig_ts.add_trace(go.Scatter(
                x=ts_sorted["reportingYear"],
                y=ts_sorted["co2_tonnes"],
                mode="lines+markers",
                name="Verified Scope 1 CO₂ (E-PRTR)",
                line=dict(color="#8ed5ff", width=3),
                marker=dict(size=10, color="#8ed5ff", symbol="circle", line=dict(color="#ffffff", width=1.5)),
                hovertemplate="<b>Year %{x}</b><br>Reported: %{y:,.0f} t CO₂<extra></extra>",
            ))

            # Red dashed legal limit line
            fig_ts.add_trace(go.Scatter(
                x=[ts_sorted["reportingYear"].min(), ts_sorted["reportingYear"].max()],
                y=[legal_limit_tco2, legal_limit_tco2],
                mode="lines",
                name=f"Legal Permit Limit ({legal_limit_tco2:,.0f} t/yr)",
                line=dict(color="#ef4444", width=2.5, dash="dash"),
                hovertemplate=f"<b>Legal Permit Limit</b>: {legal_limit_tco2:,.0f} t CO₂/yr<extra></extra>",
            ))

            fig_ts.add_annotation(
                x=ts_sorted["reportingYear"].median(),
                y=legal_limit_tco2,
                text=f"Legal Permit Limit: {legal_limit_tco2:,.0f} t CO₂/yr",
                showarrow=False,
                yshift=14,
                font=dict(color="#ef4444", size=11, family="monospace"),
                bgcolor="rgba(15, 19, 28, 0.9)",
                bordercolor="#ef4444",
                borderwidth=1,
            )

            fig_ts = apply_stitch_plotly_theme(fig_ts, f"Multi-Year Emissions Timeline vs Legal Permit Limit: {html.escape(str(fac_row['facilityName']))}")
            fig_ts.update_layout(
                height=320,
                xaxis=dict(title="Reporting Calendar Year", dtick=1, gridcolor="#2d3440"),
                yaxis=dict(title="Verified Scope 1 CO₂ (Tonnes)", gridcolor="#2d3440"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_ts, use_container_width=True)

    # Tab 2 Decision Matrix
    st.markdown("---")
    with st.expander("📋 Decision Matrix: Summary of Cohort Historical Trajectory Diagnoses", expanded=True):
        st.markdown(
            r"""
            | Trajectory Status | Indicator | Quantitative Condition | Operational Interpretation | Audit Recommendation |
            | :--- | :---: | :--- | :--- | :--- |
            | **Normal Historical Operation** | 🟢 Concordant | Within $\pm 1.5\sigma$ of 6-year mean | Plant emissions fluctuate within normal European industrial operational variance. | Use historical mean as reliable prior baseline for upcoming CBAM reporting. |
            | **Noticeable Emission Drop** | 🟡 Moderate Drift | Drop between $1.5\sigma$ and $3.0\sigma$ | Facility emitted noticeably less than past years; could reflect reduced production, kiln overhaul, or under-reporting. | Compare claimed production volume against national grid/clinker trade flows. |
            | **Severe Historical Drop Anomaly** | 🔴 High Anomaly | Drop $> 3.5\sigma$ ($\max(0, -z) > 3.5$) | Statistically improbable emissions drop while declaring sustained or growing production volume. | Priority candidate for production verification; verify whether operations were partially shut down or diverted. |
            | **Permit Cap Breach** | 🚨 Over-Capacity | Reported $\text{CO}_2 > \text{Legal Permit Cap}$ | Declared emissions exceed licensed environmental permit ceiling under EU Industrial Emissions Directive (IED). | Flag potential illegal capacity expansion or permit compliance violation to national environmental regulator. |
            """
        )

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

    sector_mode = st.radio(
        "Select Production Sector for Audit Simulation:",
        ["Cement Clinker", "Crude Steel"],
        horizontal=True,
        help="Select the industrial commodity sector to simulate first-principles stoichiometric verification against chemical mass balances.",
    )

    if sector_mode == "Cement Clinker":
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            clinker_tonnes = st.number_input(
                "Clinker Produced (Metric Tonnes)",
                min_value=10000.0,
                max_value=5000000.0,
                value=1000000.0,
                step=50000.0,
                help="Annual mass of clinker produced in metric tonnes (calcined limestone kiln output). Forms the primary chemical basis for calcination CO₂.",
            )
            cement_tonnes = st.number_input(
                "Total Cement Produced (Tonnes)",
                min_value=10000.0,
                max_value=6000000.0,
                value=1150000.0,
                step=50000.0,
                help="Annual mass of finished cement ground and dispatched (clinker plus gypsum, slag, and fly ash additives).",
            )
        with col_c2:
            clinker_ratio = st.slider(
                "Clinker-to-Cement Ratio",
                min_value=0.40,
                max_value=1.0,
                value=0.87,
                step=0.01,
                help="Proportion of clinker in finished cement (e.g., 0.87 for CEM I / CEM II blend). Higher clinker ratio mathematically increases emissions.",
            )
            fuel_type = st.selectbox(
                "Primary Kiln Fuel",
                ["coal", "petcoke", "natural_gas", "waste_derived_fuel_50pct_bio"],
                help="Primary thermal fuel fired into the rotary kiln. Waste-derived fuels with 50% biomass credit lower fossil combustion emissions.",
            )
        with col_c3:
            reported_co2 = st.number_input(
                "Reported Direct Scope 1 CO₂ (Tonnes)",
                min_value=0.0,
                max_value=5000000.0,
                value=810000.0,
                step=25000.0,
                help="Total gross direct Scope 1 carbon dioxide emissions declared by the facility for the calendar reporting year.",
            )
            ccus_tco2 = st.number_input(
                "Verified CCUS Captured CO₂ (Tonnes)",
                min_value=0.0,
                max_value=1000000.0,
                value=0.0,
                step=10000.0,
                help="Permanently captured and geologically stored CO₂ tonnage supported by ISO 14064-3 verified custody transfer records.",
            )

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
            steel_tonnes = st.number_input(
                "Crude Steel Produced (Tonnes)",
                min_value=10000.0,
                max_value=10000000.0,
                value=2000000.0,
                step=50000.0,
                help="Total annual metric tonnes of liquid crude steel produced across blast furnaces or electric arc furnaces.",
            )
            claimed_route = st.selectbox(
                "Claimed Production Route",
                ["BF-BOF", "DRI-NG-EAF", "DRI-H2-EAF", "Scrap-EAF"],
                help="Industrial manufacturing method claimed in declaration (e.g., carbon-intensive integrated BF-BOF vs low-carbon Scrap-EAF recycling).",
            )
        with col_s2:
            scrap_ratio = st.slider(
                "Scrap Ratio (Dilution)",
                min_value=0.05,
                max_value=1.0,
                value=0.18,
                step=0.01,
                help="Fraction of recycled scrap steel charged into the furnace to dilute hot metal carbon intensity.",
            )
            reported_steel_co2 = st.number_input(
                "Reported Scope 1 CO₂ (Tonnes)",
                min_value=0.0,
                max_value=10000000.0,
                value=3600000.0,
                step=50000.0,
                help="Total direct Scope 1 carbon dioxide emissions declared by the steelworks for the calendar reporting year.",
            )
        with col_s3:
            steel_ccus = st.number_input(
                "Verified CCUS Captured CO₂ (Tonnes)",
                min_value=0.0,
                max_value=2000000.0,
                value=0.0,
                step=10000.0,
                help="Verified captured CO₂ tonnage permanently sequestered via compliant carbon capture infrastructure.",
            )

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

    st.markdown("---")
    with st.expander("📋 Decision Matrix: Summary of Stoichiometric Physical Diagnoses & Actions", expanded=True):
        st.markdown(
            r"""
            | Physical Feasibility Verdict | Status Badge | Physical & Chemical Condition | Non-Technical Operational Meaning | Recommended Regulatory Action |
            | :--- | :---: | :--- | :--- | :--- |
            | **Physically Feasible / Concordant** | `✅ PHYSICALLY FEASIBLE` | Declared Scope 1 $\ge$ Net Stoichiometric Floor | Declared emissions exceed the absolute chemical minimum required by law of conservation of mass (calcination + BAT combustion). | **Accepted for Standard Desk Verification.** Proceed to historical trajectory and registry checks. |
            | **Route Misclassification Detected** | `⚠️ ROUTE MISCLASSIFICATION DETECTED` | Intensity matches low-carbon route (Scrap-EAF) but is impossible for claimed route (BF-BOF) | Plant claims to use one production method but reports emissions typical of a much lower-carbon alternative. | **Technical Route Audit.** Request production logbooks, electricity bills, and scrap purchasing invoices to verify physical technology. |
            | **Physical Stoichiometric Violation** | `🚨 PHYSICAL FEASIBILITY VIOLATION` | Declared Scope 1 $<$ Net Stoichiometric Floor | The declaration claims emissions lower than what chemical reactions physically emit under stoichiometric conversion efficiency and best-available thermal efficiency. | **Immediate Rejection / Mandatory Audit.** Declaration cannot be true under the laws of chemistry. Freeze CBAM clearance and dispatch verifiers. |
            | **Unsubstantiated Carbon Capture (CCUS)** | `⚠️ HIGH DEFICIT RISK` | Net emissions feasible only with massive CCUS deduction | Reported gross emissions violate floor unless credited with large unverified CCUS volumes. | **Audit CCUS Transfer Receipts.** Demand accredited ISO 14064-3 geological storage custody transfer certificates. |
            """
        )

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
        supplier_name = st.text_input(
            "Supplier / Installation Name:",
            "Overseas Heavy Industries Ltd.",
            help="Legal corporate identity or installation trading name of the non-EU industrial supplier.",
        )
        supp_sector = st.selectbox(
            "Commodity Sector:",
            ["Cement Clinker", "Finished Cement (CEM II)", "Crude Steel (BF-BOF)", "Crude Steel (Scrap-EAF)"],
            help="Standardized industrial commodity category covered under EU CBAM Annex I.",
        )
        decl_specific_emissions = st.number_input(
            "Declared Specific Scope 1 Intensity (t CO₂ / t product):",
            min_value=0.0,
            max_value=5.0,
            value=0.62,
            step=0.01,
            help="Declared direct emissions intensity per metric tonne of product (Scope 1 t CO₂ / t). Evaluated against chemical reaction baselines.",
        )
        annual_volume_tonnes = st.number_input(
            "Annual Production Volume (Metric Tonnes):",
            min_value=1000.0,
            max_value=20000000.0,
            value=1200000.0,
            step=50000.0,
            help="Total declared volume of goods imported into the European Union during the calendar year.",
        )

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

    st.markdown("---")
    with st.expander("📋 Decision Matrix: Summary of Supplier Plausibility Pre-Check Diagnoses", expanded=True):
        st.markdown(
            r"""
            | Pre-Check Verdict | Status Badge | Quantitative Intensity Range | Non-Technical Operational Meaning | Commercial & Customs Action |
            | :--- | :---: | :--- | :--- | :--- |
            | **Consistent with Physical Floor** | `CONSISTENT WITH PHYSICAL FLOOR` | Specific Intensity $\ge$ Typical Benchmark Lower Bound | Declared intensity aligns with modern European and global Best Available Techniques (BAT). | **Clear for Import Filing.** Standard CBAM declaration clearance approved. |
            | **Potential Inconsistency (Low Intensity)** | `POTENTIAL INCONSISTENCY (LOW INTENSITY)` | Physical Floor $\le$ Intensity $<$ Typical Benchmark | Plant claims world-class energy efficiency surpassing 90% of global industrial installations. Plausible only with advanced tech. | **Request Production Details.** Ask importer for clinker-to-cement ratio or electric arc furnace power receipts. |
            | **High Inconsistency Risk (Physical Violation)** | `HIGH INCONSISTENCY RISK (VIOLATION)` | Specific Intensity $<$ Physical Lower Bound Floor | Declared carbon intensity violates fundamental laws of physics and chemical reactions. | **Reject CBAM Filing.** Importer must revise declaration or pay default EU benchmark penalty rates. |
            """
        )

# -------------------------------------------------------------
# -------------------------------------------------------------
# TAB 5: COPERNICUS SATELLITE ENGINE & STAGE 2 MULTI-SENSOR EO
# -------------------------------------------------------------
elif menu == "5. Copernicus Satellite Engine (Sentinel-5P)":
    scope_banner()
    st.markdown('<div class="stitch-main-title">Multi-Sensor Earth Observation & Satellite Verification Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="stitch-sub-title">Stage 1 Atmospheric NO₂ Plumes (Sentinel-5P) + Stage 2 Kiln/Furnace Thermal Infrared (USGS Landsat 30m / NASA FIRMS 375m) & Optical Freight Logistics (Planet Labs 3m / VHR)</div>',
        unsafe_allow_html=True,
    )

    sat_client = CopernicusSentinel5PClient()
    sat_analyzer = SatellitePlumeAnalyzer()

    c_sel, p_sel = st.columns([2, 1])
    with c_sel:
        target_fac_name = st.selectbox(
            "Select Target Facility for Multi-Sensor Satellite Analysis:",
            facilities_df["facilityName"].tolist(),
            help="Select an industrial facility from the 30-plant European cohort to inspect Stage 2 Thermal/Logistics and Stage 1 Atmospheric Plumes.",
        )
    with p_sel:
        prod_claimed = st.number_input(
            "Declared Production (Tonnes)",
            min_value=10000.0,
            max_value=10000000.0,
            value=1000000.0,
            step=50000.0,
            help="Declared annual production volume (metric tonnes) to cross-check against observed satellite thermal, freight, and atmospheric activity.",
        )

    target_row = facilities_df[facilities_df["facilityName"] == target_fac_name].iloc[0]
    fac_id = target_row["FacilityInspireId"]
    lat = float(target_row.get("latitude", target_row.get("Latitude", 0.0)))
    lon = float(target_row.get("longitude", target_row.get("Longitude", 0.0)))

    sat_tab_stage2, sat_tab_stage1 = st.tabs([
        "🔥 Stage 2: Thermal Kiln/Furnace Timeline (USGS/FIRMS) & Freight Railcars (Planet/VHR)",
        "🌫️ Stage 1: Copernicus Sentinel-5P Atmospheric NO₂ Plume (Baseline)",
    ])

    with sat_tab_stage2:
        ms_parquet_path = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "multisensor_thermal_logistics_2023.parquet"
        firms_tl_path = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "firms_viirs_monthly_timeline_2023.parquet"

        if ms_parquet_path.exists():
            ms_df = pd.read_parquet(ms_parquet_path)
            ms_sub = ms_df[ms_df["facility_id"] == fac_id]
            if ms_sub.empty:
                ms_sub = ms_df[ms_df["facility_name"] == target_fac_name]
        else:
            ms_sub = pd.DataFrame()

        if not ms_sub.empty:
            ms_row = ms_sub.iloc[0]
            st.success(
                f"✅ **Stage 2 Multi-Sensor Upgrade Active:** Pinpoint 30m/375m Thermal Infrared & 3m/Sub-Meter Optical Logistics resolve Stage 1's coarse footprint limit. "
                f"Across Cement kilns, NASA FIRMS 375m active thermal hotspots correlate strongly with reported Scope 1 CO₂ (**Spearman ρ = +0.778, p = 0.0010**); "
                f"across the pooled 30-plant cohort, the 12-month thermal operation timeline achieves **Spearman ρ = +0.470 (p = 0.0117)**."
            )

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(
                    f'<div class="bento-card"><div class="bento-label">Landsat-8/9 30m ΔT</div>'
                    f'<div class="bento-value" style="color: #f97316;">+{ms_row["thermal_delta_t_c"]:.1f} °C</div>'
                    f'<div class="bento-sub">Peak {ms_row["plant_core_peak_lst_c"]:.1f}°C vs Bg {ms_row["regional_bg_median_lst_c"]:.1f}°C</div></div>',
                    unsafe_allow_html=True,
                )
            with k2:
                st.markdown(
                    f'<div class="bento-card"><div class="bento-label">FIRMS VIIRS 375m Hotspots</div>'
                    f'<div class="bento-value" style="color: #facc15;">{int(ms_row["firms_hotspot_detections_2023"])} Hits</div>'
                    f'<div class="bento-sub">Active {int(ms_row["firms_active_months_count"])}/12 Mos • {ms_row["firms_cumulative_frp_mw"]:.1f} MW FRP</div></div>',
                    unsafe_allow_html=True,
                )
            with k3:
                st.markdown(
                    f'<div class="bento-card"><div class="bento-label">Planet Labs 3m Cadence</div>'
                    f'<div class="bento-value" style="color: #8ed5ff;">{int(ms_row["planet_clear_passes_2023"])} Passes</div>'
                    f'<div class="bento-sub">PSScene ({ms_row["planet_mean_gsd_m"]:.1f}m GSD) • {int(ms_row["planet_active_months_2023"])}/12 Mos</div></div>',
                    unsafe_allow_html=True,
                )
            with k4:
                st.markdown(
                    f'<div class="bento-card"><div class="bento-label">Freight & Stockpile Index</div>'
                    f'<div class="bento-value" style="color: #4edea3;">{ms_row["vhr_rail_yard_contrast_index"]:.3f}</div>'
                    f'<div class="bento-sub">Stockpile: {ms_row["vhr_stockpile_activity_index"]:.3f} • Z={ms_row["freight_logistics_zscore"]:+.2f}σ</div></div>',
                    unsafe_allow_html=True,
                )

            col_img, col_seg, col_tl = st.columns([1.0, 1.0, 1.35])
            img_rel = str(ms_row.get("vhr_image_path", ""))
            img_abs = WORKSPACE_ROOT / img_rel if img_rel else None

            with col_img:
                st.markdown("#### 🛰️ A. VHR Optical Factory & Rail-Yard")
                if img_abs and img_abs.exists():
                    st.image(
                        str(img_abs),
                        caption=(
                            f"{target_fac_name} ({lat:.4f}°N, {lon:.4f}°E) | "
                            f"Planet 3m Scene: {ms_row['planet_best_scene_id']} ({ms_row['planet_best_scene_date']})"
                        ),
                        use_container_width=True,
                    )
                else:
                    st.info("High-resolution optical chip not cached locally.")

            with col_seg:
                st.markdown("#### 🚂 B. Freight Rail-Yard & Stockpile Map")
                if img_abs and img_abs.exists():
                    from PIL import Image as _PILImage

                    vhr_arr = np.asarray(_PILImage.open(img_abs).convert("RGB"), dtype=np.float32) / 255.0
                    gray_arr = 0.299 * vhr_arr[:, :, 0] + 0.587 * vhr_arr[:, :, 1] + 0.114 * vhr_arr[:, :, 2]
                    gx_arr = np.abs(np.diff(gray_arr, axis=1, prepend=gray_arr[:, :1]))
                    gy_arr = np.abs(np.diff(gray_arr, axis=0, prepend=gray_arr[:1, :]))
                    edge_mag = np.sqrt(gx_arr**2 + gy_arr**2)
                    rail_mask = edge_mag > np.percentile(edge_mag, 86)
                    r_c, g_c, b_c = vhr_arr[:, :, 0], vhr_arr[:, :, 1], vhr_arr[:, :, 2]
                    ore_mask = (r_c > 0.34) & ((r_c / (b_c + 0.05)) > 1.32)
                    coal_mask = (gray_arr > 0.07) & (gray_arr < 0.24) & (np.abs(r_c - b_c) < 0.05)

                    seg_overlay = vhr_arr * 0.52
                    seg_overlay[rail_mask] = [0.0, 0.92, 1.0]
                    seg_overlay[ore_mask] = [1.0, 0.38, 0.08]
                    seg_overlay[coal_mask & (~rail_mask)] = [0.98, 0.80, 0.08]
                    seg_uint8 = (np.clip(seg_overlay, 0.0, 1.0) * 255).astype(np.uint8)
                    st.image(
                        seg_uint8,
                        caption=(
                            f"Cyan: Freight Rail Sidings & Wagons (Idx={ms_row['vhr_rail_yard_contrast_index']:.3f}) | "
                            f"Orange/Gold: Ore & Coal Stockpiles (Idx={ms_row['vhr_stockpile_activity_index']:.3f})"
                        ),
                        use_container_width=True,
                    )

            with col_tl:
                st.markdown("#### 🔥 C. 12-Month Operation Timeline (FIRMS 375m)")
                if firms_tl_path.exists():
                    tl_df = pd.read_parquet(firms_tl_path)
                    tl_fac = tl_df[tl_df["facility_id"] == fac_id].sort_values("month")
                    if not tl_fac.empty:
                        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                        tl_fac["Month_Name"] = [month_names[m - 1] for m in tl_fac["month"]]
                        fig_tl = go.Figure()
                        fig_tl.add_trace(
                            go.Bar(
                                x=tl_fac["Month_Name"],
                                y=tl_fac["hotspot_count"],
                                name="375m Thermal Detections (Count)",
                                marker_color="#f97316",
                            )
                        )
                        fig_tl.add_trace(
                            go.Scatter(
                                x=tl_fac["Month_Name"],
                                y=tl_fac["cumulative_frp_mw"],
                                name="Cumulative Radiative Power (MW)",
                                yaxis="y2",
                                line=dict(color="#facc15", width=3),
                                mode="lines+markers",
                            )
                        )
                        fig_tl = apply_stitch_plotly_theme(
                            fig_tl,
                            f"2023 Monthly Thermal Activity & Fire Radiative Power (MW): {html.escape(target_fac_name)}",
                        )
                        fig_tl.update_layout(
                            height=360,
                            yaxis=dict(title="VIIRS 375m Hotspot Count"),
                            yaxis2=dict(
                                title="Radiative Power (MW)",
                                overlaying="y",
                                side="right",
                                showgrid=False,
                            ),
                            legend=dict(orientation="h", y=1.12),
                        )
                        st.plotly_chart(fig_tl, use_container_width=True)

            proof_img_path = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "facility_imagery" / "stage2_visual_proof_duisburg.png"
            if proof_img_path.exists():
                with st.expander("🔬 View Full 4-Panel Spatial Verification Benchmark Figure (2D USGS Landsat-9 30m Thermal Heatmap + Freight Railcar Segmentation)", expanded=True):
                    st.image(
                        str(proof_img_path),
                        caption="Full 4-Panel Visual Verification on thyssenkrupp Steel Europe AG Werk Beeckerwerth (Duisburg): (A) VHR Optical Yard, (B) Freight Rail Siding & Stockpile Detection, (C) 2D USGS Landsat-9 30m Surface Temperature Heatmap showing the +25.1°C Blast Furnace Core Anomaly next to the Rhine River, and (D) 12-Month NASA FIRMS VIIRS 375m Continuous Operation Timeline.",
                        use_container_width=True,
                    )

            with st.expander("📊 View Full 30-Facility Stage 2 Multi-Sensor Benchmark Table (USGS M2M + NASA FIRMS + Planet Labs)", expanded=False):
                display_cols = [
                    "facility_name",
                    "sector",
                    "country",
                    "landsat_scene_id",
                    "plant_core_peak_lst_c",
                    "regional_bg_median_lst_c",
                    "thermal_delta_t_c",
                    "firms_hotspot_detections_2023",
                    "firms_active_months_count",
                    "firms_cumulative_frp_mw",
                    "planet_clear_passes_2023",
                    "planet_best_scene_id",
                    "vhr_rail_yard_contrast_index",
                    "vhr_stockpile_activity_index",
                    "thermal_activity_zscore",
                    "freight_logistics_zscore",
                ]
                st.dataframe(ms_df[display_cols].sort_values("thermal_delta_t_c", ascending=False), use_container_width=True)
        else:
            st.warning("Stage 2 Multi-Sensor dataset not found in cache.")

    with sat_tab_stage1:
        st.caption("ℹ️ **Stage 1 Baseline (Inconclusive / Underpowered Pilot Evidence):** Multi-year analysis (2019–2023) indicates that Sentinel-5P tropospheric NO₂ column density (5.5 × 3.5 km footprint) is not a reliable standalone quantitative proxy for annual plant-level CO₂ (mean within-plant Spearman ρ = -0.100). This motivated the Stage 2 upgrade to 30m/375m Thermal Infrared and 3m/VHR Optical Freight monitoring.")

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

        st.markdown("---")
        with st.expander("📋 Decision Matrix: Summary of Satellite Remote Sensing Diagnoses", expanded=True):
            st.markdown(
                r"""
                | Satellite Plume Verdict | Plume Contrast ($\sigma$) | Cloud Fraction | Non-Technical Operational Meaning | Verifier Recommendation |
                | :--- | :---: | :---: | :--- | :--- |
                | **Plume Concordant (Active Combustion)** | $z \ge +1.0\sigma$ | $\le 40\%$ | Clear tropospheric $\text{NO}_2$ plume detected above regional background; confirms continuous thermal combustion. | Corroborates declared high-volume production; indicates active plant firing. |
                | **Anomalously Weak Plume (Potential Ghost / Idling)** | $z < 0.0\sigma$ | $\le 40\%$ | No measurable combustion plume detected above background despite claiming large production volumes. | Investigate whether facility was idled, in cold shutdown, or declaring 'ghost production' from another site. |
                | **Elevated Plume Contrast (High Flare / Heavy Run)** | $z > +2.5\sigma$ | $\le 40\%$ | Strong atmospheric plume detected; suggests heavy continuous firing or potential flaring. | Cross-check declared output; ensures emissions were not under-reported relative to atmospheric footprint. |
                | **Inconclusive (Compromised Observation)** | Any | $> 50\%$ | Persistent cloud obscuration, snow cover, or missing satellite overpasses degrade sensor confidence. | **Do Not Penalize.** Remote sensing is inconclusive; rely on physical mass balance and ground audit records. |
                """
            )

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
        stoich_margin_sigma = st.slider(
            "Stoichiometric Safety Margin (Sigma above lower bound)",
            0.0,
            5.0,
            1.2,
            0.1,
            help="Safety margin in standard deviations above the chemical calcination/reduction floor. Values < 1.0σ approach physical limits.",
        )
        stoich_violated = st.checkbox(
            "Simulate Stoichiometric Physical Floor Violation",
            False,
            help="Toggle to simulate an explicit chemical mass-balance breach (reporting less than stoichiometric minimum). Triggers immediate hard veto.",
        )

        has_satellite = st.checkbox(
            "Include Copernicus Sentinel-5P Satellite Data (Auxiliary)",
            True,
            help="Toggle auxiliary Earth observation evidence from the Copernicus Sentinel-5P satellite.",
        )
        if has_satellite:
            sat_zscore = st.slider(
                "Satellite Plume Anomaly Z-Score (vs Regional Background)",
                -2.0,
                4.0,
                1.8,
                0.1,
                help="Normalized tropospheric NO₂ plume column density relative to clean 15–30 km regional background.",
            )
            sat_cloud = st.slider(
                "Satellite Cloud Obscuration Fraction",
                0.0,
                1.0,
                0.25,
                0.05,
                help="Fraction of cloudy days or cloudy pixels degrading satellite sensor confidence (high cloud reduces evidence weight).",
            )
        else:
            sat_zscore = None
            sat_cloud = 1.0

        has_temporal = st.checkbox(
            "Include Historical Time Series Baseline",
            True,
            help="Toggle historical multi-year emissions registry baseline evidence (E-PRTR / IED).",
        )
        if has_temporal:
            temp_zscore = st.slider(
                "Sudden Emission Drop Anomaly max(0, -z)",
                0.0,
                4.0,
                0.8,
                0.1,
                help="One-sided sudden drop anomaly score max(0, -z). High values indicate abnormal decreases compared to past years.",
            )
            years_hist = st.slider(
                "Available Historical Reference Years",
                1,
                6,
                5,
                help="Number of continuous historical reporting years available in public environmental registers (more years = higher confidence).",
            )
        else:
            temp_zscore = None
            years_hist = 0

        has_registry = st.checkbox(
            "Include Registry Capacity Check",
            False,
            help="Toggle independent plant capacity registry verification (e.g., Global Energy Monitor database).",
        )
        reg_ratio = (
            st.slider(
                "Claimed Production vs GEM Registry Capacity Ratio",
                0.5,
                1.5,
                1.0,
                0.05,
                help="Ratio of declared production to licensed nameplate plant capacity. Values > 1.2 suggest unverified over-capacity.",
            )
            if has_registry
            else 1.0
        )

        has_stage2_eo = st.checkbox(
            "Include Stage 2 Thermal Kiln/Furnace (USGS/FIRMS) & Freight Railcars (Planet/VHR)",
            True,
            help="Toggle Stage 2 multi-sensor thermal infrared (Landsat 30m / VIIRS 375m) and optical freight logistics (Planet 3m / VHR) streams.",
        )
        if has_stage2_eo:
            therm_zscore = st.slider(
                "Thermal Infrared Kiln/Furnace Anomaly Z-Score (Landsat 30m ΔT + VIIRS 375m FRP)",
                -2.0,
                4.5,
                2.4,
                0.1,
                help="Standardized localized thermal heat anomaly over the blast furnace or rotary kiln core.",
            )
            freight_zscore = st.slider(
                "Optical Freight Rail-Yard & Stockpile Activity Z-Score (Planet 3m + VHR)",
                -2.0,
                4.5,
                1.6,
                0.1,
                help="Standardized rail-yard rolling-stock contrast and raw-material stockpile occupancy index.",
            )
        else:
            therm_zscore = None
            freight_zscore = None

    ev = EvidenceInput(
        stoichiometric_discrepancy_sigma=stoich_margin_sigma,
        stoichiometric_violated=stoich_violated,
        satellite_plume_anomaly_zscore=sat_zscore,
        satellite_cloud_fraction=sat_cloud,
        temporal_variance_zscore=temp_zscore,
        years_reported_history=years_hist,
        registry_capacity_ratio=reg_ratio if has_registry else None,
        thermal_anomaly_zscore=therm_zscore,
        thermal_operating_months_ratio=0.92 if has_stage2_eo else None,
        freight_logistics_zscore=freight_zscore,
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

    st.markdown("---")
    with st.expander("📋 Decision Matrix: Summary of Multimodal Bayesian Posterior Risk Classifications", expanded=True):
        st.markdown(
            r"""
            | Multimodal Verdict | Status Badge | Posterior Risk $P(H \mid E)$ | Evidence Confidence $C_{\text{overall}}$ | Meaning for Non-Technical Users | Regulatory Workflow Action |
            | :--- | :---: | :---: | :---: | :--- | :--- |
            | **Consistent** | `CONSISTENT` | $< 25\%$ | $\ge 50\%$ | All available evidence streams (physics, history, satellite, registry) agree with the declaration. | **Clear for Expedited Verification.** No in-person audit required. |
            | **Potential Inconsistency** | `POTENTIAL INCONSISTENCY` | $25\% \le P \le 70\%$ | $\ge 50\%$ | Mild deviations detected in historical drop or satellite plume. Declaration is technically feasible but warrants scrutiny. | **Technical Clarification Request.** Importer must provide fuel invoices, CEMS logs, and clinker ratios. |
            | **High Inconsistency Risk** | `HIGH INCONSISTENCY RISK` | $> 70\%$ or Veto | $\ge 50\%$ | Physical floor breach or combined multi-stream anomalies indicate high probability of under-reporting. | **Mandatory On-Site Physical Inspection.** Flag declaration to customs; freeze clearance of CBAM certificates. |
            | **Insufficient Evidence** | `INSUFFICIENT EVIDENCE` | Any | $< 50\%$ | Data streams are missing or degraded (heavy clouds, no historical records). System refuses to guess. | **Defer Automated Decision.** Conduct standard independent third-party physical verifier audit without remote bias. |
            """
        )

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

    st.info(
        "📖 **Detailed Scientific Evaluation Guide Available:** "
        "For an exhaustive technical breakdown of metric formulations (ROC-AUC with 95% bootstrap CIs, PR-AUC, Brier score, ECE, Authentic FPR), "
        "model architectures (Models A through E2), theoretical optimal values vs achievable bounds, and the dual-stage operational recommendation, "
        "consult the project guide: `docs/TAB_7_EMPIRICAL_BENCHMARK_GUIDE.md`."
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

        display_cols = ["model_name", "roc_auc", "pr_auc", "brier_score", "ece", "fpr_authentic"]
        if "recall_at_fpr_5" in df_summary.columns:
            display_cols.extend(["recall_at_fpr_5", "recall_at_fpr_10", "recall_at_fpr_20", "abstention_rate"])
        display_df = df_summary[display_cols].copy()
        
        col_rename = {
            "model_name": "Model Architecture",
            "roc_auc": "ROC-AUC",
            "pr_auc": "PR-AUC",
            "brier_score": "Brier Score",
            "ece": "ECE",
            "fpr_authentic": "Authentic FPR",
            "recall_at_fpr_5": "Recall@5% FPR",
            "recall_at_fpr_10": "Recall@10% FPR",
            "recall_at_fpr_20": "Recall@20% FPR",
            "abstention_rate": "Abstention Rate",
        }
        display_df.rename(columns=col_rename, inplace=True)
        fmt_dict = {
            "ROC-AUC": "{:.4f}",
            "PR-AUC": "{:.4f}",
            "Brier Score": "{:.4f}",
            "ECE": "{:.4f}",
            "Authentic FPR": "{:.2%}",
            "Recall@5% FPR": "{:.2%}",
            "Recall@10% FPR": "{:.2%}",
            "Recall@20% FPR": "{:.2%}",
            "Abstention Rate": "{:.1%}",
        }
        st.dataframe(
            display_df.style.format({k: v for k, v in fmt_dict.items() if k in display_df.columns}),
            use_container_width=True,
        )

        st.info(
            "💡 **Key Methodological Finding (Step 6):** At matched false-positive rates (FPR = 5%, 10%, 20%), "
            "Model D (Historical Trajectory Alone: Recall@5% = 83.3%, Recall@10% = 90.8%) performs on par with "
            "Model E2 (Learned Logistic: Recall@5% = 85.0%, Recall@10% = 91.7%). The learned multimodal classifier does not "
            "meaningfully exceed historical anomaly detection at matched false alarms. Multimodal Bayesian fusion (Model E1) "
            "serves a distinct legal and operational purpose: physical sanity-checking, boundary-aware constraint enforcement, "
            "and confidence-gated audit trails with near-zero authentic false positives (0.56% FPR)."
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
            st.caption("Simulating customs capacity constraint: audit top k% highest-risk declarations against random sampling baseline (36.9% positive prevalence).")
            df_triage = pd.read_csv(triage_csv)
            triage_cols = [c for c in [
                "k_pct", "k_cases", "random_baseline_precision",
                "e1_bayes_caught", "e1_bayes_precision", "e1_bayes_recall", "e1_bayes_lift",
                "e2_logistic_caught", "e2_logistic_precision", "e2_logistic_recall", "e2_logistic_lift"
            ] if c in df_triage.columns]
            st.dataframe(
                df_triage[triage_cols].style.format({
                    "k_pct": "Top {}%",
                    "random_baseline_precision": "{:.1%}",
                    "e1_bayes_precision": "{:.1%}",
                    "e1_bayes_recall": "{:.1%}",
                    "e1_bayes_lift": "{:.2f}x",
                    "e2_logistic_precision": "{:.1%}",
                    "e2_logistic_recall": "{:.1%}",
                    "e2_logistic_lift": "{:.2f}x",
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

    st.markdown("---")
    with st.expander("📋 Decision Matrix: Summary of Evaluated Model Architectures & Deployment Roles", expanded=True):
        st.markdown(
            r"""
            | Model Architecture | Statistical Paradigm | ROC-AUC | PR-AUC | Authentic FPR | Recall @ 5% FPR | Abstention | Recommended Deployment Role |
            | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
            | **Model A: Naive Prior** | Constant Baseline ($P=0.08$) | 0.5000 | 0.3692 | 0.00% | 0.00% | 0.0% | Null benchmark baseline |
            | **Model B: Stoichiometry Alone** | Route-Specific Engineering Lower Bound | 0.7909 | 0.7326 | 1.55% | 33.73% | 28.6% | Hard physical veto gate (when boundaries & capacity permit) |
            | **Model C: Satellite Alone** | Tropospheric $\text{NO}_2$ Column Plume | 0.5183 | 0.3781 | 96.61% | 6.67% | 0.0% | Auxiliary qualitative check ($w \le 1.0$) |
            | **Model D: Historical Alone** | Robust Longitudinal Drop $\max(0, -z)$ | 0.9631 | 0.9428 | 6.78% | 83.33% | 0.0% | Primary historical statistical anomaly detector |
            | **Model E1: Expert Bayesian Fusion** | Probabilistic Log-Odds + Confidence Gating | 0.8935 | 0.8684 | 0.56% | 69.17% | 0.0% | **Stage 2: Accredited Verifier Audit Dossier (Near-zero false alarms: 0.56%)** |
            | **Model E2: Learned Logistic Regression** | Supervised Feature Fusion (GroupKFold) | 0.9643 | 0.9484 | 6.78% | 85.00% | 0.0% | **Stage 1: High-Throughput Customs Port Triage (Max recall & lift)** |
            """
        )

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
            - **Institution:** University of Europe for Applied Sciences (UE Germany), Potsdam Campus
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
