"""
Generates 06_Quick_User_Guide.pdf using ReportLab.
"""
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
try:
    pdfmetrics.registerFont(TTFont("Arial", str(FONTS_DIR / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTS_DIR / "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Arial-Italic", str(FONTS_DIR / "ariali.ttf")))
    MAIN_FONT = "Arial"
    BOLD_FONT = "Arial-Bold"
    ITALIC_FONT = "Arial-Italic"
except Exception:
    MAIN_FONT = "Helvetica"
    BOLD_FONT = "Helvetica-Bold"
    ITALIC_FONT = "Helvetica-Oblique"


class GuideCanvas(canvas.Canvas):
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
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont(MAIN_FONT, 7.5)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(14 * mm, 11 * mm, 196 * mm, 11 * mm)
        self.drawString(
            14 * mm, 7.8 * mm,
            "VeriCBAM User Guide | Decision Support for CBAM Emissions Auditing | Cristhian David Cáceres Mateus | UE Germany (Potsdam)"
        )
        self.drawRightString(196 * mm, 7.8 * mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_guide_pdf(pdf_path: Path):
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=11 * mm,
        bottomMargin=13 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("G_Title", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=13.5, leading=16.5, textColor=colors.HexColor("#1A365D"), spaceAfter=1)
    subtitle_style = ParagraphStyle("G_Sub", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=8.8, leading=11.5, textColor=colors.HexColor("#2B6CB0"), spaceAfter=4)
    h1_style = ParagraphStyle("G_H1", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=9.0, leading=11.5, textColor=colors.HexColor("#1A365D"), spaceBefore=4, spaceAfter=1.8, keepWithNext=True)
    body_style = ParagraphStyle("G_Body", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=7.4, leading=9.6, textColor=colors.HexColor("#2D3748"), alignment=TA_JUSTIFY, spaceAfter=2.2)
    bullet_style = ParagraphStyle("G_Bullet", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=7.3, leading=9.4, textColor=colors.HexColor("#2D3748"), leftIndent=10, firstLineIndent=-6.5, spaceAfter=1.6)
    meta_k = ParagraphStyle("G_MK", fontName=BOLD_FONT, fontSize=7.3, leading=9.2, textColor=colors.HexColor("#2B6CB0"))
    meta_v = ParagraphStyle("G_MV", fontName=MAIN_FONT, fontSize=7.3, leading=9.2, textColor=colors.HexColor("#2D3748"))

    story = []
    story.append(Paragraph("VeriCBAM: Quick User Guide for Companies & Institutions", title_style))
    story.append(Paragraph("30-Second Screening & Official PDF Audit Dossier Walkthrough", subtitle_style))

    meta_data = [
        [Paragraph("Author:", meta_k), Paragraph("Cristhian David Cáceres Mateus (ID: 93515346)", meta_v),
         Paragraph("Institution:", meta_k), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_v)],
        [Paragraph("Supervisor:", meta_k), Paragraph("Dr. Humera Noor | M.Sc. Data Science", meta_v),
         Paragraph("Live Web App:", meta_k), Paragraph("<font color='#2B6CB0'><u>https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/</u></font>", meta_v)],
    ]
    meta_tbl = Table(meta_data, colWidths=[24 * mm, 64 * mm, 26 * mm, 68 * mm])
    meta_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 2.5))

    intro_box = Table([[Paragraph(
        "<b>Purpose:</b> This guide provides verification bodies (DNV, TÜV, Bureau Veritas), customs authorities (DEHSt), "
        "and industrial importers with a zero-friction walkthrough to audit declared emissions in 30 seconds and export "
        "an official 1-page PDF Pre-Audit Screening Dossier.",
        body_style
    )]], colWidths=[182 * mm])
    intro_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EDF2F7")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(intro_box)
    story.append(Spacer(1, 1.5))

    # Step 1
    story.append(Paragraph("1. Access the Quick Audit Cockpit", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#CBD5E0"), spaceAfter=1.5))
    story.append(Paragraph("Open the live web application at <b>https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/</b>. Ensure that <b>Tab 1: Quick Audit &amp; PDF Dossier Generator</b> is selected in the navigation sidebar (default landing page).", body_style))

    # Step 2
    story.append(Paragraph("2. Select Your Audit Testing Mode", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#CBD5E0"), spaceAfter=1.5))
    story.append(Paragraph("• <b>Option A (Pre-Loaded Reference Plant — Fastest):</b> Select any of the 30 European cement or steel complexes (e.g., <i>ThyssenKrupp Duisburg</i> or <i>Cementownia Górażdże</i>). The system automatically pre-populates verified capacity, historical baselines, and multi-sensor satellite Earth observation signatures (Landsat 30m thermal ΔT, NASA VIIRS 375m active months, Planet VHR rail-yard contrast). Adjust declared production or emissions to test 'what-if' scenarios.", bullet_style))
    story.append(Paragraph("• <b>Option B (External Foreign Supplier — Zero Prior History):</b> Designed specifically for third-country exporters (Turkey, India, China, USA) lacking EU historical registries. Enter the plant name, sector (Cement / Steel), route (BF-BOF, Scrap-EAF, Dry Kiln), production volume, and declared CO<sub>2</sub>. Check <i>'External Facility Lacks Past History (Use Satellite Data Only)'</i> to evaluate the declaration purely via thermodynamic mass balance and satellite operational discrepancy.", bullet_style))
    story.append(Paragraph("• <b>Option C (Upload CSV File):</b> Drag and drop a standard declaration spreadsheet containing facility name, sector, route, production tonnes, and declared CO<sub>2</sub> for automated batch/single parsing.", bullet_style))

    # Step 3
    story.append(Paragraph("3. Inspect the Automated Screening Diagnostic", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#CBD5E0"), spaceAfter=1.5))
    story.append(Paragraph("The platform instantly computes and displays four diagnostic KPI cards:", body_style))
    story.append(Paragraph("• <b>Declared Carbon Intensity:</b> Declared t CO<sub>2</sub> / t product vs. the thermodynamic chemical lower bound (1.350 t/t for BF-BOF steel, 0.770 t/t for clinker).", bullet_style))
    story.append(Paragraph("• <b>Physical Mass Balance:</b> Displays <b>FEASIBLE</b> (green) or <b>VIOLATION</b> (red) with the exact missing CO<sub>2</sub> tonnage deficit.", bullet_style))
    story.append(Paragraph("• <b>Satellite Kiln/Furnace Activity:</b> Shows verified active operating months (out of 12) and localized core heat excess ΔT (°C).", bullet_style))
    story.append(Paragraph("• <b>Inconsistency Risk Score:</b> A calibrated probability score (0% to 100%) synthesized by the Bayesian log-odds engine:", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;– <b>CONSISTENT (&lt; 25%):</b> Green badge — Clear for expedited import filing without on-site inspection.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;– <b>POTENTIAL INCONSISTENCY (25%–70%):</b> Yellow badge — Request technical clarification, CEMS logs, and fuel receipts.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;– <b>HIGH INCONSISTENCY RISK (&gt; 70%):</b> Red badge — Mandatory on-site audit recommended; freeze certificate clearance.", bullet_style))

    # Step 4
    story.append(Paragraph("4. Export the Official Pre-Audit Screening Dossier (PDF)", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.4, color=colors.HexColor("#CBD5E0"), spaceAfter=1.5))
    story.append(Paragraph(
        "At the bottom of Tab 1, click <b>'Download Official Pre-Audit Screening Dossier (PDF)'</b>. "
        "The system instantly generates a publication-ready 1-page PDF document containing plant metadata, the legal verdict, "
        "the quantitative mass-balance table, multi-source evidence breakdown, and an official lead verifier SHA256 sign-off block—ready to attach "
        "to official customs records or audit working papers.",
        body_style
    ))

    doc.build(story, canvasmaker=GuideCanvas)
    print(f"Guide PDF generated at: {pdf_path}")


if __name__ == "__main__":
    out = Path(r"c:\Users\crist\Projects\UEprojects\Capstone\submissions\06_Quick_User_Guide.pdf")
    build_guide_pdf(out)
