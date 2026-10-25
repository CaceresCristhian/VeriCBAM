"""
Generates the publication-quality 2-page Project_Summary_and_Status_Report.pdf from Project_Summary_and_Status_Report.md
using ReportLab with TrueType Arial fonts, custom NumberedCanvas, compact typography, styled tables, and clean layout.
"""

import os
import re
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
MD_PATH = WORKSPACE / "Project_Summary_and_Status_Report.md"
PDF_PATH = WORKSPACE / "Project_Summary_and_Status_Report.pdf"

FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
pdfmetrics.registerFont(TTFont("Arial", str(FONTS_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTS_DIR / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", str(FONTS_DIR / "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", str(FONTS_DIR / "arialbi.ttf")))


class NumberedCanvas(canvas.Canvas):
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

        # Header (on page > 1)
        if self._pageNumber > 1:
            self.drawString(15 * mm, 287 * mm, "VeriCBAM — Executive Summary & Status Report | M.Sc. Data Science")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(15 * mm, 284 * mm, 195 * mm, 284 * mm)

        # Footer (on all pages)
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(195 * mm, 10 * mm, footer_text)
        self.drawString(15 * mm, 10 * mm, "VeriCBAM Project Status Report | Supervisor: Dr. Humera Noor | University of Europe for Applied Sciences (Potsdam)")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(15 * mm, 13 * mm, 195 * mm, 13 * mm)
        self.restoreState()


def parse_braced_arg(s: str, start_idx: int):
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

    text = re.sub(r"(\d+(?:,\d+)?)\s*\^\\circ\\text\{C\}", r"\1°C", text)
    text = re.sub(r"(\d+(?:,\d+)?)\s*\^\\circ C", r"\1°C", text)
    text = re.sub(r"\^\\circ\\text\{C\}", "°C", text)
    text = re.sub(r"\^\\circ", "°", text)

    text = re.sub(r"\\xrightarrow\{\\Delta H\s*=\s*\+?178\\text\{ kJ/mol\}\}", " —[ ΔH = +178 kJ/mol ]→ ", text)
    text = re.sub(r"\\xrightarrow\{([^}]+)\}", r" —[ \1 ]→ ", text)

    text = replace_fractions(text)

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
    text = text.replace(r"\text{ t CO}_2/\text{t}", " t CO<sub>2</sub>/t").replace(r"t CO_2/t", "t CO<sub>2</sub>/t")
    text = text.replace(r"\text{ t/t}", " t/t")
    text = text.replace(r"\text{ km}", " km").replace(r"\text{km}", " km")
    text = text.replace(r"\text{mol/m}^2", "mol/m<sup>2</sup>").replace("mol/m²", "mol/m<sup>2</sup>")

    text = text.replace(r"\gamma", "γ").replace(r"\Gamma", "Γ")
    text = text.replace(r"\delta", "δ").replace(r"\Delta", "Δ")
    text = text.replace(r"\sigma", "σ").replace(r"\Sigma", "Σ")
    text = text.replace(r"\tau", "τ")
    text = text.replace(r"\eta", "η")
    text = text.replace(r"\mu", "μ")
    text = text.replace(r"\rho", "ρ")

    text = text.replace(r"\ln", "ln").replace(r"\max", "max").replace(r"\min", "min")
    text = text.replace(r"\left(", "(").replace(r"\right)", ")")
    text = text.replace(r"\left[", "[").replace(r"\right]", "]")
    text = text.replace(r"\mid", "|").replace(r"\approx", "≈").replace(r"\le", "≤").replace(r"\ge", "≥")
    text = text.replace(r"\in", " in ").replace(r"\times", "×").replace(r"\cdot", "·").replace(r"\neq", "≠")
    text = text.replace(r"\longrightarrow", " → ").replace(r"\rightarrow", " → ")
    text = text.replace(r"\%", "%").replace(r"\{", "{").replace(r"\}", "}")
    text = text.replace(r"\hat{Q}", "Q̂").replace(r"\hat{p}", "p̂")

    text = re.sub(r"\\text\{([^}]+)\}", r"\1", text)
    text = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", text)
    text = text.replace(r"--", "–")
    return re.sub(r"\s+", " ", text).strip()


def clean_markdown_inline(text: str) -> str:
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<font color="#2B6CB0"><u>\1</u></font>', text)

    def replace_code(m):
        code_val = m.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<font face="Courier" color="#1A365D">{code_val}</font>'
    text = re.sub(r"`(.*?)`", replace_code, text)

    def replace_inline_math(m):
        raw_math = m.group(1)
        conv = convert_latex_math(raw_math, is_display=False)
        return f'<i>{conv}</i>'
    text = re.sub(r"\$([^\$\n]+)\$", replace_inline_math, text)

    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\w)\*([^\*]+)\*(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"(?<=\s)_([^_]+)_(?=\s|[.,;:!?)])", r"<i>\1</i>", text)

    text = text.replace("CO2", "CO<sub>2</sub>").replace("NOx", "NO<sub>x</sub>").replace("SOx", "SO<sub>x</sub>")
    text = text.replace("CaCO3", "CaCO<sub>3</sub>").replace("Fe2O3", "Fe<sub>2</sub>O<sub>3</sub>")
    return text


def build_pdf():
    print(f"Reading markdown from: {MD_PATH}")
    content = MD_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A365D"),
        alignment=TA_LEFT,
        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2B6CB0"),
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor("#2D3748"),
        alignment=TA_JUSTIFY,
        spaceAfter=3.5,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=10,
        firstLineIndent=-7,
        spaceAfter=2.5,
    )

    formula_style = ParagraphStyle(
        "Formula_Custom",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1A365D"),
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=2,
    )

    meta_key_style = ParagraphStyle("MetaKey", fontName="Arial-Bold", fontSize=7.5, leading=10, textColor=colors.HexColor("#2B6CB0"))
    meta_val_style = ParagraphStyle("MetaVal", fontName="Arial", fontSize=7.5, leading=10, textColor=colors.HexColor("#2D3748"))

    story = []

    # Title & Subtitle
    story.append(Paragraph("VeriCBAM: Project Summary & Executive Status Report", title_style))
    story.append(Paragraph("Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment", subtitle_style))

    # Meta card
    meta_data = [
        [Paragraph("Author:", meta_key_style), Paragraph("Cristhian David Cáceres Mateus (M.Sc. Data Science)", meta_val_style),
         Paragraph("Institution:", meta_key_style), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_val_style)],
        [Paragraph("Supervisor:", meta_key_style), Paragraph("Dr. Humera Noor", meta_val_style),
         Paragraph("Live Cockpit URL:", meta_key_style), Paragraph('<font color="#2B6CB0"><u>https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/</u></font>', meta_val_style)],
    ]
    meta_tbl = Table(meta_data, colWidths=[20 * mm, 70 * mm, 24 * mm, 66 * mm])
    meta_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2B6CB0"), spaceAfter=5))

    # Advance past markdown frontmatter
    i = 0
    for idx, l in enumerate(lines[:20]):
        if l.strip() in ["---", "***", "___"]:
            i = idx + 1
            break

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
        avail_width = 180 * mm
        if col_count == 8:
            col_w = [25*mm, 27*mm, 22*mm, 15*mm, 16*mm, 18*mm, 21*mm, 36*mm]
        else:
            col_w = [avail_width / col_count] * col_count
        t = Table(parsed_rows, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        return t

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

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
                    story.append(Spacer(1, 3))
                table_raw_rows = []
                in_table = False

        if not stripped:
            i += 1
            continue

        if stripped in ["---", "***", "___"]:
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceBefore=3, spaceAfter=4))
            i += 1
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(clean_markdown_inline(stripped[4:]), h1_style))
            i += 1
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(clean_markdown_inline(stripped[3:]), h1_style))
            i += 1
            continue

        if stripped.startswith("$$"):
            formula_clean = convert_latex_math(stripped, is_display=True)
            formula_p = Paragraph(formula_clean, formula_style)
            formula_box = Table([[formula_p]], colWidths=[180 * mm])
            formula_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            story.append(formula_box)
            story.append(Spacer(1, 2.5))
            i += 1
            continue

        if stripped.startswith("* ") or stripped.startswith("- ") or stripped.startswith("• "):
            bullet_text = clean_markdown_inline(stripped[2:])
            story.append(Paragraph(f"• &nbsp; {bullet_text}", bullet_style))
            i += 1
            continue

        m_num = re.match(r"^(\d+[\.\)])\s+(.*)", stripped)
        if m_num:
            num_label = m_num.group(1)
            num_text = clean_markdown_inline(m_num.group(2))
            story.append(Paragraph(f"<b>{num_label}</b> &nbsp; {num_text}", bullet_style))
            i += 1
            continue

        story.append(Paragraph(clean_markdown_inline(stripped), body_style))
        i += 1

    if in_table and table_raw_rows:
        tbl = flush_table(table_raw_rows)
        if tbl:
            story.append(tbl)

    print(f"Building summary PDF at: {PDF_PATH} ...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Summary PDF generated successfully!")


if __name__ == "__main__":
    build_pdf()
