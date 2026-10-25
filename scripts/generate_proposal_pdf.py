"""
Generates the publication-quality Capstone_Proposal_Document.pdf from Capstone_Proposal_Document.md
using ReportLab with TrueType Unicode font registration (Arial), custom NumberedCanvas (running headers,
footers, page X of Y), clean typography, styled tables, callouts, and academic formatting.
"""

import os
import re
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

WORKSPACE = Path(r"c:\Users\crist\Projects\UEprojects\Capstone")
MD_PATH = WORKSPACE / "Capstone_Proposal_Document.md"
PDF_PATH = WORKSPACE / "Capstone_Proposal_Document.pdf"

# Register TrueType Arial fonts for full Unicode support (accents, euro, math symbols, Greek letters)
FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
pdfmetrics.registerFont(TTFont("Arial", str(FONTS_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTS_DIR / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", str(FONTS_DIR / "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", str(FONTS_DIR / "arialbi.ttf")))


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Header (on pages > 1)
        if self._pageNumber > 1:
            self.drawString(20 * mm, 285 * mm, "VeriCBAM — Master Capstone Proposal | University of Europe for Applied Sciences")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(20 * mm, 282 * mm, 190 * mm, 282 * mm)

        # Footer (on all pages)
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(190 * mm, 12 * mm, footer_text)
        self.drawString(20 * mm, 12 * mm, "VeriCBAM — Master Capstone Proposal | M.Sc. Data Science | Supervisor: Dr. Humera Noor")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(20 * mm, 15 * mm, 190 * mm, 15 * mm)
        self.restoreState()


def parse_braced_arg(s: str, start_idx: int):
    """Parses a balanced {arg} substring from start_idx."""
    if start_idx >= len(s) or s[start_idx] != '{':
        return None, start_idx
    depth = 0
    for i in range(start_idx, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return s[start_idx + 1:i], i + 1
    return None, start_idx


def replace_fractions(text: str) -> str:
    """Recursively parses and converts LaTeX \\frac{num}{den} to clean (num / den)."""
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
        if any(op in num_clean for op in ["+", "-", "×", "·", " "]):
            num_expr = f"({num_clean})"
        else:
            num_expr = num_clean
        if any(op in den_clean for op in ["+", "-", "×", "·", " "]):
            den_expr = f"({den_clean})"
        else:
            den_expr = den_clean
        text = text[:idx] + f"({num_expr} / {den_expr})" + text[end_idx:]
    return text


def convert_latex_math(s: str, is_display: bool = False) -> str:
    """Converts a LaTeX math expression to clean typographical text with Unicode symbols and ReportLab tags."""
    text = s.strip()
    if is_display:
        if text.startswith("$$"):
            text = text[2:].strip()
        if text.endswith("$$"):
            text = text[:-2].strip()
        elif text.endswith(".$$"):
            text = text[:-3].strip() + "."
        elif text.endswith(",$$"):
            text = text[:-3].strip() + ","
    else:
        if text.startswith("$") and text.endswith("$"):
            text = text[1:-1].strip()

    # Temperature and degree symbols
    text = re.sub(r"(\d+(?:,\d+)?)\s*\^\\circ\\text\{C\}", r"\1°C", text)
    text = re.sub(r"(\d+(?:,\d+)?)\s*\^\\circ C", r"\1°C", text)
    text = re.sub(r"\^\\circ\\text\{C\}", "°C", text)
    text = re.sub(r"\^\\circ", "°", text)

    # Reaction arrows with delta H
    text = re.sub(r"\\xrightarrow\{\\Delta H\s*=\s*\+?178\\text\{ kJ/mol\}\}", " —[ ΔH = +178 kJ/mol ]→ ", text)
    text = re.sub(r"\\xrightarrow\{([^}]+)\}", r" —[ \1 ]→ ", text)

    # Fractions
    text = replace_fractions(text)

    # Summations
    text = re.sub(r"\\sum_\{k=1\}\^\{6\}", "Σ<sub>(k=1..6)</sub>", text)
    text = re.sub(r"\\sum_\{([^}]+)\}\^\{([^}]+)\}", r"Σ<sub>(\1..\2)</sub>", text)
    text = text.replace(r"\sum", "Σ")

    # Common chemical formulas using <sub> tags
    text = text.replace(r"\text{CaCO}_3", "CaCO<sub>3</sub>").replace(r"CaCO_3", "CaCO<sub>3</sub>").replace("CaCO₃", "CaCO<sub>3</sub>")
    text = text.replace(r"\text{CaO}", "CaO")
    text = text.replace(r"\text{CO}_2", "CO<sub>2</sub>").replace(r"CO_2", "CO<sub>2</sub>").replace("CO₂", "CO<sub>2</sub>").replace(r"\text{CO}", "CO")
    text = text.replace(r"\text{NO}_x", "NO<sub>x</sub>").replace(r"NO_x", "NO<sub>x</sub>").replace("NOx", "NO<sub>x</sub>")
    text = text.replace(r"\text{NO}_2", "NO<sub>2</sub>").replace(r"NO_2", "NO<sub>2</sub>").replace("NO₂", "NO<sub>2</sub>")
    text = text.replace(r"\text{SO}_x", "SO<sub>x</sub>").replace(r"SO_x", "SO<sub>x</sub>").replace("SOx", "SO<sub>x</sub>")
    text = text.replace(r"\text{SO}_2", "SO<sub>2</sub>").replace(r"SO_2", "SO<sub>2</sub>").replace("SO₂", "SO<sub>2</sub>")
    text = text.replace(r"\text{Fe}_2\text{O}_3", "Fe<sub>2</sub>O<sub>3</sub>").replace(r"Fe_2O_3", "Fe<sub>2</sub>O<sub>3</sub>").replace("Fe₂O₃", "Fe<sub>2</sub>O<sub>3</sub>")
    text = text.replace(r"\text{Fe}", "Fe")
    text = text.replace(r"t\text{CO}_2e", "t CO<sub>2</sub>e").replace(r"tCO_2e", "t CO<sub>2</sub>e").replace("t CO₂e", "t CO<sub>2</sub>e")

    # Units
    text = text.replace(r"\text{ kJ/mol}", " kJ/mol").replace(r"\text{kJ/mol}", " kJ/mol")
    text = text.replace(r"\text{ g/mol}", " g/mol").replace(r"\text{g/mol}", " g/mol")
    text = text.replace(r"\text{ t CO}_2/\text{t CaO}", " t CO<sub>2</sub>/t CaO")
    text = text.replace(r"\text{ t CO}_2/\text{t clinker}", " t CO<sub>2</sub>/t clinker")
    text = text.replace(r"\text{ t CO}_2/\text{t crude steel}", " t CO<sub>2</sub>/t crude steel")
    text = text.replace(r"\text{ t CO}_2/\text{t hot metal}", " t CO<sub>2</sub>/t hot metal")
    text = text.replace(r"\text{ t CO}_2/\text{t}", " t CO<sub>2</sub>/t").replace(r"t CO_2/t", "t CO<sub>2</sub>/t")
    text = text.replace(r"\text{ t/t}", " t/t")
    text = text.replace(r"\text{ GJ/t clinker}", " GJ/t clinker").replace(r"\text{GJ/t clinker}", " GJ/t clinker")
    text = text.replace(r"\text{ kg coke/t}", " kg coke/t").replace(r"\text{kg coke/t}", " kg coke/t")
    text = text.replace(r"\text{ km}", " km").replace(r"\text{km}", " km")
    text = text.replace(r"\text{mol/m}^2", "mol/m<sup>2</sup>").replace("mol/m²", "mol/m<sup>2</sup>")

    # Greek letters (supported in Windows Arial)
    text = text.replace(r"\gamma", "γ").replace(r"\Gamma", "Γ")
    text = text.replace(r"\delta", "δ").replace(r"\Delta", "Δ")
    text = text.replace(r"\sigma", "σ").replace(r"\Sigma", "Σ")
    text = text.replace(r"\tau", "τ")
    text = text.replace(r"\eta", "η")
    text = text.replace(r"\mu", "μ")
    text = text.replace(r"\rho", "ρ")

    # Math operators and functions
    text = text.replace(r"\operatorname{logit}", "logit")
    text = text.replace(r"\operatorname{LR}", "LR")
    text = text.replace(r"\hat{p}", "p̂")
    text = text.replace(r"\ln", "ln")
    text = text.replace(r"\max", "max")
    text = text.replace(r"\min", "min")
    text = text.replace(r"\left(", "(").replace(r"\right)", ")")
    text = text.replace(r"\left[", "[").replace(r"\right]", "]")
    text = text.replace(r"\left", "").replace(r"\right", "")
    text = text.replace(r"\mid", "|")
    text = text.replace(r"\approx", "≈")
    text = text.replace(r"\le", "≤").replace(r"\ge", "≥")
    text = text.replace(r"\in", " in ")  # Arial does not have U+2208 (element of)
    text = text.replace(r"\times", "×")
    text = text.replace(r"\cdot", "·")
    text = text.replace(r"\neq", "≠")
    text = text.replace(r"\longrightarrow", " → ")
    text = text.replace(r"\rightarrow", " → ")
    text = text.replace(r"\uparrow", " (gas)").replace(r"\downarrow", " (precipitate)")
    text = text.replace(r"\quad", " &nbsp; &nbsp; ").replace(r"\qquad", " &nbsp; &nbsp; &nbsp; &nbsp; ")
    text = text.replace(r"\%", "%")
    text = text.replace(r"\{", "{").replace(r"\}", "}")
    text = text.replace(r"\bar{V}_\text{bg}", "V<sub>bg</sub>").replace(r"\bar{V}_\text{target}", "V<sub>target</sub>")
    text = text.replace(r"\bar{V}_{\text{bg}}", "V<sub>bg</sub>").replace(r"\bar{V}_{\text{target}}", "V<sub>target</sub>")
    text = text.replace(r"\bar{V}", "V")

    # Clean any remaining \text{...}
    text = re.sub(r"\\text\{([^}]+)\}", r"\1", text)

    # Convert subscripts _sub or _{sub} to <sub>sub</sub>
    text = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", text)

    text = text.replace(r"\operatorname", "")
    text = text.replace(r"--", "–")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_markdown_inline(text: str) -> str:
    """Convert common inline markdown to HTML tags compatible with ReportLab with Arial."""
    # 1. Protect links: [label](url) -> label
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<font color="#2B6CB0"><u>\1</u></font>', text)

    # 2. Protect inline code: `code` -> monospace font, escaping internal characters
    def replace_code(m):
        code_val = m.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<font face="Courier" color="#1A365D">{code_val}</font>'
    text = re.sub(r"`(.*?)`", replace_code, text)

    # 3. Inline math: $math$ -> clean typography with convert_latex_math
    def replace_inline_math(m):
        raw_math = m.group(1)
        conv = convert_latex_math(raw_math, is_display=False)
        return f'<i>{conv}</i>'
    text = re.sub(r"\$([^\$\n]+)\$", replace_inline_math, text)

    # 4. Bold italic: ***text***
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<b><i>\1</i></b>", text)
    # 5. Bold: **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # 6. Italic: *text* (avoid touching isolated underscores in filenames)
    text = re.sub(r"(?<!\w)\*([^\*]+)\*(?!\w)", r"<i>\1</i>", text)
    # 7. Underscore italics only when flanked by spaces or punctuation: e.g. " _italic_ "
    text = re.sub(r"(?<=\s)_([^_]+)_(?=\s|[.,;:!?)])", r"<i>\1</i>", text)

    # Clean standard chemical abbreviations in regular prose
    text = text.replace("CO2", "CO<sub>2</sub>").replace("NOx", "NO<sub>x</sub>").replace("SOx", "SO<sub>x</sub>")
    text = text.replace("CaCO3", "CaCO<sub>3</sub>").replace("Fe2O3", "Fe<sub>2</sub>O<sub>3</sub>")

    return text


def build_pdf():
    print(f"Reading markdown from: {MD_PATH}")
    if not MD_PATH.exists():
        raise FileNotFoundError(f"Markdown file not found: {MD_PATH}")

    content = MD_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles using Arial
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        alignment=TA_LEFT,
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        alignment=TA_LEFT,
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor("#2C5282"),
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True,
    )

    h3_style = ParagraphStyle(
        "Heading3_Custom",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2D3748"),
        alignment=TA_JUSTIFY,
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3,
    )

    formula_style = ParagraphStyle(
        "Formula_Custom",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1A365D"),
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=3,
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Arial-Italic",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#2C5282"),
        alignment=TA_JUSTIFY,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1A202C"),
    )

    meta_key_style = ParagraphStyle(
        "MetaKey",
        fontName="Arial-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#2B6CB0"),
    )
    meta_val_style = ParagraphStyle(
        "MetaVal",
        fontName="Arial",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#2D3748"),
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("Capstone Project Proposal: VeriCBAM", title_style))
    story.append(Paragraph("Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=7))

    # Metadata Card (3 Clean Rows, Potsdam Campus, No Scope/Repo row)
    meta_table_data = [
        [Paragraph("Student Name:", meta_key_style), Paragraph("Cristhian David Cáceres Mateus", meta_val_style),
         Paragraph("Matriculation No:", meta_key_style), Paragraph("93515346", meta_val_style)],
        [Paragraph("Degree Program:", meta_key_style), Paragraph("Master of Science in Data Science (M.Sc. DSc)", meta_val_style),
         Paragraph("Institution:", meta_key_style), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_val_style)],
        [Paragraph("Faculty Supervisor:", meta_key_style), Paragraph("Dr. Humera Noor", meta_val_style),
         Paragraph("Submission Date:", meta_key_style), Paragraph("October 2026 (Semester Winter 2026/2027)", meta_val_style)],
    ]

    meta_table = Table(meta_table_data, colWidths=[31 * mm, 54 * mm, 31 * mm, 54 * mm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Parse body
    i = 0
    # Advance past frontmatter header until after the first horizontal rule
    for idx, l in enumerate(lines[:25]):
        if l.strip() in ["---", "***", "___"]:
            i = idx + 1
            break

    in_code_block = False
    code_lines = []
    code_lang = ""
    in_table = False
    table_raw_rows = []

    def flush_table(rows):
        if not rows:
            return None
        parsed_rows = []
        for r in rows:
            parsed_cells = [Paragraph(clean_markdown_inline(c.strip()), body_style) for c in r]
            parsed_rows.append(parsed_cells)
        col_count = len(parsed_rows[0])
        avail_width = 170 * mm
        col_w = [avail_width / col_count] * col_count
        if col_count == 4:
            col_w = [36 * mm, 50 * mm, 42 * mm, 42 * mm]
        elif col_count == 5:
            col_w = [28 * mm, 35 * mm, 35 * mm, 32 * mm, 40 * mm]
        t = Table(parsed_rows, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        return t

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip main title since rendered above
        if i < 15 and (stripped.startswith("# Capstone Project Proposal") or stripped.startswith("## Multimodal Evidence")):
            i += 1
            continue

        # Code block handling
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                if code_lang == "mermaid" or any("flowchart" in l or "gantt" in l for l in code_lines):
                    diagram_note = "<b>System Architecture & Dataflow:</b> End-to-end multimodal pipeline linking document ingestion to physical bounds, remote sensing, and dual-stage Bayesian/logistic inference. <i>(Interactive visualization available in Streamlit UI Tab 1)</i>"
                    if any("gantt" in l for l in code_lines):
                        diagram_note = "<b>Capstone Milestone Roadmap:</b> Sequential sprint progression from co-pollutant cohort ingestion to proposal approval, probability calibration, UI cockpit delivery, and January 2027 defense."
                    callout_box = Table([[Paragraph(diagram_note, callout_style)]], colWidths=[170 * mm])
                    callout_box.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ]))
                    story.append(callout_box)
                    story.append(Spacer(1, 4))
                else:
                    code_text = "<br/>".join(code_lines)
                    code_p = Paragraph(code_text, code_style)
                    code_box = Table([[code_p]], colWidths=[170 * mm])
                    code_box.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ]))
                    story.append(code_box)
                    story.append(Spacer(1, 4))
                code_lines = []
                code_lang = ""
            else:
                in_code_block = True
                code_lang = stripped[3:].strip().lower()
                code_lines = []
            i += 1
            continue

        if in_code_block:
            escaped = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_lines.append(escaped if escaped else "&nbsp;")
            i += 1
            continue

        # Table handling
        if stripped.startswith("|") and stripped.endswith("|"):
            if re.match(r"^\|(\s*:?-+:?\s*\|)+$", stripped):
                i += 1
                continue
            cells = [c for c in stripped.split("|")[1:-1]]
            table_raw_rows.append(cells)
            in_table = True
            i += 1
            continue
        else:
            if in_table:
                tbl = flush_table(table_raw_rows)
                if tbl:
                    story.append(tbl)
                    story.append(Spacer(1, 4))
                table_raw_rows = []
                in_table = False

        if not stripped:
            i += 1
            continue

        # Horizontal Rule
        if stripped in ["---", "***", "___"]:
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceBefore=4, spaceAfter=5))
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            story.append(Paragraph(clean_markdown_inline(stripped[2:]), title_style))
            i += 1
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(clean_markdown_inline(stripped[3:]), h1_style))
            i += 1
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(clean_markdown_inline(stripped[4:]), h2_style))
            i += 1
            continue
        if stripped.startswith("#### "):
            story.append(Paragraph(clean_markdown_inline(stripped[5:]), h3_style))
            i += 1
            continue

        # Centered Display Math Block ($$...$$)
        if stripped.startswith("$$"):
            # Check if multi-line or single-line
            if (stripped.endswith("$$") or stripped.endswith(".$$") or stripped.endswith(",$$")) and len(stripped) > 4:
                formula_raw = stripped
            else:
                formula_parts = [stripped]
                while i + 1 < len(lines):
                    i += 1
                    next_stripped = lines[i].strip()
                    formula_parts.append(next_stripped)
                    if next_stripped.endswith("$$") or next_stripped.endswith(".$$") or next_stripped.endswith(",$$"):
                        break
                formula_raw = " ".join(formula_parts)

            formula_clean = convert_latex_math(formula_raw, is_display=True)
            formula_p = Paragraph(formula_clean, formula_style)
            formula_box = Table([[formula_p]], colWidths=[170 * mm])
            formula_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(formula_box)
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Callouts / Blockquotes
        if stripped.startswith("> "):
            callout_text = clean_markdown_inline(stripped[2:])
            callout_p = Paragraph(callout_text, callout_style)
            callout_box = Table([[callout_p]], colWidths=[170 * mm])
            callout_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
                ('LINEBEFORE', (0, 0), (0, -1), 2.5, colors.HexColor("#3182CE")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BEE3F8")),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(callout_box)
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Bullets
        if stripped.startswith("* ") or stripped.startswith("- ") or stripped.startswith("• "):
            bullet_text = clean_markdown_inline(stripped[2:])
            story.append(Paragraph(f"• &nbsp; {bullet_text}", bullet_style))
            i += 1
            continue

        # Numbered list item
        m_num = re.match(r"^(\d+[\.\)])\s+(.*)", stripped)
        if m_num:
            num_label = m_num.group(1)
            num_text = clean_markdown_inline(m_num.group(2))
            story.append(Paragraph(f"<b>{num_label}</b> &nbsp; {num_text}", bullet_style))
            i += 1
            continue

        # Standard Body Paragraph
        story.append(Paragraph(clean_markdown_inline(stripped), body_style))
        i += 1

    # End table flush if any
    if in_table and table_raw_rows:
        tbl = flush_table(table_raw_rows)
        if tbl:
            story.append(tbl)

    print(f"Building PDF document at: {PDF_PATH} ...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF generation completed successfully!")
    pdf_size_mb = PDF_PATH.stat().st_size / (1024 * 1024)
    print(f"File size: {pdf_size_mb:.2f} MB ({PDF_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build_pdf()
