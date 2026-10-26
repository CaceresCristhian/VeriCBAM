# VeriCBAM: Capstone Project Work Plan, Risk Matrix & Execution Roadmap
## Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment

* **Student Name:** Cristhian David Cáceres Mateus (Matriculation No: 93515346)
* **Degree Program:** Master of Science in Data Science (M.Sc. DSc)
* **Academic Institution:** University of Europe for Applied Sciences (UE Germany), Potsdam Campus
* **Faculty Supervisor:** Dr. Humera Noor | **Semester:** Winter 2026/2027 (October 2026 – January 2027)

---

### 1. Project Execution Schedule & Academic Milestones (Winter 2026/2027)

| Phase / Sprint | Timeline | Key Technical & Academic Activities | Primary Deliverable / Milestone |
| :--- | :---: | :--- | :--- |
| **Milestone 1 & Sprint 0** | Oct 03 – Oct 14, 2026 | Topic alignment, EEA E-PRTR v16 cohort extraction (30 facilities, 177 plant-years), GEM capacity & boundary registry curation. | **M1: Topic Approval (Oct 12, 2026)** & Cleaned Layer A Registry |
| **Milestone 2 & Sprint 1** | Oct 15 – Nov 09, 2026 | Proposal formalization; chemical stoichiometry engines (`cement_models.py`, `steel_models.py`), boundary gas-export rules, XML/XLSX declaration parser. | **M2: Proposal Approval (Oct 26, 2026)** & **Progress Report 1 (Nov 09)** |
| **Sprint 2** | Nov 10 – Nov 23, 2026 | Copernicus Sentinel-5P TROPOMI Level-2 $\text{NO}_2$ extraction (`copernicus_client.py`), cloud-fraction gating, leave-one-year-out $\text{NO}_x/\text{CO}_2$ ratio & pooled-MAD baselines. | **M4: Progress Report 2 (Nov 23, 2026)** & 5-Stream Feature Pipeline |
| **Sprint 3** | Nov 24 – Dec 07, 2026 | Weighted Bayesian log-odds fusion (**Model E1**), confidence gating ($C_{\text{overall}} < 0.50$), 5-fold `GroupKFold` logistic triage (**Model E2**), 325-case graded benchmark & bootstrap CIs. | **M5: Progress Report 3 (Dec 07, 2026)** & Empirical Ablation Suite |
| **Sprint 4** | Dec 08 – Dec 21, 2026 | 8-tab Streamlit Decision Cockpit (`src/ui/app.py`), standalone zero-history supplier pre-check, 1-click audit dossier exporter, `pytest` verification suite. | **M6: Progress Report 4 (Dec 21, 2026)** & Live Cloud Cockpit |
| **Sprint 5 & Defense** | Dec 22 – Jan 18, 2027 | Master thesis manuscript finalization, end-to-end reproducibility verification (`reproduce_all.py`), and oral examination slides. | **M7: Final Submission (Jan 04, 2027)** & **M8: Defense (Jan 18, 2027)** |

---

### 2. Technical Risk Management Matrix

| Identified Risk | Severity | Likelihood | Impact on Project | Proactive Mitigation Strategy |
| :--- | :---: | :---: | :--- | :--- |
| **Persistent Cloud Obscuration in Sentinel-5P** | High | High | Overpass data gaps over North/Central Europe during winter months. | Use `qa_value >= 0.50` with explicit cloud fraction confidence weighting ($C_{\text{sat}} = 1 - f_{\text{cloud}}$) and an `Insufficient Evidence` abstention gate ($C_{\text{overall}} < 0.50$). |
| **Transferred Process Gases in Steelworks** | High | High | False physical violation flags on BF-BOF plants exporting blast furnace gas (BFG) to off-site power plants. | Map legal operating boundaries from national IED permits; set `stoich_applicable = False` ($\hat{p}=\text{NaN}$) and evaluate via co-pollutant and historical streams. |
| **Biomass Emission Reporting Missingness** | Medium | High | Inability to isolate biogenic $\text{CO}_2$ in public registry records. | Standardize on total direct $\text{CO}_2$ as the primary regulatory proxy across the 2018–2023 historical panel series. |
| **Facility Data Leakage in ML Models** | Critical | Low | Artificially inflated cross-validation benchmark metrics. | Enforce strict 5-fold `GroupKFold` grouped by `facility_id`, isolating all multi-year records of any given plant between training and test folds. |
| **Construct Validity & Proxy Mismatch** | High | Medium | Facility annual mass ($t\text{CO}_2$) does not directly equal product specific intensity ($t\text{CO}_2e/t$). | Explicitly document proxy boundaries; build a standalone supplier pre-screening module that accepts declared physical production volume ($Q$). |
| **Synthetic Benchmark Circularity** | Medium | Medium | Rule-based perturbations may not capture all real-world evasion patterns. | Evaluate across five graded understatement magnitudes ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$) plus cross-route misclassifications, reporting Recall at fixed FPR budgets ($5\%, 10\%$). |

