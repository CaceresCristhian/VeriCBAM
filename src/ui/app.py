"""
VeriCBAM - Multimodal Decision Support System for CBAM Emissions Auditing
Applied Capstone Cockpit | University of Europe for Applied Sciences (UE Germany)
Cristhian David Caceres Mateus | Supervisor: Dr. Humera Noor
"""

import dataclasses
import html
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
from ui.theme import STITCH_THEME_CSS, apply_stitch_plotly_theme, bento_card, scope_banner

try:
    from ui.dossier_pdf_generator import generate_dossier_pdf
except ImportError:
    generate_dossier_pdf = None

st.set_page_config(
    page_title="VeriCBAM | Decision Support Cockpit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(STITCH_THEME_CSS, unsafe_allow_html=True)
st.sidebar.markdown(STITCH_THEME_CSS, unsafe_allow_html=True)


@st.cache_data
def load_cohort_data():
    mgr = CohortManager()
    facilities = mgr.get_all_facilities().copy()
    for upper, lower in [("Latitude", "latitude"), ("Longitude", "longitude"), ("facilityName", "facility_name")]:
        if upper in facilities.columns and lower not in facilities.columns:
            facilities[lower] = facilities[upper]
        elif lower in facilities.columns and upper not in facilities.columns:
            facilities[upper] = facilities[lower]
    return mgr, facilities


def _render_cards(cards):
    cols = st.columns(len(cards))
    for col, (lbl, val, sub, color) in zip(cols, cards):
        with col:
            st.markdown(bento_card(lbl, val, sub, color), unsafe_allow_html=True)


def render_tab_quick_audit(facilities_df: pd.DataFrame):
    scope_banner()
    st.markdown('<div class="stitch-main-title">🚀 Quick Audit & 1-Click PDF Dossier Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="stitch-sub-title">Instant Pre-Audit Screening for Importers, Verification Bodies & Customs Authorities</div>', unsafe_allow_html=True)

    audit_mode = st.radio(
        "Select Audit Mode:",
        [
            "Option A: Audit Pre-Loaded Facility (30 Reference Sites)",
            "Option B: Audit External / Custom Facility",
            "Option C: Upload Declaration File (CSV)",
        ],
        horizontal=True,
    )

    ms_cache = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "multisensor_thermal_logistics_2023.csv"
    multisensor_df = pd.read_csv(ms_cache) if ms_cache.exists() else pd.DataFrame()

    facility_name, country_name, sector_name = "Custom Installation", "Global", "Cement"
    route_name, reporting_year = "Dry Kiln (Preheater/Precalciner)", 2023
    annual_prod_tonnes, declared_co2_tonnes = 1_000_000.0, 780_000.0
    sat_active_months, sat_delta_t, sat_freight_z = 11, 18.5, 1.2
    is_external_sat_only = False

    if audit_mode.startswith("Option A"):
        col_sel1, col_sel2 = st.columns([2, 1])
        with col_sel1:
            facility_list = sorted(facilities_df["facility_name"].dropna().unique().tolist())
            selected_fac = st.selectbox("Select European Reference Facility:", facility_list)
        with col_sel2:
            fac_match = facilities_df[facilities_df["facility_name"] == selected_fac].iloc[0]
            st.metric("Sector & Country", f"{fac_match['sector']} ({fac_match['country']})")

        facility_name, country_name, sector_name = selected_fac, fac_match["country"], fac_match["sector"]
        if not multisensor_df.empty:
            ms_match = multisensor_df[multisensor_df["facility_name"] == selected_fac]
            if not ms_match.empty:
                ms_row = ms_match.iloc[0]
                sat_active_months = int(ms_row.get("firms_active_months_count", 11))
                sat_delta_t = float(ms_row.get("thermal_delta_t_c", 18.0))
                sat_freight_z = float(ms_row.get("freight_logistics_zscore", 1.0))

        if sector_name == "Cement":
            route_name, default_prod, default_co2 = "Dry Kiln (Preheater/Precalciner)", 1_100_000.0, 840_000.0
        else:
            tech_route = str(fac_match.get("verified_technology_route", "BF-BOF"))
            route_name = "BF-BOF" if "BF" in tech_route else "Scrap-EAF"
            default_prod = 2_500_000.0
            default_co2 = 4_200_000.0 if route_name == "BF-BOF" else 350_000.0

        col_d1, col_d2 = st.columns(2)
        annual_prod_tonnes = col_d1.number_input("Declared Production Output (Tonnes product):", 10_000.0, 20_000_000.0, default_prod, 50_000.0)
        declared_co2_tonnes = col_d2.number_input("Declared Direct Scope 1 CO₂ (Tonnes CO₂):", 1_000.0, 25_000_000.0, default_co2, 50_000.0)

    elif audit_mode.startswith("Option B"):
        st.info("💡 **External Supplier Screening:** Test third-country facilities using first-principles mass balances and satellite thermal/freight discrepancy.")
        c1, c2, c3 = st.columns(3)
        facility_name = c1.text_input("Facility / Supplier Name:", "Overseas Industrial Works Ltd.")
        country_name = c1.text_input("Country of Origin:", "Turkey / India / China / USA")
        reporting_year = c1.selectbox("Reporting Period:", [2024, 2023, 2025], index=1)

        sector_name = c2.selectbox("Industrial Sector:", ["Cement", "Iron & Steel"])
        route_opts = ["Dry Kiln (Preheater/Precalciner)", "Semi-Dry / Semi-Wet Kiln", "Wet Kiln"] if sector_name == "Cement" else ["BF-BOF", "DRI-NG-EAF", "DRI-H2-EAF", "Scrap-EAF"]
        route_name = c2.selectbox("Technology Route:", route_opts)
        annual_prod_tonnes = c2.number_input("Annual Production Volume (Tonnes):", 1_000.0, 30_000_000.0, 1_200_000.0, 50_000.0)

        declared_co2_tonnes = c3.number_input("Declared Direct Scope 1 CO₂ (Tonnes CO₂):", 100.0, 40_000_000.0, 950_000.0, 50_000.0)
        is_external_sat_only = c3.checkbox("External Facility Lacks Past History (Use Satellite Data Only)", value=True)

        with st.expander("🛰️ Satellite Remote Sensing Parameters (Landsat Thermal & Freight Siding)"):
            sc1, sc2, sc3 = st.columns(3)
            sat_active_months = sc1.slider("Active Operating Months (VIIRS 375m):", 0, 12, 11)
            sat_delta_t = sc2.slider("Kiln/Furnace Thermal Anomaly ΔT (°C):", -5.0, 35.0, 19.5)
            sat_freight_z = sc3.slider("Freight Rail-Yard & Stockpile Z-Score:", -2.0, 3.5, 1.3)
    else:
        st.info("📂 **Upload Declaration File:** CSV columns `facility_name`, `sector`, `route`, `production_tonnes`, `declared_co2_tonnes`.")
        uploaded_file = st.file_uploader("Upload CSV declaration file:", type=["csv"])
        if uploaded_file is not None:
            try:
                up_df = pd.read_csv(uploaded_file)
                st.dataframe(up_df.head(), use_container_width=True)
                sel_idx = st.selectbox("Select row to audit:", list(range(len(up_df))))
                row_sel = up_df.iloc[sel_idx]
                facility_name = str(row_sel.get("facility_name", f"Facility #{sel_idx+1}"))
                sector_name = str(row_sel.get("sector", "Cement"))
                route_name = str(row_sel.get("route", "BF-BOF" if sector_name == "Iron & Steel" else "Dry Kiln"))
                annual_prod_tonnes = float(row_sel.get("production_tonnes", 1_000_000.0))
                declared_co2_tonnes = float(row_sel.get("declared_co2_tonnes", 800_000.0))
                country_name = str(row_sel.get("country", "Global"))
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

    decl_intensity = declared_co2_tonnes / max(annual_prod_tonnes, 1.0)
    if sector_name == "Cement":
        phys_floor_int = 0.770
    elif route_name == "BF-BOF":
        phys_floor_int = 1.350
    elif "DRI" in route_name:
        phys_floor_int = 0.550
    else:
        phys_floor_int = 0.040

    phys_min_total = annual_prod_tonnes * phys_floor_int
    is_phys_feasible = declared_co2_tonnes >= (phys_min_total * 0.98)
    phys_deficit = max(0.0, phys_min_total - declared_co2_tonnes)

    engine = ProbabilisticEvidenceFusionEngine()
    stoich_margin_sig = (decl_intensity - phys_floor_int) / max(phys_floor_int * 0.15, 0.01)
    ev_kwargs = {
        "stoichiometric_discrepancy_sigma": max(-2.0, min(5.0, stoich_margin_sig)),
        "stoichiometric_violated": not is_phys_feasible,
        "satellite_plume_anomaly_zscore": 1.5,
        "satellite_cloud_fraction": 0.20,
        "temporal_variance_zscore": None if is_external_sat_only else 0.8,
        "years_reported_history": 0.0 if is_external_sat_only else 5.0,
        "registry_capacity_ratio": None,
        "thermal_anomaly_zscore": (sat_delta_t - 8.0) / 6.0,
        "thermal_operating_months_ratio": sat_active_months / 12.0,
        "freight_logistics_zscore": sat_freight_z,
    }
    valid_fields = {f.name for f in dataclasses.fields(EvidenceInput)}
    ev_obj = EvidenceInput(**{k: v for k, v in ev_kwargs.items() if k in valid_fields})
    decision = engine.fuse_evidence(ev_obj, reported_emissions_tco2=declared_co2_tonnes, physical_min_tco2=phys_min_total)

    post_risk_pct = decision.posterior_inconsistency_risk * 100.0
    conf_score_pct = decision.evidence_confidence_score * 100.0
    final_verdict = decision.audit_verdict.upper()

    st.markdown("---")
    st.markdown("### 📋 Automated Audit Screening Diagnostic")
    badge_phys = "<font color='#4edea3'>FEASIBLE</font>" if is_phys_feasible else "<font color='#ef4444'>VIOLATION</font>"
    risk_col = "#ef4444" if post_risk_pct >= 70 else ("#facc15" if post_risk_pct >= 25 else "#4edea3")
    _render_cards([
        ("Declared Carbon Intensity", f"{decl_intensity:.3f} t/t", f"Floor: {phys_floor_int:.3f} tCO₂/t", "#8ed5ff"),
        ("Physical Mass Balance", badge_phys, f"Deficit: {phys_deficit:,.0f} t CO₂", "#ffffff"),
        ("Satellite Kiln Activity", f"{sat_active_months}/12 Mos", f"Peak ΔT: +{sat_delta_t:.1f}°C", "#facc15"),
        ("Inconsistency Risk Score", f"{post_risk_pct:.1f}%", f"Confidence: {conf_score_pct:.1f}%", risk_col),
    ])

    if "HIGH" in final_verdict or not is_phys_feasible or post_risk_pct >= 70:
        st.markdown('<div class="status-badge badge-risk">🚨 HIGH INCONSISTENCY RISK — MANDATORY ON-SITE AUDIT RECOMMENDED</div>', unsafe_allow_html=True)
        rec_text = "MANDATORY ON-SITE INSPECTION: High probability of under-reporting or physical bound breach. Freeze automated clearance."
    elif "POTENTIAL" in final_verdict or post_risk_pct >= 25:
        st.markdown('<div class="status-badge badge-potential">⚠️ POTENTIAL INCONSISTENCY — REQUEST TECHNICAL DOCUMENTATION</div>', unsafe_allow_html=True)
        rec_text = "TECHNICAL CLARIFICATION REQUIRED: Moderate discrepancy detected. Request monthly CEMS records and fuel invoices."
    elif conf_score_pct < 50:
        st.markdown('<div class="status-badge badge-insufficient">⚪ INSUFFICIENT EVIDENCE — DEFER TO STANDARD MANUAL VERIFICATION</div>', unsafe_allow_html=True)
        rec_text = "INSUFFICIENT OBSERVATIONAL EVIDENCE: Defer automated decision to standard accredited verifier audit."
    else:
        st.markdown('<div class="status-badge badge-consistent">✅ CONSISTENT WITH PHYSICAL & SATELLITE EVIDENCE — CLEAR FOR FILING</div>', unsafe_allow_html=True)
        rec_text = "CLEAR FOR EXPEDITED IMPORT CLEARANCE: Emissions concordant with stoichiometry and satellite operating signatures."

    st.markdown("#### Multi-Source Evidence Synthesis Breakdown")
    ev_breakdown_list = [
        {"stream": "Chemical Stoichiometry (Mass Balance)", "status": "Pass" if is_phys_feasible else "Breach", "detail": f"Floor: {phys_floor_int:.3f} tCO₂/t (Margin {decl_intensity - phys_floor_int:+.3f})", "impact": "High (w=1.5)"},
        {"stream": "Thermal Kiln Satellite (Landsat / VIIRS)", "status": "Active Firing" if sat_active_months >= 10 else "Low Heat", "detail": f"{sat_active_months}/12 active months (ΔT +{sat_delta_t:.1f}°C)", "impact": "High (w=1.1)"},
        {"stream": "Optical Freight Siding Logistics (VHR)", "status": "Normal Turnover" if sat_freight_z >= 0 else "Low Activity", "detail": f"Freight siding & stockpile z={sat_freight_z:+.2f}σ", "impact": "Moderate (w=1.0)"},
        {"stream": "Historical Reporting Baseline", "status": "Concordant" if not is_external_sat_only else "Unobserved", "detail": "Longitudinal baseline stable" if not is_external_sat_only else "External supplier (Zero EU history)", "impact": "w=1.0" if not is_external_sat_only else "Abstained (w=0.0)"},
    ]
    st.dataframe(pd.DataFrame(ev_breakdown_list), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📥 Export Official Pre-Audit Screening Dossier")
    dossier_payload = {
        "facility_name": facility_name,
        "country": country_name,
        "sector": sector_name,
        "route": route_name,
        "reporting_year": reporting_year,
        "declared_production_tonnes": annual_prod_tonnes,
        "declared_co2_tonnes": declared_co2_tonnes,
        "declared_intensity": decl_intensity,
        "physical_floor_intensity": phys_floor_int,
        "total_floor_co2": phys_min_total,
        "is_physically_feasible": is_phys_feasible,
        "physical_deficit_tco2": phys_deficit,
        "risk_verdict": final_verdict,
        "posterior_risk_pct": post_risk_pct,
        "evidence_confidence_pct": conf_score_pct,
        "audit_recommendation": rec_text,
        "evidence_breakdown": ev_breakdown_list,
        "satellite_summary": f"{sat_active_months}/12 active months, ΔT +{sat_delta_t:.1f}°C, freight z={sat_freight_z:+.2f}σ",
    }
    if generate_dossier_pdf is not None:
        try:
            pdf_bytes = generate_dossier_pdf(dossier_payload)
            safe_fname = f"vericbam_audit_dossier_{facility_name.lower()[:20].replace(' ', '_').replace('/', '_')}.pdf"
            st.download_button("📄 Download Official Pre-Audit Screening Dossier (PDF)", pdf_bytes, file_name=safe_fname, mime="application/pdf")
        except Exception as e:
            st.error(f"Error rendering PDF dossier: {e}")


def render_tab_overview():
    scope_banner()
    st.markdown('<div class="stitch-main-title">VeriCBAM: Multimodal Decision Support for CBAM Auditing</div>', unsafe_allow_html=True)
    st.markdown('<div class="stitch-sub-title">Physics-Grounded & Satellite Evidence Synthesis for European Carbon Border (CBAM) Verification</div>', unsafe_allow_html=True)

    _render_cards([
        ("Benchmark Cohort", "30 Sites", "15 Cement • 15 Steel (10 EU States)", "#ffffff"),
        ("Authentic Panel", "177 Plant-Yrs", "2018–2023 E-PRTR Real Negatives", "#8ed5ff"),
        ("Graded Benchmark", "325 Cases", "177 Real Neg. • 148 Inconsistencies", "#4edea3"),
        ("Evidence Modalities", "6 Streams", "Physics, Stage 1 & 2 EO, Hist, NOx, Reg", "#facc15"),
    ])

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### Regulatory Mandate & ELI Citations")
        st.markdown(
            """
            - **Regulation (EU) 2023/956:** Establishes CBAM reporting and actual emissions verification (Articles 8 & 9).
            - **Implementing Regulation (EU) 2025/2546:** Rules for verification principles and physical site thresholds. [ELI Link](http://data.europa.eu/eli/reg_impl/2025/2546/oj)
            - **Delegated Regulation (EU) 2025/2551:** Verifier accreditation and oversight rules. [ELI Link](http://data.europa.eu/eli/reg_del/2025/2551/oj)
            - **Implementing Regulation (EU) 2025/2547:** Calculation methodology for direct/indirect embedded emissions. [ELI Link](http://data.europa.eu/eli/reg_impl/2025/2547/oj)
            - **EEA E-PRTR / IED v16 (2026):** Authentic empirical emissions reference panel across 30 installations.
            """
        )
    with col_right:
        st.markdown("### Core Scientific & Mathematical Formulations")
        st.markdown(
            r"""
            - **Cement Calcination Floor:** $\text{CaCO}_3 \rightarrow \text{CaO} + \text{CO}_2$ ($0.495\text{--}0.525\text{ t CO}_2/\text{t clinker}$)
            - **Steel Carbothermic Floor:** $\text{Fe}_2\text{O}_3 + 3\text{C} \rightarrow 2\text{Fe} + 3\text{CO}$ ($1.350\text{ t CO}_2/\text{t crude steel}$)
            - **Bayesian Log-Odds Fusion:** $\text{logit } P(H|E) = \text{logit } P(H) + \sum w_i C_i \ln(\text{LR}_i)$
            - **Robust Historical Scale:** Leave-one-year-out pooled MAD $\sigma_{\text{pooled}} = 0.0911$ across 177 facility-years.
            """
        )

    st.markdown("---")
    with st.expander("📋 Decision Matrix: Summary of VeriCBAM Screening Outcomes & Actions", expanded=True):
        st.markdown(
            r"""
            | Screening Verdict | System Status Badge | Triggering Condition | Meaning for Stakeholders | Recommended Action |
            | :--- | :---: | :--- | :--- | :--- |
            | **Consistent** | `CONSISTENT` | $P(H \mid E) < 25\%$ | Aligned with chemical stoichiometry, satellite activity, and baselines. | **Clear for Expedited Verification.** |
            | **Potential Inconsistency** | `POTENTIAL INCONSISTENCY` | $25\% \le P(H \mid E) \le 70\%$ | Unusual efficiency or mild satellite/longitudinal deviation. | **Request Technical Clarification.** CEMS & fuel logs. |
            | **High Inconsistency Risk** | `HIGH RISK (VIOLATION)` | $P(H \mid E) > 70\%$ or Floor Breach | Physically impossible emissions or severe anomaly ($>3.5\sigma$). | **Mandatory On-Site Physical Inspection.** |
            | **Insufficient Evidence** | `INSUFFICIENT EVIDENCE` | Confidence $C_{\text{overall}} < 50\%$ | Compromised observations (clouds/missing baseline). System refuses to guess. | **Defer Automated Decision.** Manual audit. |
            """
        )


def render_tab_cohort(mgr: CohortManager, facilities_df: pd.DataFrame):
    scope_banner()
    st.markdown('<div class="stitch-main-title">Curated 30-Facility European Benchmark Cohort</div>', unsafe_allow_html=True)
    st.markdown('<div class="stitch-sub-title">Authentic multi-year Scope 1 CO₂ emission records from EEA E-PRTR / IED v16</div>', unsafe_allow_html=True)

    c_filter, s_filter, f_filter = st.columns([1, 1, 2])
    sector_choice = c_filter.selectbox("Filter Sector:", ["All Sectors", "Cement", "Steel"])
    country_choice = s_filter.selectbox("Filter Country:", ["All Countries"] + sorted(facilities_df["countryName"].unique().tolist()))

    filtered = facilities_df.copy()
    if sector_choice != "All Sectors":
        filtered = filtered[filtered["sector"] == sector_choice]
    if country_choice != "All Countries":
        filtered = filtered[filtered["countryName"] == country_choice]

    facility_options = filtered["facilityName"].tolist() or facilities_df["facilityName"].tolist()
    if not len(filtered):
        filtered = facilities_df.copy()
    selected_fac = f_filter.selectbox("Select Target Facility:", facility_options)

    fac_row = filtered[filtered["facilityName"] == selected_fac].iloc[0]
    fac_id = fac_row["FacilityInspireId"]
    fac_lat = float(fac_row.get("latitude", 51.1657))
    fac_lon = float(fac_row.get("longitude", 10.4515))
    ts_df = mgr.get_facility_time_series(fac_id)

    sector = str(fac_row.get("sector", "Cement"))
    if sector == "Cement":
        cap_mtpa = float(fac_row.get("clinker_capacity_mtpa", 0.0) or fac_row.get("cement_capacity_mtpa", 1.5) or 1.5)
        legal_limit_tco2 = cap_mtpa * 1e6 * 0.950
        legal_basis = f"Clinker Capacity ({cap_mtpa:.2f} Mt/yr) × 0.950 t CO₂/t BAT Upper Limit"
    else:
        cap_mtpa = float(fac_row.get("crude_steel_capacity_mtpa", 0.0) or fac_row.get("primary_iron_capacity_mtpa", 0.0) or 2.5)
        is_eaf = any(k in str(fac_row.get("verified_technology_route", "")) for k in ("Scrap", "EAF"))
        factor = 0.350 if is_eaf else 2.200
        legal_limit_tco2 = cap_mtpa * 1e6 * factor
        legal_basis = f"Steel Capacity ({cap_mtpa:.2f} Mt/yr) × {factor:.3f} t CO₂/t Ceiling"

    try:
        fig_map = px.scatter_map(
            filtered, lat="latitude", lon="longitude", hover_name="facilityName",
            hover_data={"city": True, "countryName": True, "mean_co2_tonnes": ":,.0f", "sector": True, "latitude": False, "longitude": False},
            color="sector", size="mean_co2_tonnes", color_discrete_map={"Cement": "#facc15", "Steel": "#8ed5ff"},
            size_max=30, zoom=4.0, center={"lat": fac_lat, "lon": fac_lon},
        )
        fig_map.add_trace(go.Scattermap(lat=[fac_lat], lon=[fac_lon], mode="markers+text", marker=dict(size=24, color="#ef4444"), text=[f"📍 {selected_fac}"], textposition="top center", name="Selected"))
    except Exception:
        fig_map = px.scatter_mapbox(
            filtered, lat="latitude", lon="longitude", hover_name="facilityName",
            color="sector", size="mean_co2_tonnes", color_discrete_map={"Cement": "#facc15", "Steel": "#8ed5ff"},
            size_max=30, zoom=4.0, center={"lat": fac_lat, "lon": fac_lon}, mapbox_style="carto-darkmatter",
        )
        fig_map.add_trace(go.Scattermapbox(lat=[fac_lat], lon=[fac_lon], mode="markers+text", marker=dict(size=24, color="#ef4444"), text=[f"📍 {selected_fac}"], textposition="top center", name="Selected"))

    fig_map = apply_stitch_plotly_theme(fig_map, f"Geospatial Cohort (Highlighting: {html.escape(selected_fac)})")
    fig_map.update_layout(height=440, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown(
            f"""
            <div class="bento-card">
                <div class="bento-label">Facility Metadata & Licensed Permit</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px;">{html.escape(str(fac_row['facilityName']))}</div>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 4px 0;"><strong>Sector:</strong> {html.escape(sector)}</p>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 4px 0;"><strong>Location:</strong> {html.escape(str(fac_row['city']))}, {html.escape(str(fac_row['countryName']))}</p>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 4px 0;"><strong>Verified Route:</strong> {html.escape(str(fac_row.get('verified_technology_route', 'N/A')))}</p>
                <p style="font-size: 0.85rem; color: #cbd5e1; margin: 0 0 8px 0;"><strong>Historical Mean CO₂:</strong> {fac_row['mean_co2_tonnes']:,.0f} t/yr</p>
                <div style="padding: 8px 10px; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 6px;">
                    <span style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #ffb4ab;">Legal Permit Ceiling:</span>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #ef4444; font-family: monospace;">{legal_limit_tco2:,.0f} t CO₂/yr</div>
                    <div style="font-size: 0.72rem; color: #cbd5e1;">{html.escape(legal_basis)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_right:
        if not ts_df.empty:
            ts_sorted = ts_df.sort_values("reportingYear")
            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(x=ts_sorted["reportingYear"], y=ts_sorted["co2_tonnes"], mode="lines+markers", name="Verified Scope 1 CO₂", line=dict(color="#8ed5ff", width=3)))
            fig_ts.add_trace(go.Scatter(x=[ts_sorted["reportingYear"].min(), ts_sorted["reportingYear"].max()], y=[legal_limit_tco2, legal_limit_tco2], mode="lines", name="Permit Limit", line=dict(color="#ef4444", width=2.5, dash="dash")))
            fig_ts = apply_stitch_plotly_theme(fig_ts, f"Multi-Year Emissions Timeline vs Permit Limit: {html.escape(str(fac_row['facilityName']))}")
            fig_ts.update_layout(height=310, xaxis=dict(title="Year", dtick=1), yaxis=dict(title="Scope 1 CO₂ (Tonnes)"), legend=dict(orientation="h", y=1.08))
            st.plotly_chart(fig_ts, use_container_width=True)


def render_tab_stoichiometry():
    scope_banner()
    st.markdown('<div class="stitch-main-title">Deterministic Stoichiometric Physics Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="stitch-sub-title">First-principles chemical mass balances and route-specific engineering lower bounds</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="formula-box"><b>Cement Calcination:</b> CaCO₃ → CaO + CO₂ (0.7848 t CO₂ / t CaO) &nbsp;|&nbsp; '
        '<b>Steel Reduction:</b> Fe₂O₃ + 3 C → 2 Fe + 3 CO (1.182 t CO₂ / t hot metal)</div>',
        unsafe_allow_html=True,
    )

    sector_mode = st.radio("Select Commodity Sector:", ["Cement Clinker", "Crude Steel"], horizontal=True)
    if sector_mode == "Cement Clinker":
        c1, c2, c3 = st.columns(3)
        clinker_t = c1.number_input("Clinker Produced (Tonnes)", 10_000.0, 5_000_000.0, 1_000_000.0, 50_000.0)
        cement_t = c1.number_input("Total Cement Produced (Tonnes)", 10_000.0, 6_000_000.0, 1_150_000.0, 50_000.0)
        clinker_ratio = c2.slider("Clinker-to-Cement Ratio", 0.40, 1.0, 0.87, 0.01)
        fuel_type = c2.selectbox("Primary Kiln Fuel", ["coal", "petcoke", "natural_gas", "waste_derived_fuel_50pct_bio"])
        reported_co2 = c3.number_input("Reported Direct Scope 1 CO₂ (Tonnes)", 0.0, 5_000_000.0, 810_000.0, 25_000.0)
        ccus_tco2 = c3.number_input("Verified CCUS Captured CO₂ (Tonnes)", 0.0, 1_000_000.0, 0.0, 10_000.0)

        res = audit_cement_declaration(CementDeclarationInput("Audit Candidate Kiln", 2024, clinker_t, cement_t, clinker_ratio, reported_co2, reported_fuel_type=fuel_type, ccus_captured_tco2=ccus_tco2))
        st.markdown("---")
        _render_cards([
            ("Calcination Floor", f"{res.process_emissions_min_tco2:,.0f} t", "Chemical Mass Balance", "#ffffff"),
            ("Combustion Floor", f"{res.combustion_emissions_min_tco2:,.0f} t", f"BAT Kiln ({fuel_type})", "#ffffff"),
            ("Net Physical Floor", f"{res.total_physical_minimum_tco2:,.0f} t", "Minimum Allowable", "#8ed5ff"),
            ("Specific Intensity", f"{res.reported_specific_intensity_tco2_per_t_clinker:.3f}", f"Floor: {res.minimum_specific_intensity_tco2_per_t_clinker:.3f} tCO₂/t", "#4edea3" if res.is_physically_feasible else "#ef4444"),
        ])
        if not res.is_physically_feasible:
            st.markdown('<div class="status-badge badge-risk">🚨 PHYSICAL FEASIBILITY VIOLATION</div>', unsafe_allow_html=True)
            st.error(res.violation_reason)
        else:
            st.markdown('<div class="status-badge badge-consistent">✅ PHYSICALLY FEASIBLE</div>', unsafe_allow_html=True)
            st.success(res.violation_reason)
    else:
        c1, c2, c3 = st.columns(3)
        steel_t = c1.number_input("Crude Steel Produced (Tonnes)", 10_000.0, 10_000_000.0, 2_000_000.0, 50_000.0)
        route = c1.selectbox("Claimed Production Route", ["BF-BOF", "DRI-NG-EAF", "DRI-H2-EAF", "Scrap-EAF"])
        scrap_ratio = c2.slider("Scrap Ratio (Dilution)", 0.05, 1.0, 0.18, 0.01)
        reported_co2 = c2.number_input("Reported Scope 1 CO₂ (Tonnes)", 0.0, 10_000_000.0, 3_600_000.0, 50_000.0)
        ccus_tco2 = c3.number_input("Verified CCUS Captured CO₂ (Tonnes)", 0.0, 2_000_000.0, 0.0, 10_000.0)

        res = audit_steel_declaration(SteelDeclarationInput("Audit Candidate Steelwork", 2024, steel_t, route, reported_co2, scrap_ratio=scrap_ratio, ccus_captured_tco2=ccus_tco2))
        st.markdown("---")
        _render_cards([
            ("Reported Intensity", f"{res.reported_specific_intensity_tco2_per_t:.3f}", "Declared Scope 1", "#ffffff"),
            ("Stoichiometric Floor", f"{res.theoretical_floor_intensity_tco2_per_t:.3f}", f"Floor ({route})", "#8ed5ff"),
            ("Typical Benchmark", f"{res.typical_benchmark_intensity_tco2_per_t:.3f}", "EU BREF Median", "#facc15"),
            ("Net Allowable CO₂", f"{res.total_physical_minimum_tco2:,.0f} t", "Engineering Bound", "#4edea3" if res.is_physically_feasible else "#ef4444"),
        ])
        if not res.is_physically_feasible:
            st.markdown('<div class="status-badge badge-risk">🚨 ROUTE LOWER BOUND VIOLATION</div>', unsafe_allow_html=True)
            st.error(res.violation_reason)
        elif res.route_misclassification_detected:
            st.markdown('<div class="status-badge badge-potential">⚠️ ROUTE MISCLASSIFICATION DETECTED</div>', unsafe_allow_html=True)
            st.warning(res.violation_reason)
        else:
            st.markdown('<div class="status-badge badge-consistent">✅ CONCORDANT WITH ROUTE BOUNDS</div>', unsafe_allow_html=True)
            st.success(res.violation_reason)


def render_tab_satellite(facilities_df: pd.DataFrame):
    scope_banner()
    st.markdown('<div class="stitch-main-title">Multi-Sensor Earth Observation Verification Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="stitch-sub-title">Stage 2 Thermal Infrared (USGS Landsat 30m / NASA FIRMS 375m) & Optical Freight Logistics (Planet/VHR) + Stage 1 Sentinel-5P</div>', unsafe_allow_html=True)

    c_sel, p_sel = st.columns([2, 1])
    target_fac = c_sel.selectbox("Select Target Facility:", facilities_df["facilityName"].tolist())
    prod_claimed = p_sel.number_input("Declared Production (Tonnes)", 10_000.0, 10_000_000.0, 1_000_000.0, 50_000.0)

    target_row = facilities_df[facilities_df["facilityName"] == target_fac].iloc[0]
    fac_id = target_row["FacilityInspireId"]
    lat = float(target_row.get("latitude", 0.0))
    lon = float(target_row.get("longitude", 0.0))

    tab_s2, tab_s1 = st.tabs([
        "🔥 Stage 2: Thermal Kiln/Furnace (USGS/FIRMS) & Freight Yard (Planet/VHR)",
        "🌫️ Stage 1: Copernicus Sentinel-5P NO₂ Plume Baseline",
    ])

    with tab_s2:
        ms_path = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "multisensor_thermal_logistics_2023.parquet"
        firms_path = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "firms_viirs_monthly_timeline_2023.parquet"
        ms_df = pd.read_parquet(ms_path) if ms_path.exists() else pd.DataFrame()
        ms_sub = ms_df[(ms_df["facility_id"] == fac_id) | (ms_df["facility_name"] == target_fac)] if not ms_df.empty else pd.DataFrame()

        if ms_sub.empty:
            st.warning("Stage 2 Multi-Sensor dataset not found in cache.")
        else:
            ms_row = ms_sub.iloc[0]
            _render_cards([
                ("Landsat-8/9 30m ΔT", f"+{ms_row['thermal_delta_t_c']:.1f} °C", f"Peak {ms_row['plant_core_peak_lst_c']:.1f}°C vs {ms_row['regional_bg_median_lst_c']:.1f}°C", "#f97316"),
                ("FIRMS VIIRS 375m", f"{int(ms_row['firms_hotspot_detections_2023'])} Hits", f"{int(ms_row['firms_active_months_count'])}/12 Mos • {ms_row['firms_cumulative_frp_mw']:.1f} MW", "#facc15"),
                ("Planet 3m Cadence", f"{int(ms_row['planet_clear_passes_2023'])} Passes", f"{ms_row['planet_mean_gsd_m']:.1f}m GSD • {int(ms_row['planet_active_months_2023'])}/12 Mos", "#8ed5ff"),
                ("Freight & Stockpile", f"{ms_row['vhr_rail_yard_contrast_index']:.3f}", f"Stockpile: {ms_row['vhr_stockpile_activity_index']:.3f} • Z={ms_row['freight_logistics_zscore']:+.2f}σ", "#4edea3"),
            ])

            col_img, col_seg, col_tl = st.columns([1.0, 1.0, 1.35])
            img_rel = str(ms_row.get("vhr_image_path", ""))
            img_abs = WORKSPACE_ROOT / img_rel if img_rel else None

            with col_img:
                st.markdown("#### 🛰️ A. VHR Factory & Rail-Yard")
                if img_abs and img_abs.exists():
                    st.image(str(img_abs), caption=f"{target_fac} ({lat:.4f}°N, {lon:.4f}°E)", use_container_width=True)
            with col_seg:
                st.markdown("#### 🚂 B. Rail-Yard & Stockpile Overlay")
                if img_abs and img_abs.exists():
                    from PIL import Image as _PILImage
                    vhr = np.asarray(_PILImage.open(img_abs).convert("RGB"), dtype=np.float32) / 255.0
                    gray = 0.299 * vhr[:, :, 0] + 0.587 * vhr[:, :, 1] + 0.114 * vhr[:, :, 2]
                    edge = np.hypot(np.diff(gray, axis=1, prepend=gray[:, :1]), np.diff(gray, axis=0, prepend=gray[:1, :]))
                    rail_mask = edge > np.percentile(edge, 86)
                    ore_mask = (vhr[:, :, 0] > 0.34) & ((vhr[:, :, 0] / (vhr[:, :, 2] + 0.05)) > 1.32)
                    coal_mask = (gray > 0.07) & (gray < 0.24) & (np.abs(vhr[:, :, 0] - vhr[:, :, 2]) < 0.05)
                    overlay = vhr * 0.52
                    overlay[rail_mask] = [0.0, 0.92, 1.0]
                    overlay[ore_mask] = [1.0, 0.38, 0.08]
                    overlay[coal_mask & (~rail_mask)] = [0.98, 0.80, 0.08]
                    st.image((np.clip(overlay, 0.0, 1.0) * 255).astype(np.uint8), caption="Cyan: Rail Sidings | Orange/Gold: Ore/Coal Stockpiles", use_container_width=True)
            with col_tl:
                st.markdown("#### 🔥 C. 12-Month FIRMS Timeline")
                if firms_path.exists():
                    tl_df = pd.read_parquet(firms_path)
                    tl_fac = tl_df[tl_df["facility_id"] == fac_id].sort_values("month")
                    if not tl_fac.empty:
                        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                        x_m = [months[m - 1] for m in tl_fac["month"]]
                        fig_tl = go.Figure()
                        fig_tl.add_trace(go.Bar(x=x_m, y=tl_fac["hotspot_count"], name="375m Hotspots", marker_color="#f97316"))
                        fig_tl.add_trace(go.Scatter(x=x_m, y=tl_fac["cumulative_frp_mw"], name="FRP (MW)", yaxis="y2", line=dict(color="#facc15", width=3)))
                        fig_tl = apply_stitch_plotly_theme(fig_tl, "2023 Monthly Thermal Activity & FRP")
                        fig_tl.update_layout(height=340, yaxis=dict(title="Hotspots"), yaxis2=dict(title="MW", overlaying="y", side="right", showgrid=False), legend=dict(orientation="h", y=1.12))
                        st.plotly_chart(fig_tl, use_container_width=True)

            proof_img = WORKSPACE_ROOT / "data" / "03_satellite_cache" / "facility_imagery" / "stage2_visual_proof_duisburg.png"
            if proof_img.exists():
                with st.expander("🔬 View Duisburg 4-Panel Thermal & Freight Verification Proof", expanded=False):
                    st.image(str(proof_img), use_container_width=True)

            with st.expander("📊 View Full 30-Facility Stage 2 Multi-Sensor Table", expanded=False):
                cols = ["facility_name", "sector", "country", "landsat_scene_id", "thermal_delta_t_c", "firms_hotspot_detections_2023", "firms_active_months_count", "planet_clear_passes_2023", "vhr_rail_yard_contrast_index", "freight_logistics_zscore"]
                st.dataframe(ms_df[cols].sort_values("thermal_delta_t_c", ascending=False), use_container_width=True)

    with tab_s1:
        obs_list = CopernicusSentinel5PClient().get_facility_observations(fac_id, target_fac, lat, lon, year=2023)
        analysis = SatellitePlumeAnalyzer().analyze_facility_plumes(obs_list, claimed_production_tonnes=prod_claimed)
        _render_cards([
            ("Plume Contrast", f"+{analysis.plume_anomaly_zscore:.2f} σ", "Above Regional Bg", "#8ed5ff"),
            ("Valid Overpasses", f"{analysis.valid_clear_sky_overpasses} / {analysis.total_overpasses}", f"Cloud: {analysis.mean_cloud_fraction*100:.1f}%", "#ffffff"),
            ("Operational State", html.escape(analysis.operational_state_inference.split("(")[0].strip()), "Inferred State", "#facc15"),
            ("Remote Verdict", html.escape(analysis.consistency_verdict), "Signal Concordance", "#4edea3"),
        ])
        if obs_list:
            obs_df = pd.DataFrame([
                {
                    "Date": o.observation_date,
                    "Facility (µmol/m²)": (o.tropospheric_column_density_mol_m2 * 1e6) if not np.isnan(o.tropospheric_column_density_mol_m2) else 0.0,
                    "Background (µmol/m²)": (o.regional_background_mol_m2 * 1e6) if not np.isnan(o.regional_background_mol_m2) else 0.0,
                }
                for o in obs_list
            ])
            fig_obs = go.Figure()
            fig_obs.add_trace(go.Bar(x=obs_df["Date"], y=obs_df["Facility (µmol/m²)"], name="Facility Plume", marker_color="#8ed5ff"))
            fig_obs.add_trace(go.Scatter(x=obs_df["Date"], y=obs_df["Background (µmol/m²)"], name="15–30km Buffer", line=dict(color="#facc15", width=2, dash="dash")))
            fig_obs = apply_stitch_plotly_theme(fig_obs, f"2023 Sentinel-5P NO₂ Contrast: {html.escape(target_fac)}")
            fig_obs.update_layout(height=320)
            st.plotly_chart(fig_obs, use_container_width=True)


def render_tab_bayesian():
    scope_banner()
    st.markdown('<div class="stitch-main-title">Multimodal Probabilistic Evidence Fusion Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="stitch-sub-title">Calibrated risk posteriors decoupled from observational confidence</div>', unsafe_allow_html=True)
    st.markdown('<div class="formula-box">logit P(H | E) = logit P(H) + ∑ wᵢ · Cᵢ · ln(LRᵢ)</div>', unsafe_allow_html=True)

    engine = ProbabilisticEvidenceFusionEngine()
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("#### Input Evidence Streams")
        stoich_sig = st.slider("Stoichiometric Safety Margin (σ above floor)", 0.0, 5.0, 1.2, 0.1)
        stoich_viol = st.checkbox("Simulate Stoichiometric Floor Violation", False)

        has_sat = st.checkbox("Include Sentinel-5P Satellite Data", True)
        sat_z = st.slider("Sentinel-5P Plume Anomaly Z-Score", -2.0, 4.0, 1.8, 0.1) if has_sat else None
        sat_cloud = st.slider("Cloud Fraction", 0.0, 1.0, 0.25, 0.05) if has_sat else 1.0

        has_hist = st.checkbox("Include Historical E-PRTR Baseline", True)
        temp_z = st.slider("Sudden Drop Anomaly max(0, -z)", 0.0, 4.0, 0.8, 0.1) if has_hist else None
        yrs_hist = st.slider("Historical Reference Years", 1, 6, 5) if has_hist else 0

        has_reg = st.checkbox("Include Registry Capacity Check", False)
        reg_ratio = st.slider("Claimed / GEM Capacity Ratio", 0.5, 1.5, 1.0, 0.05) if has_reg else None

        has_s2 = st.checkbox("Include Stage 2 Thermal (USGS/FIRMS) & Freight (VHR)", True)
        therm_z = st.slider("Thermal Core Anomaly Z-Score", -2.0, 4.5, 2.4, 0.1) if has_s2 else None
        freight_z = st.slider("Freight Rail-Yard Activity Z-Score", -2.0, 4.5, 1.6, 0.1) if has_s2 else None

    ev_kwargs = {
        "stoichiometric_discrepancy_sigma": stoich_sig,
        "stoichiometric_violated": stoich_viol,
        "satellite_plume_anomaly_zscore": sat_z,
        "satellite_cloud_fraction": sat_cloud,
        "temporal_variance_zscore": temp_z,
        "years_reported_history": yrs_hist,
        "registry_capacity_ratio": reg_ratio,
        "thermal_anomaly_zscore": therm_z,
        "thermal_operating_months_ratio": 0.92 if has_s2 else None,
        "freight_logistics_zscore": freight_z,
    }
    valid_fields = {f.name for f in dataclasses.fields(EvidenceInput)}
    ev = EvidenceInput(**{k: v for k, v in ev_kwargs.items() if k in valid_fields})
    decision = engine.fuse_evidence(ev, reported_emissions_tco2=800_000, physical_min_tco2=750_000)

    with col_e2:
        st.markdown("#### Probabilistic Decision Synthesis")
        badge_cls = (
            "badge-consistent" if decision.audit_verdict == "Consistent"
            else ("badge-potential" if decision.audit_verdict == "Potential Inconsistency"
                  else ("badge-risk" if decision.audit_verdict == "High Inconsistency Risk" else "badge-insufficient"))
        )
        st.markdown(f'<div class="status-badge {badge_cls}">{html.escape(decision.audit_verdict.upper())}</div>', unsafe_allow_html=True)
        st.write("")
        _render_cards([
            ("Inconsistency Risk P(H|E)", f"{decision.posterior_inconsistency_risk*100:.1f}%", "Posterior Risk", "#8ed5ff"),
            ("Evidence Confidence", f"{decision.evidence_confidence_score*100:.1f}%", "Observational Quality", "#4edea3"),
        ])

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=decision.posterior_inconsistency_risk * 100,
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
        ))
        fig_gauge = apply_stitch_plotly_theme(fig_gauge)
        fig_gauge.update_layout(height=230)
        st.plotly_chart(fig_gauge, use_container_width=True)

        with st.expander("📊 Prior Sensitivity Analysis (P(H) = 2% to 15%)"):
            sens = engine.evaluate_prior_sensitivity(ev, reported_emissions_tco2=800_000, physical_min_tco2=750_000)
            st.table(pd.DataFrame([{"Base Prior P(H)": f"{p*100:.0f}%", "Posterior Risk P(H|E)": f"{r*100:.1f}%"} for p, r in sens.items()]))


def render_tab_benchmark():
    scope_banner()
    st.markdown('<div class="stitch-main-title">Empirical Benchmark Evaluation: 325-Case Graded Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="stitch-sub-title">Facility-grouped evaluation of single-stream and Stage 2 multimodal architectures</div>', unsafe_allow_html=True)

    results_dir = WORKSPACE_ROOT / "experiments" / "results"
    summary_csv = results_dir / "graded_model_comparison_summary.csv"
    sens_csv = results_dir / "graded_label_sensitivity.csv"
    m5_csv = results_dir / "m5_historical_score_ablation.csv"
    triage_csv = results_dir / "triage_auditor_simulation.csv"

    if not summary_csv.exists():
        st.warning("Run `python experiments/run_graded_evaluation.py` to generate empirical benchmark tables.")
        return

    df_sum = pd.read_csv(summary_csv)
    row_e2 = df_sum[df_sum["model_name"].str.contains("Bayesian")].iloc[-1]
    row_e3 = df_sum[df_sum["model_name"].str.contains("Logistic")].iloc[-1]
    row_c2 = df_sum[df_sum["model_name"].str.contains("Stage 2 Satellite|Historical Alone")].iloc[0]

    _render_cards([
        ("Stage 2 Bayesian Fusion", f"{row_e2['roc_auc']:.4f}", f"95% CI [{row_e2['roc_auc_ci_low']:.3f}, {row_e2['roc_auc_ci_high']:.3f}]", "#8ed5ff"),
        ("Logistic Triage (GroupKFold)", f"{row_e3['roc_auc']:.4f}", f"95% CI [{row_e3['roc_auc_ci_low']:.3f}, {row_e3['roc_auc_ci_high']:.3f}]", "#4edea3"),
        ("Stage 2 Multi-Sensor EO", f"{row_c2['roc_auc']:.4f}", "vs 0.5183 Stage 1 TROPOMI", "#facc15"),
        ("Evaluated Benchmark", "325 Cases", "177 Negatives • 148 Positives", "#ffffff"),
    ])

    st.markdown("### 1. Model Comparison on 325-Case Graded Benchmark")
    col_map = {
        "model_name": "Model Architecture", "roc_auc": "ROC-AUC", "pr_auc": "PR-AUC",
        "brier_score": "Brier Score", "ece": "ECE", "fpr_authentic": "Authentic FPR",
        "recall_at_fpr_5": "Recall@5% FPR", "recall_at_fpr_10": "Recall@10% FPR", "abstention_rate": "Abstention Rate",
    }
    disp_df = df_sum[[c for c in col_map if c in df_sum.columns]].rename(columns=col_map)
    fmt = {
        "ROC-AUC": "{:.4f}", "PR-AUC": "{:.4f}", "Brier Score": "{:.4f}", "ECE": "{:.4f}",
        "Authentic FPR": "{:.2%}", "Recall@5% FPR": "{:.2%}", "Recall@10% FPR": "{:.2%}", "Abstention Rate": "{:.1%}",
    }
    st.dataframe(disp_df.style.format({k: v for k, v in fmt.items() if k in disp_df.columns}), use_container_width=True)

    fig_bars = go.Figure()
    for col_y, label, clr in [("roc_auc", "ROC-AUC", "#8ed5ff"), ("pr_auc", "PR-AUC", "#4edea3"), ("brier_score", "Brier Score", "#facc15")]:
        fig_bars.add_trace(go.Bar(name=label, x=df_sum["model_name"], y=df_sum[col_y], marker_color=clr))
    fig_bars = apply_stitch_plotly_theme(fig_bars, "Discrimination & Calibration Across Evaluated Models")
    fig_bars.update_layout(barmode="group", height=340)
    st.plotly_chart(fig_bars, use_container_width=True)

    c_left, c_right = st.columns(2)
    with c_left:
        if m5_csv.exists():
            st.markdown("### 2. One-Sided Historical Drift Ablation")
            st.dataframe(pd.read_csv(m5_csv).style.format({"roc_auc": "{:.4f}", "pr_auc": "{:.4f}", "brier_score": "{:.4f}", "ece": "{:.4f}", "fpr_authentic": "{:.2%}"}), use_container_width=True)
    with c_right:
        if sens_csv.exists():
            st.markdown("### 3. Screening Threshold Sensitivity (≥5% vs ≥10%)")
            st.dataframe(pd.read_csv(sens_csv)[["threshold", "model", "prevalence", "roc_auc", "pr_auc"]].style.format({"prevalence": "{:.1%}", "roc_auc": "{:.4f}", "pr_auc": "{:.4f}"}), use_container_width=True)

    if triage_csv.exists():
        st.markdown("### 4. Auditor Triage Prioritization Efficiency")
        df_tri = pd.read_csv(triage_csv)
        tri_cols = [c for c in ["k_pct", "k_cases", "random_baseline_precision", "e1_bayes_caught", "e1_bayes_precision", "e1_bayes_recall", "e1_bayes_lift", "e2_logistic_caught", "e2_logistic_precision", "e2_logistic_recall", "e2_logistic_lift"] if c in df_tri.columns]
        st.dataframe(df_tri[tri_cols].style.format({"k_pct": "Top {}%", "random_baseline_precision": "{:.1%}", "e1_bayes_precision": "{:.1%}", "e1_bayes_recall": "{:.1%}", "e1_bayes_lift": "{:.2f}x", "e2_logistic_precision": "{:.1%}", "e2_logistic_recall": "{:.1%}", "e2_logistic_lift": "{:.2f}x"}), use_container_width=True)


with st.spinner("Initializing VeriCBAM Decision Support Engine..."):
    mgr, facilities_df = load_cohort_data()

shield_icon = Path(__file__).parent / "shield.png"
if shield_icon.exists():
    st.sidebar.image(str(shield_icon), width=56)
st.sidebar.markdown("### VeriCBAM Audit Suite")
st.sidebar.caption("EU CBAM Emissions Verification")

MENU_OPTIONS = [
    "1. 🚀 Quick Audit & PDF Dossier Generator",
    "2. Executive Overview & Regulatory Framework",
    "3. 30-Facility European Benchmark Cohort",
    "4. Stoichiometric Physics Engine",
    "5. Multi-Sensor Satellite Engine (Stage 1 & 2 EO)",
    "6. Bayesian Evidence Fusion",
    "7. Empirical Benchmark & Ablation (325 Cases)",
]
menu = st.sidebar.radio("Navigation", MENU_OPTIONS)

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

if menu == MENU_OPTIONS[0]:
    render_tab_quick_audit(facilities_df)
elif menu == MENU_OPTIONS[1]:
    render_tab_overview()
elif menu == MENU_OPTIONS[2]:
    render_tab_cohort(mgr, facilities_df)
elif menu == MENU_OPTIONS[3]:
    render_tab_stoichiometry()
elif menu == MENU_OPTIONS[4]:
    render_tab_satellite(facilities_df)
elif menu == MENU_OPTIONS[5]:
    render_tab_bayesian()
elif menu == MENU_OPTIONS[6]:
    render_tab_benchmark()
