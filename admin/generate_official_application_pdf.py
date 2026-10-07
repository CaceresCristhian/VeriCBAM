"""
Generate the officially filled and visually rendered VeriCBAM Capstone Application Form PDF
using PyMuPDF to guarantee appearance stream generation and persistent visual field rendering.
"""

from pathlib import Path
import pymupdf

HERE = Path(__file__).parent
input_pdf_path = HERE / "Capstone_Application_Form.pdf"
output_pdf_path = HERE / "VeriCBAM_Capstone_Application_Form_Filled_v2.pdf"

doc = pymupdf.open(input_pdf_path)
page = doc[0]

description_text = (
    "In 2026, the EU Carbon Border Adjustment Mechanism (CBAM, Regulation (EU) 2023/956) entered its definitive "
    "financial enforcement phase, obliging European importers of carbon-intensive commodities (cement, iron and steel) "
    "to declare embedded direct emissions from non-EU installations under Commission Implementing Regulation (EU) 2025/2547, "
    "subject to third-party verification under Implementing Regulations (EU) 2025/2546 and 2025/2551. Importers and authorities "
    "face an acute screening bottleneck: supplier declarations require substantial audit scrutiny, while mandatory on-site physical "
    "audits are economically and logistically constrained (~4,100 declarants and tens of thousands of suppliers competing for ~403 "
    "accredited verification bodies globally).\n\n"
    "This project develops VeriCBAM, an explainable multimodal decision-support system that screens and assesses the consistency "
    "of CBAM declarations against independent physical, observational, and historical evidence. VeriCBAM integrates three empirical "
    "pillars: (1) a first-principles stoichiometric and engineering engine establishing process-specific lower bounds for cement clinker "
    "calcination and metallurgical steelmaking (BF-BOF vs. Scrap-EAF); (2) a Copernicus Earth Observation pipeline extracting real Sentinel-5P "
    "TROPOMI Level-2 tropospheric NO2 column enhancements as an operational activity indicator (with CO and Sentinel-2 SWIR planned as extensions); "
    "and (3) longitudinal historical facility fingerprints derived from independent emissions registries (EEA E-PRTR).\n\n"
    "The core decision layer features an expert-parameterized probabilistic evidence-fusion engine that quantifies material inconsistency risk "
    "alongside separate observational confidence scores, 95% sensitivity intervals, and an explicit 'Insufficient Evidence' state. The system is "
    "evaluated via a 5-model ablation study and facility-grouped cross-validation across a 30-facility European industrial cohort (177 historical observations) "
    "and a 101-case controlled perturbation benchmark, delivered via an interactive Streamlit decision-support cockpit."
)

field_data = {
    "Last Name": "Caceres Mateus",
    "First Name": "Cristhian David",
    "Matriculation No": "93515346",
    "Study Program": "M.Sc. Data Science",
    "Title of Project": "VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment",
    "Description": description_text,
    "Place Date": "Berlin, 12.10.2026",
    "aware": True,
}

for widget in page.widgets():
    name = widget.field_name
    if name in field_data:
        val = field_data[name]
        if widget.field_type_string == "CheckBox":
            widget.field_value = "Yes" if val else "Off"
        else:
            widget.field_value = str(val)
            if name == "Description":
                widget.text_fontsize = 6.2  # Ensure full multi-paragraph text fits neatly
            elif name == "Title of Project":
                widget.text_fontsize = 8.5
            else:
                widget.text_fontsize = 10.0
        widget.update()

# Save with garbage collection and deflation
doc.save(output_pdf_path, garbage=3, deflate=True)
doc.close()
print(f"Successfully generated officially filled PDF: {output_pdf_path}")

# Verify by reopening and extracting text
verify_doc = pymupdf.open(output_pdf_path)
v_page = verify_doc[0]
print("\nVerifying filled fields in generated PDF:")
for w in v_page.widgets():
    if w.field_name in field_data:
        val_display = (w.field_value[:40] + "...") if len(str(w.field_value)) > 40 else w.field_value
        print(f"  [{w.field_name}]: {val_display}")
verify_doc.close()
