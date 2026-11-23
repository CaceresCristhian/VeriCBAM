"""
Shared ReportLab PDF generation utilities for VeriCBAM submission documents.
Centralizes Arial TrueType font registration, headers/footers, and Markdown/LaTeX inline conversion.
"""

import os
import re
from pathlib import Path
from typing import Optional
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

WORKSPACE = Path(__file__).parents[1]
DOCS_SOURCES_DIR = WORKSPACE / "docs" / "sources"
SUBMISSIONS_DIR = WORKSPACE / "submissions"

FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
try:
    pdfmetrics.registerFont(TTFont("Arial", str(FONTS_DIR / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTS_DIR / "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Italic", str(FONTS_DIR / "ariali.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-BoldItalic", str(FONTS_DIR / "arialbi.ttf")))
    MAIN_FONT = "Arial"
    BOLD_FONT = "Arial-Bold"
    ITALIC_FONT = "Arial-Italic"
except Exception:
    MAIN_FONT = "Helvetica"
    BOLD_FONT = "Helvetica-Bold"
    ITALIC_FONT = "Helvetica-Oblique"


def make_numbered_canvas(
    footer_text: str,
    header_text: Optional[str] = None,
    margin_mm: float = 14.0,
    font_size: float = 7.4,
    report_page_check: bool = False,
):
    """Returns a configured ReportLab Canvas subclass with standardized header/footer pagination."""

    class _ConfiguredCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            if report_page_check:
                print(f"  [Page Check] Rendered {num_pages} page(s)")
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self._draw_chrome(num_pages)
                super().showPage()
            super().save()

        def _draw_chrome(self, page_count: int):
            self.saveState()
            self.setFont(MAIN_FONT, font_size)
            self.setFillColor(colors.HexColor("#4A5568"))
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)

            x_left = margin_mm * mm
            x_right = (210.0 - margin_mm) * mm

            if header_text and self._pageNumber > 1:
                self.drawString(x_left, 287 * mm, header_text)
                self.line(x_left, 284 * mm, x_right, 284 * mm)

            self.line(x_left, 11.5 * mm, x_right, 11.5 * mm)
            self.drawString(x_left, 8.2 * mm, footer_text)
            self.drawRightString(x_right, 8.2 * mm, f"Page {self._pageNumber} of {page_count}")
            self.restoreState()

    return _ConfiguredCanvas


def parse_braced_arg(s: str, start_idx: int):
    if start_idx >= len(s) or s[start_idx] != "{":
        return None, start_idx
    depth = 0
    for i in range(start_idx, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[start_idx + 1 : i], i + 1
    return None, start_idx


def replace_fractions(text: str) -> str:
    while r"\frac" in text:
        idx = text.find(r"\frac")
        num, next_idx = parse_braced_arg(text, idx + 5)
        if num is None:
            break
        den, end_idx = parse_braced_arg(text, next_idx)
        if den is None:
            break
        num_clean = replace_fractions(num.strip())
        den_clean = replace_fractions(den.strip())
        num_expr = f"({num_clean})" if any(op in num_clean for op in ["+", "-", "×", "·", " "]) else num_clean
        den_expr = f"({den_clean})" if any(op in den_clean for op in ["+", "-", "×", "·", " "]) else den_clean
        text = text[:idx] + f"({num_expr} / {den_expr})" + text[end_idx:]
    return text


def convert_latex_math(s: str, is_display: bool = False) -> str:
    text = s.strip()
    if is_display:
        if text.startswith("$$"):
            text = text[2:].strip()
        if text.endswith("$$"):
            text = text[:-2].strip()
        elif text.endswith(".$$") or text.endswith(",$$"):
            text = text[:-3].strip() + text[-3]
    elif text.startswith("$") and text.endswith("$"):
        text = text[1:-1].strip()

    text = re.sub(r"(\d+(?:,\d+)?)\s*\^\\circ\\text\{C\}", r"\1°C", text)
    text = re.sub(r"(\d+(?:,\d+)?)\s*\^\\circ C", r"\1°C", text)
    text = re.sub(r"\^\\circ\\text\{C\}", "°C", text)
    text = re.sub(r"\^\\circ", "°", text)
    text = re.sub(r"\\xrightarrow\{\\Delta H\s*=\s*\+?178\\text\{ kJ/mol\}\}", " —[ ΔH = +178 kJ/mol ]→ ", text)
    text = re.sub(r"\\xrightarrow\{([^}]+)\}", r" —[ \1 ]→ ", text)

    text = replace_fractions(text)

    chem_map = [
        (r"\text{CaCO}_3", "CaCO<sub>3</sub>"), (r"CaCO_3", "CaCO<sub>3</sub>"), ("CaCO₃", "CaCO<sub>3</sub>"),
        (r"\text{CaO}", "CaO"),
        (r"\text{CO}_2", "CO<sub>2</sub>"), (r"CO_2", "CO<sub>2</sub>"), ("CO₂", "CO<sub>2</sub>"), (r"\text{CO}", "CO"),
        (r"\text{NO}_x", "NO<sub>x</sub>"), (r"NO_x", "NO<sub>x</sub>"), ("NOx", "NO<sub>x</sub>"),
        (r"\text{NO}_2", "NO<sub>2</sub>"), (r"NO_2", "NO<sub>2</sub>"), ("NO₂", "NO<sub>2</sub>"),
        (r"\text{SO}_x", "SO<sub>x</sub>"), (r"SO_x", "SO<sub>x</sub>"), ("SOx", "SO<sub>x</sub>"),
        (r"\text{SO}_2", "SO<sub>2</sub>"), (r"SO_2", "SO<sub>2</sub>"), ("SO₂", "SO<sub>2</sub>"),
        (r"\text{Fe}_2\text{O}_3", "Fe<sub>2</sub>O<sub>3</sub>"), (r"Fe_2_O_3", "Fe<sub>2</sub>O<sub>3</sub>"), ("Fe₂O₃", "Fe<sub>2</sub>O<sub>3</sub>"),
        (r"\text{Fe}", "Fe"),
        (r"t\text{CO}_2e", "t CO<sub>2</sub>e"), (r"tCO_2e", "t CO<sub>2</sub>e"), ("t CO₂e", "t CO<sub>2</sub>e"),
        (r"\text{ t CO}_2/\text{t clinker}", " t CO<sub>2</sub>/t clinker"),
        (r"\text{ t CO}_2/\text{t}", " t CO<sub>2</sub>/t"), (r"t CO_2/t", "t CO<sub>2</sub>/t"),
        (r"\text{ t/t}", " t/t"), (r"\text{ km}", " km"), (r"\text{km}", " km"),
        (r"\text{mol/m}^2", "mol/m<sup>2</sup>"), ("mol/m²", "mol/m<sup>2</sup>"),
        (r"\text{qa\_value}", "qa_value"),
    ]
    for src, dst in chem_map:
        text = text.replace(src, dst)

    sym_map = [
        (r"\gamma", "γ"), (r"\Gamma", "Γ"), (r"\delta", "δ"), (r"\Delta", "Δ"),
        (r"\sigma", "σ"), (r"\Sigma", "Σ"), (r"\tau", "τ"), (r"\eta", "η"), (r"\mu", "μ"), (r"\rho", "ρ"),
        (r"\operatorname{logit}", "logit"), (r"\operatorname{LR}", "LR"),
        (r"\hat{Q}", "Q̂"), (r"\hat{p}", "p̂"),
        (r"\bar{V}_{\text{target}}", "V<sub>target</sub>"), (r"\bar{V}_{\text{bg}}", "V<sub>bg</sub>"),
        (r"\ln", "ln"), (r"\max", "max"), (r"\min", "min"),
        (r"\sum_{k=1}^{5}", "Σ<sub>k=1..5</sub>"), (r"\sum_{k=1}^5", "Σ<sub>k=1..5</sub>"),
        (r"\left(", "("), (r"\right)", ")"), (r"\left[", "["), (r"\right]", "]"),
        (r"\mid", "|"), (r"\approx", "≈"), (r"\le", "≤"), (r"\ge", "≥"),
        (r"\in", " in "), (r"\times", "×"), (r"\cdot", "·"), (r"\neq", "≠"),
        (r"\longrightarrow", " → "), (r"\Rightarrow", " → "), (r"\rightarrow", " → "),
        (r"\delta^*", "δ<sup>*</sup>"),
        (r"\qquad", " &nbsp; &nbsp; &nbsp; "),
        (r"\%", "%"), (r"\{", "{"), (r"\}", "}"),
    ]
    for src, dst in sym_map:
        text = text.replace(src, dst)

    text = re.sub(r"\\text\{([^}]+)\}", r"\1", text)
    text = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", text)
    text = re.sub(r"_([A-Za-z0-9]+)", r"<sub>\1</sub>", text)
    text = text.replace("qa<sub>value</sub>", "qa_value").replace("--", "–")
    return re.sub(r"\s+", " ", text).strip()


def clean_markdown_inline(text: str) -> str:
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<font color="#2B6CB0"><u>\1</u></font>', text)
    text = re.sub(
        r"`(.*?)`",
        lambda m: f'<font face="Courier" color="#1A365D">{m.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</font>',
        text,
    )
    text = re.sub(r"\$([^\$\n]+)\$", lambda m: f"<i>{convert_latex_math(m.group(1), is_display=False)}</i>", text)
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\w)\*([^\*]+)\*(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"(?<=\s)_([^_]+)_(?=\s|[.,;:!?)])", r"<i>\1</i>", text)
    text = text.replace("CO2", "CO<sub>2</sub>").replace("NOx", "NO<sub>x</sub>").replace("SOx", "SO<sub>x</sub>")
    text = text.replace("CaCO3", "CaCO<sub>3</sub>").replace("Fe2O3", "Fe<sub>2</sub>O<sub>3</sub>")
    return text
