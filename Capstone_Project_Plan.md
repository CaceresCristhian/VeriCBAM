# VeriCBAM: Capstone Project Work Plan, Status & Execution Roadmap
## A Data-Driven Decision-Support Tool for Screening Carbon Border (CBAM) Emissions Reports

* **Student Name:** Cristhian David Cáceres Mateus (Matriculation No: 93515346)
* **Degree Program:** Master of Science in Data Science (M.Sc. DSc)
* **Academic Institution:** University of Europe for Applied Sciences (UE Germany), Potsdam Campus
* **Faculty Supervisor:** Dr. Humera Noor | **Semester:** Winter 2026/2027 (October 2026 – January 2027)

---

### 1. Updated Execution Schedule & Milestone Status (Status: November 2026)

| Sprint / Phase | Planned Dates | Key Completed Technical Tasks | Deliverable & Current Status |
| :--- | :---: | :--- | :--- |
| **Sprint 0: Cohort & Ingestion** | Oct 03 – Oct 14 | Scoped project; ingested and cleaned 177 plant-years across 30 EU cement/steel facilities from EEA E-PRTR v16 and GEM trackers. | **M1: Topic Approval (Oct 12)**<br/>`[COMPLETED]` |
| **Sprint 1: Stoichiometry & Planning** | Oct 15 – Oct 26 | Implemented calcination and steel reduction mass-balance floors (`cement_models.py`, `steel_models.py`); boundary gas-export rules. | **M2: Proposal Approved (Oct 30)**<br/>`[COMPLETED]` |
| **Sprint 2: Satellite & Baselines** | Oct 27 – Nov 04 | Ingested Sentinel-5P TROPOMI NO₂; built leave-one-year-out NOx/CO₂ ratios and one-sided robust pooled-MAD longitudinal drift scores. | **5-Stream Data Pipeline**<br/>`[COMPLETED]` |
| **Sprint 3: Modeling & Evaluation** | Oct 28 – Nov 05 | Built Bayesian Log-Odds Fusion (Model E1) & GroupKFold Logistic Triage (Model E3); evaluated 325-case graded benchmark with 1,000 bootstrap CIs. | **325-Case Benchmark**<br/>`[COMPLETED]` |
| **Sprint 4: Multi-Sensor & Dashboard** | Nov 01 – Nov 05 | Built live 8-tab Streamlit Cockpit with Tab 1 Quick Audit & PDF Dossier; integrated Stage 2 Multi-Sensor EO (Landsat 30m TIR, VIIRS 375m, Planet VHR). | **Live App & Quick Audit**<br/>`[COMPLETED]` |
| **Sprint 5: Industry Outreach & Deliverables** | Nov 06 – Jan 18 | Real-world industry pilots (DNV, TÜV, DEHSt, importers), bi-weekly progress updates, presentation deck, walkthrough & pitch videos, and LinkedIn post. | **Bi-Weekly Updates / Jan 04 Final**<br/>`[ACTIVE]` |

---

### 2. Project Risk Management & Resolution Matrix

| Identified Technical Risk | Severity | Likelihood | Impact on Project | Implemented Mitigation & Current Resolution |
| :--- | :---: | :---: | :--- | :--- |
| **Cloud Cover in Sentinel-5P Satellite** | High | High | Trace-gas data gaps during northern European winter. | **Resolved:** Weighted satellite evidence by cloud fraction ($C_{\text{sat}} = 1 - f_{\text{cloud}}$) and integrated cloud-resilient thermal infrared (Landsat/VIIRS). |
| **Off-Site Process Gases in Steelworks** | High | Medium | False physical violations on blast furnace plants exporting gas to power plants. | **Resolved:** Mapped plant boundaries in GEM registry; set `stoich_applicable = False` for gas-exporting plants to eliminate false alarms. |
| **Data Leakage in Machine Learning** | Critical | Low | Artificially inflated accuracy from training and testing on the same plant. | **Resolved:** Enforced strict 5-Fold `GroupKFold(groups=facility_id)`, ensuring all years of any plant are strictly isolated between folds. |
| **Confidentiality of Overseas Fraud** | High | Medium | Real non-EU fraudulent CBAM reports are legally confidential. | **Resolved:** Built a 325-case controlled benchmark combining 177 real compliant years with 148 graded synthetic understatements ($5\%\text{--}50\%$). |

---

### 3. Core Deliverables & Current Completion Status
1. **VeriCBAM Python Engine (`src/`):** 100% complete and passing 30/30 unit tests (`pytest`).
2. **Interactive Cloud Decision Cockpit:** Live at https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/ featuring the new **Tab 1 Quick Audit & 1-Click PDF Dossier Generator** for zero-friction industrial demonstrations.
3. **Stage 2 Multi-Sensor Satellite Dataset:** Cached 30-facility dataset combining USGS Landsat-8/9 30m TIR $\Delta T$, NASA FIRMS VIIRS 375m daily operating calendars, and Planet VHR freight contrast.
4. **Industry & Authority Outreach Suite:** Standalone 1-page Quick User Guide (`06_Quick_User_Guide.pdf`) and standardized demonstration protocol for verification bodies (DNV, TÜV, Bureau Veritas) and customs authorities (DEHSt).

---

### 4. Bi-Weekly Progress Roadmap & Final Deliverables Schedule (Winter 2026/2027)
* **Bi-Weekly Progress Cadence:** Progress updates submitted to Dr. Humera Noor every two weeks: **Nov 09** (Update 1: Live Tab 1 Quick Audit & Stage 2 Multi-Sensor benchmark), **Nov 23** (Update 2: Industry pilot feedback & automated PDF dossier validation), **Dec 07** (Update 3: Multi-sector sensitivity & deck structure), and **Dec 21** (Update 4: Video walkthrough production & LinkedIn draft).
* **Final Deliverables Package (Jan 04, 2027):**
  1. **Presentation Deck:** Executive slide deck presenting operational ROI and physics-grounded AI methodology.
  2. **Long-Form Video (15–20 min):** Technical walkthrough of the multimodal data pipeline and live interactive audit.
  3. **Elevator Pitch Video (1–2 min):** Concise executive video demonstrating rapid declaration screening for CBAM importers.
  4. **LinkedIn Post:** Public industry release driving adoption among EU climate verifiers and customs authorities.
  5. **Open-Source Codebase & Live App:** Reproducible GitHub repository and live Streamlit cloud decision cockpit.
