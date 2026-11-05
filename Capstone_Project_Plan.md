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
| **Sprint 5: Thesis & Defense** | Nov 06 – Jan 18 | Master thesis drafting (Chapters 1–6), code reproducibility audit, external verifier outreach, and final oral defense presentation. | **PR1 (Nov 09) / Final Sub (Jan 04)**<br/>`[ACTIVE]` |

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
2. **Interactive Cloud Decision Cockpit:** Live at https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/ featuring the new **Tab 1 Quick Audit & 1-Click PDF Dossier Generator**.
3. **Stage 2 Multi-Sensor Satellite Dataset:** Cached 30-facility dataset combining USGS Landsat-8/9 30m TIR $\Delta T$, NASA FIRMS VIIRS 375m operating calendars, and Planet VHR freight contrast.
4. **Master Thesis Manuscript:** Drafting in progress following academic structure under bi-weekly supervision of **Dr. Humera Noor**.

---

### 4. Remaining Roadmap Towards Master Thesis Submission (Winter 2026/2027)
* **Nov 09, 2026:** Progress Report 1 Submission (Demonstrating completed Stage 1 & Stage 2 empirical evaluation).
* **Nov 23, 2026:** Progress Report 2 Submission (Draft Thesis Methodology & Empirical Results chapters).
* **Dec 07 – Dec 21, 2026:** Progress Reports 3 & 4 (Complete manuscript review, conclusion, and policy recommendations).
* **Jan 04, 2027:** Final Master Thesis Submission (Binding university submission).
* **Jan 18, 2027:** Master Thesis Oral Defense & Examination.