---

### 3. Threats to Validity & Methodological Boundaries
1. **Construct Validity (Facility Mass vs. Product Intensity):** E-PRTR reports annual absolute facility emissions ($t\text{CO}_2$), whereas CBAM regulates specific embedded emissions per tonne of product ($t\text{CO}_2e/t$). Without declared production output $Q$, a longitudinal mass drop cannot distinguish between an emissions understatement and a genuine economic reduction in factory utilization.
2. **Confidentiality of Third-Country CBAM Declarations:** Because real non-EU transitional CBAM declarations are protected as confidential business information by the European Commission, empirical testing relies on an authentic European industrial reference cohort combined with controlled graded perturbations.
3. **Cohort Depth vs. Breadth:** The reference panel focuses on 30 major European installations (15 Cement, 15 Steel) across 10 EU Member States, prioritizing verified process-route and capacity metadata depth over unverified bulk scraping.

---

### 4. Core Software Deliverables & Resource Management Plan
* **Software & Academic Deliverables:**
  1. **VeriCBAM Core Engine (`src/`):** Modular Python package implementing thermodynamic mass-balance bounds (`cement_models.py`, `steel_models.py`), leave-one-year-out co-pollutant baselines (`nox_baseline.py`), Copernicus Sentinel-5P extraction (`copernicus_client.py`), and Bayesian log-odds fusion (`evidence_fusion.py`).
  2. **8-Tab Interactive Streamlit Decision Cockpit (`src/ui/app.py`):** Covering (1) System Overview & Architecture, (2) Facility Cohort & Geospatial Inspector, (3) Stoichiometric Feasibility Sandbox, (4) Standalone Supplier Plausibility Pre-Check, (5) Satellite Inspector, (6) Bayesian Evidence Fusion & Audit Dossier, (7) Empirical Benchmark Evaluation & Ablation, and (8) Capstone Proposal, References & Roadmap.
  3. **Reproducibility & Verification Suite:** Single-command reproduction script (`scripts/reproduce_all.py`) and automated `pytest` unit/integration suite (`tests/`).
* **Resource & Governance Plan:** Executed on a standard Python 3.12 64-bit workstation without specialized GPU requirements, utilizing public EEA E-PRTR v16 data, Copernicus Data Space Ecosystem (CDSE) APIs, and Global Energy Monitor (GEM) trackers under bi-weekly supervision sprints with Dr. Humera Noor.

---

### 5. Technical Extension Roadmap: Multi-Sensor Earth Observation (Stage 2 Horizon)
To overcome coarse trace-gas resolution ($5.5 \times 3.5\text{ km}$) and eliminate reliance on self-reported production volume ($Q$) for third-country suppliers lacking historical baselines, the project roadmap defines a **Stage 2 Multi-Sensor EO extension**:
1. **Thermal Infrared (TIR) Operating Timelines (USGS Landsat-8/9 TIRS 30 m & NASA FIRMS VIIRS 375 m):** Detects persistent radiative heat anomalies over cement rotary kilns ($1,400^\circ\text{C}$ core / $200\text{--}350^\circ\text{C}$ shell) and steel blast furnaces ($1,500^\circ\text{C}$ hot metal), reconstructing an independent monthly operating calendar.
2. **High-Resolution Optical Freight & Stockpile Logistics (PlanetScope / VHR Optical):** Quantifies rail-yard freight activity and raw-material yard contrast to independently verify physical plant throughput ($\hat{Q}$).
3. **All-Weather Synthetic Aperture Radar (Copernicus Sentinel-1 C-Band SAR):** Penetrates winter cloud cover via dual-polarization metallic double-bounce backscatter over storage yards and gantry cranes.
