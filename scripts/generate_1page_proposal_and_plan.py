"""
Generates:
1. Capstone_Proposal_1Page.pdf (strictly 1-page core Stage 1 proposal from Capstone_Proposal_1Page.md)
2. Capstone_Project_Plan.pdf (standalone Project Plan with visual Gantt chart, Sprint Schedule, Risk Matrix, Deliverables, and Roadmap from Capstone_Project_Plan.md)
"""

import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle

WORKSPACE = Path(r"c:\Users\crist\Projects\UEprojects\Capstone")
PROPOSAL_1P_MD = WORKSPACE / "Capstone_Proposal_1Page.md"
PROPOSAL_1P_PDF = WORKSPACE / "Capstone_Proposal_1Page.pdf"

PLAN_MD = WORKSPACE / "Capstone_Project_Plan.md"
PLAN_PDF = WORKSPACE / "Capstone_Project_Plan.pdf"

FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
pdfmetrics.registerFont(TTFont("Arial", str(FONTS_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTS_DIR / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", str(FONTS_DIR / "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", str(FONTS_DIR / "arialbi.ttf")))


class Proposal1PageCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        print(f"  [Page Check] Rendered {num_pages} page(s)")
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Arial", 7.2)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(13 * mm, 11 * mm, 197 * mm, 11 * mm)
        self.drawString(
            13 * mm, 7.8 * mm,
            "VeriCBAM Capstone Proposal (Stage 1 Core) | Cristhian David Cáceres Mateus (93515346) | Supervisor: Dr. Humera Noor | UE Germany (Potsdam)"
        )
        self.drawRightString(197 * mm, 7.8 * mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


class ProjectPlanCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        print(f"  [Page Check] Rendered {num_pages} page(s)")
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Arial", 7.5)
        self.setFillColor(colors.HexColor("#4A5568"))
        if self._pageNumber > 1:
            self.drawString(15 * mm, 287 * mm, "VeriCBAM — Capstone Project Work Plan, Risk Matrix & Execution Roadmap")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(15 * mm, 284 * mm, 195 * mm, 284 * mm)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(15 * mm, 12 * mm, 195 * mm, 12 * mm)
        self.drawString(
            15 * mm, 8.5 * mm,
            "VeriCBAM Project Plan | Cristhian David Cáceres Mateus (93515346) | Supervisor: Dr. Humera Noor | UE Germany (Potsdam)"
        )
        self.drawRightString(195 * mm, 8.5 * mm, f"Page {self._pageNumber} of {page_count}")
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
    else:
        if text.startswith("$") and text.endswith("$"):
            text = text[1:-1].strip()

    text = re.sub(r"(\d+(?:,\d+)?)\s*\^\\circ\\text\{C\}", r"\1°C", text)
    text = re.sub(r"\^\\circ\\text\{C\}", "°C", text)
    text = re.sub(r"\^\\circ", "°", text)
    text = replace_fractions(text)

    text = text.replace(r"\text{CaCO}_3", "CaCO<sub>3</sub>").replace(r"CaCO_3", "CaCO<sub>3</sub>")
    text = text.replace(r"\text{CaO}", "CaO")
    text = text.replace(r"\text{CO}_2", "CO<sub>2</sub>").replace(r"CO_2", "CO<sub>2</sub>").replace(r"\text{CO}", "CO")
    text = text.replace(r"\text{NO}_x", "NO<sub>x</sub>").replace(r"NO_x", "NO<sub>x</sub>")
    text = text.replace(r"\text{NO}_2", "NO<sub>2</sub>").replace(r"NO_2", "NO<sub>2</sub>")
    text = text.replace(r"\text{SO}_x", "SO<sub>x</sub>").replace(r"SO_x", "SO<sub>x</sub>")
    text = text.replace(r"\text{Fe}_2\text{O}_3", "Fe<sub>2</sub>O<sub>3</sub>")
    text = text.replace(r"\text{Fe}", "Fe")
    text = text.replace(r"t\text{CO}_2e", "t CO<sub>2</sub>e")
    text = text.replace(r"\text{ t CO}_2/\text{t clinker}", " t CO<sub>2</sub>/t clinker")
    text = text.replace(r"\text{ t CO}_2/\text{t}", " t CO<sub>2</sub>/t")
    text = text.replace(r"\text{ t/t}", " t/t")
    text = text.replace(r"\text{ km}", " km")
    text = text.replace(r"\text{qa\_value}", "qa_value")

    text = text.replace(r"\gamma", "γ").replace(r"\delta", "δ").replace(r"\Delta", "Δ")
    text = text.replace(r"\sigma", "σ").replace(r"\Sigma", "Σ").replace(r"\eta", "η")
    text = text.replace(r"\operatorname{logit}", "logit").replace(r"\operatorname{LR}", "LR")
    text = text.replace(r"\hat{Q}", "Q̂").replace(r"\hat{p}", "p̂")
    text = text.replace(r"\bar{V}_{\text{target}}", "V<sub>target</sub>").replace(r"\bar{V}_{\text{bg}}", "V<sub>bg</sub>")
    text = text.replace(r"\ln", "ln").replace(r"\max", "max").replace(r"\min", "min")
    text = text.replace(r"\sum_{k=1}^{5}", "Σ<sub>k=1..5</sub>").replace(r"\sum_{k=1}^5", "Σ<sub>k=1..5</sub>")
    text = text.replace(r"\left(", "(").replace(r"\right)", ")")
    text = text.replace(r"\mid", "|").replace(r"\approx", "≈").replace(r"\le", "≤").replace(r"\ge", "≥")
    text = text.replace(r"\in", " in ").replace(r"\times", "×").replace(r"\cdot", "·")
    text = text.replace(r"\Rightarrow", " → ").replace(r"\rightarrow", " → ")
    text = text.replace(r"\delta^*", "δ<sup>*</sup>")
    text = text.replace(r"\qquad", " &nbsp; &nbsp; &nbsp; ")
    text = text.replace(r"\%", "%").replace(r"\{", "{").replace(r"\}", "}")
    text = re.sub(r"\\text\{([^}]+)\}", r"\1", text)
    text = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", text)
    text = re.sub(r"_([A-Za-z0-9]+)", r"<sub>\1</sub>", text)
    text = text.replace("qa<sub>value</sub>", "qa_value")
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
    text = text.replace("CO2", "CO<sub>2</sub>").replace("NOx", "NO<sub>x</sub>").replace("SOx", "SO<sub>x</sub>")
    text = text.replace("CaCO3", "CaCO<sub>3</sub>").replace("Fe2O3", "Fe<sub>2</sub>O<sub>3</sub>")
    return text


def build_gantt_drawing() -> Drawing:
    """Draws a crisp visual Gantt chart for Winter 2026/2027 (Oct 2026 – Jan 2027)."""
    w = 180 * mm
    h = 56 * mm
    d = Drawing(w, h)

    # Background card
    d.add(Rect(0, 0, w, h, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#CBD5E0"), strokeWidth=0.6, rx=3, ry=3))

    # Title banner
    d.add(Rect(0, h - 7 * mm, w, 7 * mm, fillColor=colors.HexColor("#1A365D"), strokeColor=None))
    d.add(String(4 * mm, h - 4.8 * mm, "VeriCBAM Execution Gantt Chart & Milestone Timeline (Winter Semester 2026/2027)", fontName="Arial-Bold", fontSize=8, fillColor=colors.white))

    # Timeline columns: Left label area = 54mm, Chart area = 122mm (x from 54mm to 176mm)
    x0 = 54 * mm
    cw = 122 * mm
    months = ["October 2026", "November 2026", "December 2026", "January 2027"]
    mw = cw / 4.0

    # Month headers
    y_top = h - 12 * mm
    for idx, m_label in enumerate(months):
        mx = x0 + idx * mw
        d.add(Rect(mx, y_top, mw, 5 * mm, fillColor=colors.HexColor("#EDF2F7"), strokeColor=colors.HexColor("#CBD5E0"), strokeWidth=0.4))
        d.add(String(mx + mw / 2.0, y_top + 1.5 * mm, m_label, fontName="Arial-Bold", fontSize=7, fillColor=colors.HexColor("#2D3748"), textAnchor="middle"))
        # Vertical grid line
        d.add(Line(mx, 3 * mm, mx, y_top, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.5))
    d.add(Line(x0 + cw, 3 * mm, x0 + cw, y_top, strokeColor=colors.HexColor("#CBD5E0"), strokeWidth=0.5))

    # 6 Sprint rows (normalized 0.0 = Oct 1, 1.0 = Jan 25 -> 116 days total)
    # Oct 3 = 0.02, Oct 14 = 0.12
    # Oct 15 = 0.13, Nov 9 = 0.34
    # Nov 10 = 0.35, Nov 23 = 0.47
    # Nov 24 = 0.48, Dec 7 = 0.60
    # Dec 8 = 0.61, Dec 21 = 0.73
    # Dec 22 = 0.74, Jan 18 = 0.96
    sprints = [
        ("Sprint 0: Cohort & Registry", 0.02, 0.12, "#2B6CB0", "M1: Oct 12", 0.10),
        ("Sprint 1: Stoichiometry & Proposal", 0.13, 0.34, "#2B6CB0", "M2: Oct 26 / PR1: Nov 9", 0.23),
        ("Sprint 2: S-5P & Ratio Baselines", 0.35, 0.47, "#3182CE", "PR2: Nov 23", 0.47),
        ("Sprint 3: Bayesian & GroupKFold", 0.48, 0.60, "#3182CE", "PR3: Dec 07", 0.60),
        ("Sprint 4: 8-Tab Cockpit & Dossier", 0.61, 0.73, "#38A169", "PR4: Dec 21", 0.73),
        ("Sprint 5: Thesis & Oral Defense", 0.74, 0.96, "#805AD5", "Sub: Jan 4 / Def: Jan 18", 0.95),
    ]

    row_h = 6.2 * mm
    for idx, (label, s_start, s_end, col_hex, m_label, m_pos) in enumerate(sprints):
        ry = y_top - (idx + 1) * row_h - 1 * mm
        # Alternating row tint
        if idx % 2 == 1:
            d.add(Rect(2 * mm, ry - 0.8 * mm, w - 4 * mm, row_h, fillColor=colors.HexColor("#F1F5F9"), strokeColor=None))
        # Row label
        d.add(String(3.5 * mm, ry + 1.2 * mm, label, fontName="Arial-Bold", fontSize=6.8, fillColor=colors.HexColor("#1E293B")))
        # Bar
        bx = x0 + s_start * cw
        bw = (s_end - s_start) * cw
        d.add(Rect(bx, ry + 0.4 * mm, bw, 3.8 * mm, fillColor=colors.HexColor(col_hex), strokeColor=None, rx=1.5, ry=1.5))
        # Milestone marker diamond/circle + label
        mx_pt = x0 + m_pos * cw
        d.add(Circle(mx_pt, ry + 2.3 * mm, 1.3 * mm, fillColor=colors.HexColor("#F6E05E"), strokeColor=colors.HexColor("#1A202C"), strokeWidth=0.6))
        label_x = min(bx + bw + 2 * mm, x0 + cw - 26 * mm)
        if idx == 5:
            label_x = bx - 29 * mm
        d.add(String(label_x, ry + 1.2 * mm, m_label, fontName="Arial-Italic", fontSize=6.3, fillColor=colors.HexColor("#1A365D")))

    return d


def build_1page_proposal():
    print(f"Building 1-Page Proposal PDF: {PROPOSAL_1P_PDF}")
    content = PROPOSAL_1P_MD.read_text(encoding="utf-8")
    lines = content.splitlines()

    doc = SimpleDocTemplate(
        str(PROPOSAL_1P_PDF),
        pagesize=A4,
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=11 * mm,
        bottomMargin=13 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("P1_Title", parent=styles["Normal"], fontName="Arial-Bold", fontSize=13.5, leading=16, textColor=colors.HexColor("#1A365D"), spaceAfter=1)
    subtitle_style = ParagraphStyle("P1_Sub", parent=styles["Normal"], fontName="Arial-Bold", fontSize=8.8, leading=11, textColor=colors.HexColor("#2B6CB0"), spaceAfter=4)
    h1_style = ParagraphStyle("P1_H1", parent=styles["Normal"], fontName="Arial-Bold", fontSize=9.0, leading=11.2, textColor=colors.HexColor("#1A365D"), spaceBefore=4.5, spaceAfter=1.8, keepWithNext=True)
    body_style = ParagraphStyle("P1_Body", parent=styles["Normal"], fontName="Arial", fontSize=7.45, leading=9.6, textColor=colors.HexColor("#2D3748"), alignment=TA_JUSTIFY, spaceAfter=2.2)
    bullet_style = ParagraphStyle("P1_Bullet", parent=styles["Normal"], fontName="Arial", fontSize=7.35, leading=9.4, textColor=colors.HexColor("#2D3748"), leftIndent=9, firstLineIndent=-6, spaceAfter=1.6)
    callout_style = ParagraphStyle("P1_Callout", parent=styles["Normal"], fontName="Arial-BoldItalic", fontSize=7.5, leading=9.8, textColor=colors.HexColor("#1A365D"), alignment=TA_LEFT)
    formula_style = ParagraphStyle("P1_Formula", parent=styles["Normal"], fontName="Arial-Bold", fontSize=7.6, leading=10.0, textColor=colors.HexColor("#1A365D"), alignment=TA_CENTER, spaceBefore=1.5, spaceAfter=1.5)
    meta_k = ParagraphStyle("P1_MK", fontName="Arial-Bold", fontSize=7.3, leading=9.2, textColor=colors.HexColor("#2B6CB0"))
    meta_v = ParagraphStyle("P1_MV", fontName="Arial", fontSize=7.3, leading=9.2, textColor=colors.HexColor("#2D3748"))

    story = []
    story.append(Paragraph("Capstone Project Proposal: VeriCBAM (Stage 1 Core Summary)", title_style))
    story.append(Paragraph("Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment", subtitle_style))

    meta_data = [
        [Paragraph("Student Name:", meta_k), Paragraph("Cristhian David Cáceres Mateus (ID: 93515346)", meta_v),
         Paragraph("Institution:", meta_k), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_v)],
        [Paragraph("Degree Program:", meta_k), Paragraph("M.Sc. in Data Science (Winter 2026/2027)", meta_v),
         Paragraph("Faculty Supervisor:", meta_k), Paragraph("Dr. Humera Noor", meta_v)],
    ]
    meta_tbl = Table(meta_data, colWidths=[24 * mm, 64 * mm, 27 * mm, 69 * mm])
    meta_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 3))

    start_idx = 0
    for idx, l in enumerate(lines[:15]):
        if l.strip() == "---":
            start_idx = idx + 1
            break

    for line in lines[start_idx:]:
        s = line.strip()
        if not s or s == "---":
            continue
        if s.startswith("### "):
            story.append(Paragraph(clean_markdown_inline(s[4:]), h1_style))
            story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#CBD5E0"), spaceAfter=1.8))
        elif s.startswith("> "):
            q_text = clean_markdown_inline(s[2:])
            q_box = Table([[Paragraph(q_text, callout_style)]], colWidths=[184 * mm])
            q_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#90CDF4")),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
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

    doc.build(story, canvasmaker=Proposal1PageCanvas)


def build_project_plan():
    print(f"Building Standalone Project Plan PDF: {PLAN_PDF}")
    content = PLAN_MD.read_text(encoding="utf-8")
    lines = content.splitlines()

    doc = SimpleDocTemplate(
        str(PLAN_PDF),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=14 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("PP_Title", parent=styles["Normal"], fontName="Arial-Bold", fontSize=14, leading=17, textColor=colors.HexColor("#1A365D"), spaceAfter=1.5)
    subtitle_style = ParagraphStyle("PP_Sub", parent=styles["Normal"], fontName="Arial-Bold", fontSize=9, leading=11.5, textColor=colors.HexColor("#2B6CB0"), spaceAfter=5)
    h1_style = ParagraphStyle("PP_H1", parent=styles["Normal"], fontName="Arial-Bold", fontSize=9.8, leading=12.5, textColor=colors.HexColor("#1A365D"), spaceBefore=6, spaceAfter=2.5, keepWithNext=True)
    body_style = ParagraphStyle("PP_Body", parent=styles["Normal"], fontName="Arial", fontSize=7.8, leading=10.4, textColor=colors.HexColor("#2D3748"), alignment=TA_JUSTIFY, spaceAfter=3)
    bullet_style = ParagraphStyle("PP_Bullet", parent=styles["Normal"], fontName="Arial", fontSize=7.8, leading=10.2, textColor=colors.HexColor("#2D3748"), leftIndent=10, firstLineIndent=-7, spaceAfter=2)
    th_style = ParagraphStyle("PP_TH", parent=styles["Normal"], fontName="Arial-Bold", fontSize=7.4, leading=9.4, textColor=colors.white)
    td_style = ParagraphStyle("PP_TD", parent=styles["Normal"], fontName="Arial", fontSize=7.2, leading=9.3, textColor=colors.HexColor("#2D3748"))
    meta_k = ParagraphStyle("PP_MK", fontName="Arial-Bold", fontSize=7.5, leading=9.8, textColor=colors.HexColor("#2B6CB0"))
    meta_v = ParagraphStyle("PP_MV", fontName="Arial", fontSize=7.5, leading=9.8, textColor=colors.HexColor("#2D3748"))

    story = []
    story.append(Paragraph("VeriCBAM: Capstone Project Work Plan, Risk Matrix & Execution Roadmap", title_style))
    story.append(Paragraph("Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment", subtitle_style))

    meta_data = [
        [Paragraph("Student Name:", meta_k), Paragraph("Cristhian David Cáceres Mateus (ID: 93515346)", meta_v),
         Paragraph("Institution:", meta_k), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_v)],
        [Paragraph("Degree Program:", meta_k), Paragraph("Master of Science in Data Science (M.Sc. DSc)", meta_v),
         Paragraph("Faculty Supervisor:", meta_k), Paragraph("Dr. Humera Noor | Winter Semester 2026/2027", meta_v)],
    ]
    meta_tbl = Table(meta_data, colWidths=[24 * mm, 63 * mm, 27 * mm, 66 * mm])
    meta_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 5))

    # Add Visual Gantt Chart Drawing at top of Section 1
    story.append(build_gantt_drawing())
    story.append(Spacer(1, 4))

    start_idx = 0
    for idx, l in enumerate(lines[:15]):
        if l.strip() == "---":
            start_idx = idx + 1
            break

    in_table = False
    table_rows = []

    def flush_table(rows):
        if not rows:
            return None
        parsed = []
        for r_idx, r in enumerate(rows):
            style_to_use = th_style if r_idx == 0 else td_style
            parsed.append([Paragraph(clean_markdown_inline(c.strip()), style_to_use) for c in r])
        cols = len(parsed[0])
        if cols == 4:
            col_w = [34 * mm, 29 * mm, 72 * mm, 45 * mm]
        elif cols == 5:
            col_w = [34 * mm, 16 * mm, 18 * mm, 42 * mm, 70 * mm]
        else:
            col_w = [180 * mm / cols] * cols
        t = Table(parsed, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
        ]))
        return t

    for line in lines[start_idx:]:
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            inner = [c.strip() for c in s.strip("|").split("|")]
            if all(re.match(r"^:?-+:?$", c) for c in inner):
                continue
            in_table = True
            table_rows.append(inner)
            continue
        else:
            if in_table:
                tbl = flush_table(table_rows)
                if tbl:
                    story.append(tbl)
                    story.append(Spacer(1, 3.5))
                in_table = False
                table_rows = []

        if not s or s == "---":
            continue
        if s.startswith("### "):
            story.append(Paragraph(clean_markdown_inline(s[4:]), h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceAfter=2.5))
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

    doc.build(story, canvasmaker=ProjectPlanCanvas)


if __name__ == "__main__":
    build_1page_proposal()
    build_project_plan()
