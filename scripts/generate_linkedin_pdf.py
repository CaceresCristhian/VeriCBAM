"""
Generates 06_LinkedIn_Announcement_Post.pdf using ReportLab.
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


class LinkedInCanvas(canvas.Canvas):
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
        self.line(15 * mm, 12 * mm, 195 * mm, 12 * mm)
        self.drawString(
            15 * mm, 8.5 * mm,
            "VeriCBAM Capstone Project Announcement | Cristhian David Cáceres Mateus (93515346) | UE Germany (Potsdam)"
        )
        self.drawRightString(195 * mm, 8.5 * mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf(pdf_path: Path):
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("L_Title", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=14, leading=17, textColor=colors.HexColor("#1A365D"), spaceAfter=2)
    subtitle_style = ParagraphStyle("L_Sub", parent=styles["Normal"], fontName=BOLD_FONT, fontSize=9.5, leading=12.5, textColor=colors.HexColor("#0A66C2"), spaceAfter=5)
    body_style = ParagraphStyle("L_Body", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=8.5, leading=11.5, textColor=colors.HexColor("#2D3748"), alignment=TA_JUSTIFY, spaceAfter=4)
    bullet_style = ParagraphStyle("L_Bullet", parent=styles["Normal"], fontName=MAIN_FONT, fontSize=8.2, leading=11.2, textColor=colors.HexColor("#2D3748"), leftIndent=12, firstLineIndent=-8, spaceAfter=3)
    meta_k = ParagraphStyle("L_MK", fontName=BOLD_FONT, fontSize=7.8, leading=10, textColor=colors.HexColor("#0A66C2"))
    meta_v = ParagraphStyle("L_MV", fontName=MAIN_FONT, fontSize=7.8, leading=10, textColor=colors.HexColor("#2D3748"))

    story = []
    story.append(Paragraph("VeriCBAM: Master Capstone Project Announcement", title_style))
    story.append(Paragraph("Public LinkedIn Dissemination & Project Milestone Overview", subtitle_style))

    meta_data = [
        [Paragraph("Author:", meta_k), Paragraph("Cristhian David Cáceres Mateus (ID: 93515346)", meta_v),
         Paragraph("Institution:", meta_k), Paragraph("University of Europe for Applied Sciences (Potsdam)", meta_v)],
        [Paragraph("Degree Program:", meta_k), Paragraph("Master of Science in Data Science (M.Sc. DSc)", meta_v),
         Paragraph("Faculty Supervisor:", meta_k), Paragraph("Dr. Humera Noor | Winter Semester 2026/2027", meta_v)],
        [Paragraph("Live Cloud App:", meta_k), Paragraph("<font color='#0A66C2'><u>https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/</u></font>", meta_v),
         Paragraph("Source Code:", meta_k), Paragraph("<font color='#0A66C2'><u>https://github.com/CaceresCristhian/VeriCBAM</u></font>", meta_v)],
    ]
    meta_tbl = Table(meta_data, colWidths=[24 * mm, 64 * mm, 27 * mm, 63 * mm])
    meta_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 4))

    card_header = """
    <b>LinkedIn Post Content (Approved Capstone Communication Milestone):</b>
    """
    story.append(Paragraph(card_header, ParagraphStyle("Hdr", fontName=BOLD_FONT, fontSize=9, leading=12, textColor=colors.HexColor("#1A365D"), spaceAfter=3)))

    post_intro = (
        "Excited to share my Master’s Capstone project at the University of Europe for Applied Sciences (Potsdam Campus): "
        "<b>VeriCBAM — A Data-Driven Decision Support System for Carbon Border Adjustment Mechanism (CBAM) Consistency Screening</b>.<br/><br/>"
        "Starting in 2026, European industrial importers must verify self-reported greenhouse gas emissions for goods like "
        "<b>Cement</b> and <b>Iron & Steel</b> imported into the EU under Regulation (EU) 2023/956. However, commissioning physical on-site audits "
        "for thousands of overseas industrial installations poses severe logistical bottlenecks.<br/><br/>"
        "To address this challenge, <b>VeriCBAM</b> acts as an explainable screening copilot that cross-checks self-reported emissions declarations "
        "against independent multi-source evidence before costly inspections are commissioned:"
    )
    story.append(Paragraph(post_intro, body_style))

    story.append(Paragraph("• <b>First-Principles Chemical Stoichiometry:</b> Enforcing thermodynamic mass-balance lower bounds for cement clinker calcination and steelmaking reduction routes.", bullet_style))
    story.append(Paragraph("• <b>Multi-Sensor Satellite Earth Observation:</b> Integrating 30m USGS Landsat-8/9 thermal infrared (TIRS) core heat signatures, daily 375m NASA VIIRS active operating calendars, and high-resolution optical rail-yard freight activity to verify operational presence from orbit.", bullet_style))
    story.append(Paragraph("• <b>Longitudinal Trajectories & Co-Pollutant Fingerprinting:</b> Evaluating leave-one-year-out historical baselines and NOx/CO2 combustion ratios from public environmental compliance registries (EEA E-PRTR).", bullet_style))
    story.append(Paragraph("• <b>Transparent Evidence Fusion:</b> Synthesizing all streams through a confidence-gated Bayesian log-odds engine (achieving <3.5% false alarms on compliant facilities) and a supervised triage queue delivering a 2.71x audit prioritization lift.", bullet_style))

    post_outro = (
        "The platform includes an interactive, browser-based decision cockpit with a 1-click <b>Official Pre-Audit Screening Dossier (PDF)</b> "
        "generator for customs declarants, accredited verification bodies, and industrial importers.<br/><br/>"
        "Explore the live interactive cloud cockpit: <font color='#0A66C2'><b>https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/</b></font><br/>"
        "Code & Documentation on GitHub: <font color='#0A66C2'><b>https://github.com/CaceresCristhian/VeriCBAM</b></font><br/><br/>"
        "Special thanks to my academic supervisor, <b>Dr. Humera Noor</b>, for her ongoing mentorship and guidance throughout this project!"
    )
    story.append(Paragraph(post_outro, body_style))
    story.append(Spacer(1, 2))

    hashtags = (
        "<font color='#0A66C2'>#DataScience #MachineLearning #RemoteSensing #CBAM #CarbonAccounting #EarthObservation "
        "#Sustainability #EUETS #AIforGood #UniversityOfEurope #PotsdamCampus</font>"
    )
    story.append(Paragraph(hashtags, ParagraphStyle("Hash", fontName=BOLD_FONT, fontSize=7.8, leading=10.5, textColor=colors.HexColor("#0A66C2"))))

    doc.build(story, canvasmaker=LinkedInCanvas)
    print(f"LinkedIn PDF generated successfully at: {pdf_path}")


if __name__ == "__main__":
    out = Path(r"c:\Users\crist\Projects\UEprojects\Capstone\admin\06_LinkedIn_Announcement_Post.pdf")
    build_pdf(out)
