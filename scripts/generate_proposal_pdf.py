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

# Register TrueType Arial fonts for full Unicode support (accents, euro, math symbols, em-dashes)
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
        self.drawString(20 * mm, 12 * mm, "M.Sc. Data Science Capstone | Student ID: 93515346 | Supervisor: Dr. Humera Noor")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(20 * mm, 15 * mm, 190 * mm, 15 * mm)
        self.restoreState()


def clean_markdown_inline(text: str) -> str:
    """Convert common inline markdown to HTML tags compatible with ReportLab with Arial."""
    # First, protect links: [label](url) -> label
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<font color="#2B6CB0"><u>\1</u></font>', text)

    # Protect inline code: `code` -> monospace font, escaping internal characters
    def replace_code(m):
        code_val = m.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<font face="Courier" color="#1A365D">{code_val}</font>'
    text = re.sub(r"`(.*?)`", replace_code, text)

    # Common chemical and technical math approximations
    text = text.replace(r"\text{CO}_2", "CO₂").replace(r"\text{NO}_x", "NOx").replace(r"\text{SO}_x", "SOx")
    text = text.replace(r"\text{CaO}", "CaO").replace(r"\text{CaCO}_3", "CaCO₃")
    text = text.replace(r"\text{Fe}_2\text{O}_3", "Fe₂O₃").replace(r"\text{Fe}", "Fe")
    text = text.replace(r"\text{CO}", "CO").replace(r"\text{t CO}_2/\text{t}", "t CO₂/t")
    text = text.replace(r"\text{ROC-AUC}", "ROC-AUC").replace(r"\text{PR-AUC}", "PR-AUC")
    text = text.replace(r"\text{ECE}", "ECE").replace(r"\text{FPR}", "FPR")
    text = text.replace(r"\sigma_{\text{pooled}}", "σ_pooled")
    text = text.replace(r"\rightarrow", " → ").replace(r"\approx", " ≈ ").replace(r"\le", " ≤ ").replace(r"\ge", " ≥ ")
    text = text.replace(r"\in", " ∈ ").replace(r"\times", " × ")

    # Math inline: replace $math$ with clean text
    def replace_math(m):
        math_content = m.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        math_content = math_content.replace(r"\delta", "δ").replace(r"\sigma", "σ").replace(r"\tau", "τ").replace(r"\eta", "η")
        math_content = math_content.replace(r"\mu", "μ").replace(r"\rho", "ρ")
        math_content = math_content.replace(r"\text{--}", "–").replace(r"\text{", "").replace(r"}", "")
        return f'<i>{math_content}</i>'
    text = re.sub(r"\$([^\$]+)\$", replace_math, text)

    # Bold italic: ***text***
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<b><i>\1</i></b>", text)
    # Bold: **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # Italic: *text* (avoid touching isolated underscores in filenames)
    text = re.sub(r"(?<!\w)\*([^\*]+)\*(?!\w)", r"<i>\1</i>", text)
    # Underscore italics only when flanked by spaces or punctuation: e.g. " _italic_ "
    text = re.sub(r"(?<=\s)_([^_]+)_(?=\s|[.,;:!?)])", r"<i>\1</i>", text)

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
        fontName="Courier-Bold",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1A365D"),
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=2,
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

    # Metadata Card
    meta_table_data = [
        [Paragraph("Student Name:", meta_key_style), Paragraph("Cristhian David Cáceres Mateus", meta_val_style),
         Paragraph("Matriculation No:", meta_key_style), Paragraph("93515346", meta_val_style)],
        [Paragraph("Degree Program:", meta_key_style), Paragraph("Master of Science in Data Science (M.Sc. DSc)", meta_val_style),
         Paragraph("Institution:", meta_key_style), Paragraph("University of Europe for Applied Sciences (Berlin)", meta_val_style)],
        [Paragraph("Faculty Supervisor:", meta_key_style), Paragraph("Dr. Humera Noor", meta_val_style),
         Paragraph("Submission Date:", meta_key_style), Paragraph("October 2026 (Semester Winter 2026/2027)", meta_val_style)],
        [Paragraph("Official Repository:", meta_key_style), Paragraph("https://github.com/CaceresCristhian/VeriCBAM", meta_val_style),
         Paragraph("Proposal Scope:", meta_key_style), Paragraph("Official Detailed Specification Annex", meta_val_style)],
    ]

    meta_table = Table(meta_table_data, colWidths=[28 * mm, 57 * mm, 30 * mm, 55 * mm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Parse body
    i = 0
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
        # Custom widths for benchmark table if 11 cols
        if col_count == 11:
            col_w = [25*mm, 20*mm, 18*mm, 18*mm, 12*mm, 12*mm, 12*mm, 14*mm, 14*mm, 11*mm, 14*mm]
        elif col_count == 5:
            col_w = [28*mm, 35*mm, 35*mm, 32*mm, 40*mm]
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
                # End of code block
                in_code_block = False
                # If it was a mermaid diagram, render an architectural callout box
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
                    # Render code box
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

        # Centered Math Block ($$...$$)
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            formula_text = stripped[2:-2].strip()
            formula_text = formula_text.replace(r"\operatorname{logit}", "logit").replace(r"\mid", "|")
            formula_text = formula_text.replace(r"\sum_{k=1}^{6}", "Σ (k=1..6)").replace(r"\cdot", "·")
            formula_text = formula_text.replace(r"\ln(\operatorname{LR}_k)", "ln(LR_k)")
            formula_text = formula_text.replace(r"\max\left(0, -\frac{\ln E_{\text{declared}, i, t} - M_{i, -t}}{\sigma_{\text{pooled}}}\right)", "max(0, - (ln E_declared - M) / σ_pooled)")
            formula_text = formula_text.replace(r"\frac{\bar{V}_{\text{target}} - \bar{V}_{\text{bg}}}{1.4826 \times \text{MAD}_{\text{bg}}}", "(V_target - V_bg) / (1.4826 × MAD_bg)")
            formula_text = formula_text.replace(r"\max(0, 1 - f_{\text{cloud}})", "max(0, 1 - f_cloud)")
            formula_text = formula_text.replace(r"\xrightarrow{\Delta H = +178\text{ kJ/mol}}", " —[ ΔH = +178 kJ/mol ]→ ")
            formula_text = formula_text.replace(r"\uparrow", "↑")
            formula_text = clean_markdown_inline(formula_text)
            formula_p = Paragraph(formula_text, formula_style)
            formula_box = Table([[formula_p]], colWidths=[170 * mm])
            formula_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
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
