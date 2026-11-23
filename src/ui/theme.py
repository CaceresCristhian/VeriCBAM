"""
VeriCBAM Streamlit UI Design Tokens & Reusable Components.
Centralizes the dark WCAG-compliant Stitch palette, scope banner, Plotly layout theme, and Bento metric cards.
"""

import html
import streamlit as st

STITCH_THEME_CSS = """
<style>
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

    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    section[data-testid="stSidebar"], [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] {
        background-color: #161922 !important;
        border-right: 1px solid #2d3440 !important;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.01em !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] *, [data-testid="stSidebar"] small {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {
        color: #8ed5ff !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: #1e2533 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 9px 12px !important;
        margin-bottom: 5px !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label * {
        color: #ffffff !important;
        font-size: 0.90rem !important;
        font-weight: 500 !important;
        line-height: 1.35 !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #253347 !important;
        border-color: #8ed5ff !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #1c3552 !important;
        border: 1px solid #8ed5ff !important;
        border-left: 5px solid #8ed5ff !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .sidebar-student-box {
        background: #1a2230 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        margin-top: 20px !important;
        font-size: 0.82rem !important;
        line-height: 1.6 !important;
    }
    .sidebar-student-box .box-label { color: #8ed5ff !important; font-weight: 700 !important; }
    .sidebar-student-box .box-val { color: #ffffff !important; font-weight: 500 !important; }

    [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span,
    [data-testid="stRadio"] > label p, [data-testid="stSlider"] label p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.94rem !important;
    }

    .stApp div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] div[data-testid="stRadio"]) div[role="radiogroup"] label {
        background-color: rgba(28, 32, 40, 0.7) !important;
        border: 1px solid rgba(45, 52, 64, 0.8) !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        transition: all 0.2s ease !important;
    }
    .stApp div[data-testid="stRadio"]:not(section[data-testid="stSidebar"] div[data-testid="stRadio"]) div[role="radiogroup"] label:has(input:checked) {
        border-color: #8ed5ff !important;
        background-color: rgba(142, 213, 255, 0.18) !important;
    }

    .stitch-main-title {
        font-size: 2.15rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .stitch-sub-title {
        font-size: 1.02rem;
        color: #cbd5e1;
        margin-bottom: 1.4rem;
    }

    .bento-card {
        background-color: #1c2028;
        border: 1px solid #2d3440;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .bento-card:hover { border-color: #8ed5ff; transform: translateY(-2px); }
    .bento-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        font-weight: 700;
        color: #cbd5e1 !important;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .bento-value {
        font-size: 1.60rem;
        font-weight: 700;
        font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        color: #ffffff !important;
        margin-bottom: 4px;
    }
    .bento-sub { font-size: 0.80rem; color: #94a3b8 !important; }

    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        letter-spacing: 0.03em;
    }
    .badge-consistent { background: rgba(78, 222, 163, 0.15); color: #4edea3; border: 1px solid rgba(78, 222, 163, 0.4); }
    .badge-potential { background: rgba(250, 204, 21, 0.15); color: #facc15; border: 1px solid rgba(250, 204, 21, 0.4); }
    .badge-risk { background: rgba(239, 68, 68, 0.15); color: #ffb4ab; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-insufficient { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }

    .formula-box {
        background: rgba(15, 19, 28, 0.8);
        border: 1px dashed #2d3440;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.88rem;
        color: #8ed5ff;
        margin-bottom: 16px;
    }

    [data-testid="stExpander"] details {
        background-color: #1c2028 !important;
        border: 1px solid #2d3440 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] div[role="region"] {
        background-color: #141822 !important;
        border-top: 1px solid #2d3440 !important;
        color: #f1f5f9 !important;
    }

    [data-testid="stAlert"] * { color: #f8fafc !important; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > input {
        background-color: #161922 !important;
        border-color: #3b4252 !important;
        color: #f1f5f9 !important;
    }
    div[data-baseweb="select"] span { color: #f1f5f9 !important; }
</style>
"""


def scope_banner():
    """Renders the standard verification scope banner."""
    st.info(
        "🛡️ **VeriCBAM Verification Scope:** Decision-support screening under Commission Delegated Regulation "
        "(EU) 2025/2551 & Implementing Regulation (EU) 2025/2546. Advisory tool for accredited verifiers and authorities."
    )


def apply_stitch_plotly_theme(fig, title_text: str = ""):
    """Applies the dark Stitch Plotly template with offline system fonts."""
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


def bento_card(label: str, value: str, sub: str, value_color: str = "#ffffff", tooltip: str = "") -> str:
    """Renders an HTML Bento metric card."""
    title_attr = f' title="{html.escape(tooltip)}"' if tooltip else ""
    return (
        f'<div class="bento-card"{title_attr}>'
        f'<div class="bento-label">{html.escape(label)}</div>'
        f'<div class="bento-value" style="color: {value_color};">{value}</div>'
        f'<div class="bento-sub">{html.escape(sub)}</div>'
        f"</div>"
    )
