"""
Generates the 2-page submissions/05_Project_Summary_and_Status_Report_v1.pdf
from docs/sources/Project_Summary_and_Status_Report.md using shared scripts/pdf_utils.py.
"""

import re
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

sys.path.insert(0, str(Path(__file__).parent))
from pdf_utils import (
    DOCS_SOURCES_DIR,
    SUBMISSIONS_DIR,
    MAIN_FONT,
    BOLD_FONT,
    make_numbered_canvas,
    convert_latex_math,
    clean_markdown_inline,
)

MD_PATH = DOCS_SOURCES_DIR / "Project_Summary_and_Status_Report.md"
PDF_PATH = SUBMISSIONS_DIR / "05_Project_Summary_and_Status_Report_v1.pdf"


def build_pdf():
    print(f"Reading markdown from: {MD_PATH}")
    lines = MD_PATH.read_text(encoding="utf-8").splitlines()

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("DocTitle", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=15, leading=18, textColor=colors.HexColor("#1A365D"), alignment=TA_LEFT, spaceAfter=2)
    subtitle_style = ParagraphStyle("DocSubtitle", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=9.5, leading=13, textColor=colors.HexColor("#2B6CB0"), alignment=TA_LEFT, spaceAfter=6)
    h1_style = ParagraphStyle("Heading1_Custom", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=10, leading=13, textColor=colors.HexColor("#1A365D"), spaceBefore=7, spaceAfter=3, keepWithNext=True)
    body_style = ParagraphStyle("Body_Custom", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=7.8, leading=10.5, textColor=colors.HexColor("#2D3748"), alignment=TA_JUSTIFY, spaceAfter=3.5)
    bullet_style = ParagraphStyle("Bullet_Custom", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=7.8, leading=10.2, textColor=colors.HexColor("#2D3748"), leftIndent=10, firstLineIndent=-7, spaceAfter=2.5)
    formula_style = ParagraphStyle("Formula_Custom", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=8, leading=11, textColor=colors.HexColor("#1A365D"), alignment=TA_CENTER, spaceBefore=2, spaceAfter=2)
    meta_key_style = ParagraphStyle("MetaKey", fontName=BOLD_FONT, fontSize=7.5, leading=10, textColor=colors.HexColor("#2B6CB0"))
    meta_val_style = ParagraphStyle("MetaVal", fontName=MAIN_FONT, fontSize=7.5, leading=10, textColor=colors.HexColor("#2D3748"))

    story = [
        Paragraph("VeriCBAM: Project Summary & Executive Status Report", title_style),
        Paragraph("Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment", subtitle_style),
    ]

    meta_data = [
        [Paragraph("Author:", meta_key_style), Paragraph("Cristhian David Cáceres Mateus (M.Sc. Data Science)", meta_val_style),
         Paragraph("Institution:", meta_key_style), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_val_style)],
        [Paragraph("Supervisor:", meta_key_style), Paragraph("Dr. Humera Noor", meta_val_style),
         Paragraph("Live Cockpit URL:", meta_key_style), Paragraph('<font color="#2B6CB0"><u>https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/</u></font>', meta_val_style)],
    ]
    meta_tbl = Table(meta_data, colWidths=[20 * mm, 70 * mm, 24 * mm, 66 * mm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2B6CB0"), spaceAfter=5))

    start_idx = next((idx + 1 for idx, l in enumerate(lines[:20]) if l.strip() in ["---", "***", "___"]), 0)

    def flush_table(rows):
        if not rows:
            return None
        parsed_rows = [[Paragraph(clean_markdown_inline(c.strip()), body_style) for c in r] for r in rows]
        col_count = len(parsed_rows[0])
        col_w = [25 * mm, 27 * mm, 22 * mm, 15 * mm, 16 * mm, 18 * mm, 21 * mm, 36 * mm] if col_count == 8 else [180 * mm / col_count] * col_count
        t = Table(parsed_rows, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]))
        return t

    in_table = False
    table_raw_rows = []
    for line in lines[start_idx:]:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if re.match(r"^\|(\s*:?-+:?\s*\|)+$", stripped):
                continue
            table_raw_rows.append(stripped.split("|")[1:-1])
            in_table = True
            continue
        elif in_table:
            tbl = flush_table(table_raw_rows)
            if tbl:
                story.append(tbl)
                story.append(Spacer(1, 3))
            table_raw_rows = []
            in_table = False

        if not stripped:
            continue
        if stripped in ["---", "***", "___"]:
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceBefore=3, spaceAfter=4))
        elif stripped.startswith("### "):
            story.append(Paragraph(clean_markdown_inline(stripped[4:]), h1_style))
        elif stripped.startswith("## "):
            story.append(Paragraph(clean_markdown_inline(stripped[3:]), h1_style))
        elif stripped.startswith("$$"):
            formula_p = Paragraph(convert_latex_math(stripped, is_display=True), formula_style)
            formula_box = Table([[formula_p]], colWidths=[180 * mm])
            formula_box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]))
            story.append(formula_box)
            story.append(Spacer(1, 2.5))
        elif stripped.startswith(("* ", "- ", "• ")):
            story.append(Paragraph(f"• &nbsp; {clean_markdown_inline(stripped[2:])}", bullet_style))
        elif m_num := re.match(r"^(\d+[\.\)])\s+(.*)", stripped):
            story.append(Paragraph(f"<b>{m_num.group(1)}</b> &nbsp; {clean_markdown_inline(m_num.group(2))}", bullet_style))
        else:
            story.append(Paragraph(clean_markdown_inline(stripped), body_style))

    if in_table and table_raw_rows:
        tbl = flush_table(table_raw_rows)
        if tbl:
            story.append(tbl)

    print(f"Building summary PDF at: {PDF_PATH} ...")
    canvas_cls = make_numbered_canvas(
        "VeriCBAM Project Status Report | Supervisor: Dr. Humera Noor | University of Europe for Applied Sciences (Potsdam)",
        header_text="VeriCBAM — Executive Summary & Status Report | M.Sc. Data Science",
        margin_mm=15.0,
        font_size=8.0,
        report_page_check=True,
    )
    try:
        doc.build(story, canvasmaker=canvas_cls)
        print("Summary PDF generated successfully!")
    except PermissionError:
        print(f"Skipped overwrite: '{PDF_PATH.name}' is currently open in a PDF viewer. Close it to update on disk.")


if __name__ == "__main__":
    build_pdf()
