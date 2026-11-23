"""
Generates directly into submissions/:
1. 02_Project_Proposal.pdf (strictly 1-page core proposal from docs/sources/Capstone_Proposal_1Page.md)
2. 03_Project_Execution_Plan.pdf (strictly 1-page plan with Gantt chart from docs/sources/Capstone_Project_Plan.md)
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
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle

sys.path.insert(0, str(Path(__file__).parent))
from pdf_utils import (
    DOCS_SOURCES_DIR,
    SUBMISSIONS_DIR,
    MAIN_FONT,
    BOLD_FONT,
    ITALIC_FONT,
    make_numbered_canvas,
    convert_latex_math,
    clean_markdown_inline,
)

PROPOSAL_1P_MD = DOCS_SOURCES_DIR / "Capstone_Proposal_1Page.md"
PROPOSAL_1P_PDF = SUBMISSIONS_DIR / "02_Project_Proposal.pdf"

PLAN_MD = DOCS_SOURCES_DIR / "Capstone_Project_Plan.md"
PLAN_PDF = SUBMISSIONS_DIR / "03_Project_Execution_Plan.pdf"


def build_gantt_drawing() -> Drawing:
    """Draws a crisp visual Gantt chart for Winter 2026/2027 (Oct 2026 – Jan 2027)."""
    w = 184 * mm
    h = 41 * mm
    d = Drawing(w, h)

    d.add(Rect(0, 0, w, h, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#CBD5E0"), strokeWidth=0.6, rx=3, ry=3))
    d.add(Rect(0, h - 5.5 * mm, w, 5.5 * mm, fillColor=colors.HexColor("#1A365D"), strokeColor=None))
    d.add(String(4 * mm, h - 3.8 * mm, "VeriCBAM Execution Gantt Chart & Milestone Timeline (Winter Semester 2026/2027)", fontName=BOLD_FONT, fontSize=7.4, fillColor=colors.white))

    x0 = 54 * mm
    cw = 126 * mm
    months = ["October 2026", "November 2026", "December 2026", "January 2027"]
    mw = cw / 4.0

    y_top = h - 9.5 * mm
    for idx, m_label in enumerate(months):
        mx = x0 + idx * mw
        d.add(Rect(mx, y_top, mw, 4.0 * mm, fillColor=colors.HexColor("#EDF2F7"), strokeColor=colors.HexColor("#CBD5E0"), strokeWidth=0.4))
        d.add(String(mx + mw / 2.0, y_top + 1.1 * mm, m_label, fontName=BOLD_FONT, fontSize=6.5, fillColor=colors.HexColor("#2D3748"), textAnchor="middle"))
        d.add(Line(mx, 2 * mm, mx, y_top, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.5))
    d.add(Line(x0 + cw, 2 * mm, x0 + cw, y_top, strokeColor=colors.HexColor("#CBD5E0"), strokeWidth=0.5))

    sprints = [
        ("Sprint 0: Cohort & Ingestion [DONE]", 0.02, 0.12, "#2E7D32", "M1: Oct 12", 0.10),
        ("Sprint 1: Stoichiometry & Floors [DONE]", 0.13, 0.28, "#2E7D32", "M2: Oct 30", 0.26),
        ("Sprint 2: S-5P & Ratios [DONE]", 0.29, 0.40, "#2E7D32", "5-Stream Pipeline", 0.38),
        ("Sprint 3: Bayesian & Benchmark [DONE]", 0.41, 0.52, "#2E7D32", "325-Case Eval", 0.50),
        ("Sprint 4: Multi-Sensor & Quick Audit [DONE]", 0.53, 0.65, "#2E7D32", "Stage 2 EO Live", 0.63),
        ("Sprint 5: Outreach & Deliverables [ACTIVE]", 0.66, 0.96, "#1565C0", "Bi-Weekly / Jan 04 Final", 0.95),
    ]

    row_h = 4.7 * mm
    for idx, (label, s_start, s_end, col_hex, m_label, m_pos) in enumerate(sprints):
        ry = y_top - (idx + 1) * row_h - 0.2 * mm
        if idx % 2 == 1:
            d.add(Rect(2 * mm, ry - 0.4 * mm, w - 4 * mm, row_h, fillColor=colors.HexColor("#F1F5F9"), strokeColor=None))
        d.add(String(3.5 * mm, ry + 0.9 * mm, label, fontName=BOLD_FONT, fontSize=6.3, fillColor=colors.HexColor("#1E293B")))
        bx = x0 + s_start * cw
        bw = (s_end - s_start) * cw
        d.add(Rect(bx, ry + 0.4 * mm, bw, 3.0 * mm, fillColor=colors.HexColor(col_hex), strokeColor=None, rx=1.2, ry=1.2))
        mx_pt = x0 + m_pos * cw
        d.add(Circle(mx_pt, ry + 1.8 * mm, 1.1 * mm, fillColor=colors.HexColor("#F6E05E"), strokeColor=colors.HexColor("#1A202C"), strokeWidth=0.5))
        label_x = min(bx + bw + 2 * mm, x0 + cw - 26 * mm) if idx != 5 else bx - 29 * mm
        d.add(String(label_x, ry + 0.9 * mm, m_label, fontName=ITALIC_FONT, fontSize=5.9, fillColor=colors.HexColor("#1A365D")))

    return d


def build_1page_proposal():
    print(f"Building 1-Page Proposal PDF: {PROPOSAL_1P_PDF}")
    lines = PROPOSAL_1P_MD.read_text(encoding="utf-8").splitlines()

    doc = SimpleDocTemplate(
        str(PROPOSAL_1P_PDF),
        pagesize=A4,
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=9 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("P1_Title", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=13.5, leading=16.0, textColor=colors.HexColor("#1A365D"), spaceAfter=1.2)
    subtitle_style = ParagraphStyle("P1_Sub", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=9.0, leading=11.2, textColor=colors.HexColor("#2B6CB0"), spaceAfter=3.5)
    h1_style = ParagraphStyle("P1_H1", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=9.2, leading=11.5, textColor=colors.HexColor("#1A365D"), spaceBefore=4.0, spaceAfter=1.5, keepWithNext=True)
    body_style = ParagraphStyle("P1_Body", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=7.9, leading=10.0, textColor=colors.HexColor("#2D3748"), alignment=TA_JUSTIFY, spaceAfter=2.0)
    bullet_style = ParagraphStyle("P1_Bullet", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=7.8, leading=9.8, textColor=colors.HexColor("#2D3748"), leftIndent=9, firstLineIndent=-5.5, spaceAfter=1.6)
    callout_style = ParagraphStyle("P1_Callout", parent=styles["Normal"], fontName="Arial-BoldItalic" if BOLD_FONT == "Arial-Bold" else BOLD_FONT, fontSize=7.9, leading=10.0, textColor=colors.HexColor("#1A365D"), alignment=TA_LEFT)
    formula_style = ParagraphStyle("P1_Formula", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=7.8, leading=9.8, textColor=colors.HexColor("#1A365D"), alignment=TA_CENTER, spaceBefore=1.5, spaceAfter=1.5)
    meta_k = ParagraphStyle("P1_MK", fontName=BOLD_FONT, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#2B6CB0"))
    meta_v = ParagraphStyle("P1_MV", fontName=MAIN_FONT, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#2D3748"))

    story = [
        Paragraph("Capstone Project Proposal: VeriCBAM", title_style),
        Paragraph("A Data-Driven Decision-Support Tool for Screening Carbon Border (CBAM) Emissions Reports", subtitle_style),
    ]

    meta_data = [
        [Paragraph("Student Name:", meta_k), Paragraph("Cristhian David Cáceres Mateus (ID: 93515346)", meta_v),
         Paragraph("Institution:", meta_k), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_v)],
        [Paragraph("Degree Program:", meta_k), Paragraph("M.Sc. in Data Science (Winter 2026/2027)", meta_v),
         Paragraph("Faculty Supervisor:", meta_k), Paragraph("Dr. Humera Noor", meta_v)],
    ]
    meta_tbl = Table(meta_data, colWidths=[24 * mm, 64 * mm, 27 * mm, 69 * mm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 2.5))

    start_idx = next((idx + 1 for idx, l in enumerate(lines[:15]) if l.strip() == "---"), 0)

    for line in lines[start_idx:]:
        s = line.strip()
        if not s or s == "---":
            continue
        if s.startswith("### "):
            story.append(Paragraph(clean_markdown_inline(s[4:]), h1_style))
            story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#CBD5E0"), spaceAfter=1.8))
        elif s.startswith("> "):
            q_box = Table([[Paragraph(clean_markdown_inline(s[2:]), callout_style)]], colWidths=[184 * mm])
            q_box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#90CDF4")),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(q_box)
            story.append(Spacer(1, 1.8))
        elif s.startswith("$$") and s.endswith("$$"):
            story.append(Paragraph(convert_latex_math(s, is_display=True), formula_style))
        elif s.startswith("* ") or s.startswith("- "):
            story.append(Paragraph(f"• {clean_markdown_inline(s[2:])}", bullet_style))
        elif re.match(r"^\d+\.\s", s):
            num_m = re.match(r"^(\d+\.)\s+(.*)", s)
            story.append(Paragraph(f"<b>{num_m.group(1)}</b> {clean_markdown_inline(num_m.group(2))}", bullet_style))
        else:
            story.append(Paragraph(clean_markdown_inline(s), body_style))

    canvas_cls = make_numbered_canvas(
        "VeriCBAM Capstone Proposal (Stage 1 Core) | Cristhian David Cáceres Mateus (93515346) | Supervisor: Dr. Humera Noor | UE Germany (Potsdam)",
        margin_mm=13.0,
        font_size=7.2,
        report_page_check=True,
    )
    doc.build(story, canvasmaker=canvas_cls)


def build_project_plan():
    print(f"Building Standalone Project Plan PDF: {PLAN_PDF}")
    lines = PLAN_MD.read_text(encoding="utf-8").splitlines()

    doc = SimpleDocTemplate(
        str(PLAN_PDF),
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=8 * mm,
        bottomMargin=12 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("PP_Title", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=12.0, leading=14.0, textColor=colors.HexColor("#1A365D"), spaceAfter=1)
    subtitle_style = ParagraphStyle("PP_Sub", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=8.0, leading=9.8, textColor=colors.HexColor("#2B6CB0"), spaceAfter=2.0)
    h1_style = ParagraphStyle("PP_H1", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=8.0, leading=9.8, textColor=colors.HexColor("#1A365D"), spaceBefore=2.0, spaceAfter=0.8, keepWithNext=True)
    body_style = ParagraphStyle("PP_Body", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=6.5, leading=8.0, textColor=colors.HexColor("#2D3748"), alignment=TA_JUSTIFY, spaceAfter=1.0)
    bullet_style = ParagraphStyle("PP_Bullet", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=6.4, leading=7.8, textColor=colors.HexColor("#2D3748"), leftIndent=7, firstLineIndent=-4.8, spaceAfter=0.7)
    th_style = ParagraphStyle("PP_TH", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=6.5, leading=7.8, textColor=colors.white)
    td_style = ParagraphStyle("PP_TD", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=6.2, leading=7.5, textColor=colors.HexColor("#2D3748"))
    meta_k = ParagraphStyle("PP_MK", fontName=BOLD_FONT, fontSize=7.0, leading=8.6, textColor=colors.HexColor("#2B6CB0"))
    meta_v = ParagraphStyle("PP_MV", fontName=MAIN_FONT, fontSize=7.0, leading=8.6, textColor=colors.HexColor("#2D3748"))

    story = [
        Paragraph("VeriCBAM: Capstone Project Work Plan, Risk Matrix & Execution Roadmap", title_style),
        Paragraph("A Data-Driven Decision-Support Tool for Screening Carbon Border (CBAM) Emissions Reports", subtitle_style),
    ]

    meta_data = [
        [Paragraph("Student Name:", meta_k), Paragraph("Cristhian David Cáceres Mateus (ID: 93515346)", meta_v),
         Paragraph("Institution:", meta_k), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_v)],
        [Paragraph("Degree Program:", meta_k), Paragraph("Master of Science in Data Science (M.Sc. DSc)", meta_v),
         Paragraph("Faculty Supervisor:", meta_k), Paragraph("Dr. Humera Noor | Winter Semester 2026/2027", meta_v)],
    ]
    meta_tbl = Table(meta_data, colWidths=[24 * mm, 66 * mm, 27 * mm, 69 * mm])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 2.0))
    story.append(build_gantt_drawing())
    story.append(Spacer(1, 1.5))

    start_idx = next((idx + 1 for idx, l in enumerate(lines[:15]) if l.strip() == "---"), 0)

    def flush_table(rows):
        if not rows:
            return None
        parsed = [[Paragraph(clean_markdown_inline(c.strip()), th_style if r_idx == 0 else td_style) for c in r] for r_idx, r in enumerate(rows)]
        cols = len(parsed[0])
        col_w = [34 * mm, 29 * mm, 74 * mm, 49 * mm] if cols == 4 else ([34 * mm, 16 * mm, 18 * mm, 44 * mm, 74 * mm] if cols == 5 else [186 * mm / cols] * cols)
        t = Table(parsed, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 1.2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
            ("LEFTPADDING", (0, 0), (-1, -1), 3.0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3.0),
        ]))
        return t

    in_table = False
    table_rows = []
    for line in lines[start_idx:]:
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            inner = [c.strip() for c in s.strip("|").split("|")]
            if all(re.match(r"^:?-+:?$", c) for c in inner):
                continue
            in_table = True
            table_rows.append(inner)
            continue
        elif in_table:
            tbl = flush_table(table_rows)
            if tbl:
                story.append(tbl)
                story.append(Spacer(1, 2.5))
            in_table = False
            table_rows = []

        if not s or s == "---":
            continue
        if s.startswith("### "):
            story.append(Paragraph(clean_markdown_inline(s[4:]), h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceAfter=1.8))
        elif s.startswith("* ") or s.startswith("- "):
            story.append(Paragraph(f"• {clean_markdown_inline(s[2:])}", bullet_style))
        elif re.match(r"^\d+\.\s", s):
            num_m = re.match(r"^(\d+\.)\s+(.*)", s)
            story.append(Paragraph(f"<b>{num_m.group(1)}</b> {clean_markdown_inline(num_m.group(2))}", bullet_style))
        else:
            story.append(Paragraph(clean_markdown_inline(s), body_style))

    if in_table and table_rows:
        tbl = flush_table(table_rows)
        if tbl:
            story.append(tbl)

    canvas_cls = make_numbered_canvas(
        "VeriCBAM Project Plan | Cristhian David Cáceres Mateus (93515346) | Supervisor: Dr. Humera Noor | UE Germany (Potsdam)",
        header_text="VeriCBAM — Capstone Project Work Plan, Risk Matrix & Execution Roadmap",
        margin_mm=12.0,
        font_size=7.2,
        report_page_check=True,
    )
    doc.build(story, canvasmaker=canvas_cls)


if __name__ == "__main__":
    build_1page_proposal()
    build_project_plan()
