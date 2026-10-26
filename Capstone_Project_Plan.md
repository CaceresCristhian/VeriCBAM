# VeriCBAM: Capstone Project Work Plan, Risk Matrix & Execution Roadmap
## A Data-Driven Decision-Support Tool for Screening Carbon Border (CBAM) Emissions Reports

* **Student Name:** Cristhian David Cáceres Mateus (Matriculation No: 93515346)
* **Degree Program:** Master of Science in Data Science (M.Sc. DSc)
* **Academic Institution:** University of Europe for Applied Sciences (UE Germany), Potsdam Campus
* **Faculty Supervisor:** Dr. Humera Noor | **Semester:** Winter 2026/2027 (October 2026 – January 2027)

---

### 1. Project Execution Schedule & Academic Milestones (Winter 2026/2027)

| Phase / Sprint | Timeline | Key Activities & Tasks | Primary Deliverable / Milestone |
| :--- | :---: | :--- | :--- |
| **Milestone 1 & Sprint 0** | Oct 03 – Oct 14, 2026 | Define project scope; collect and clean historical emissions data for 30 European cement and steel plants (177 annual records) and plant capacity data. | **M1: Topic Approval (Oct 12, 2026)** & Cleaned Facility Dataset |
| **Milestone 2 & Sprint 1** | Oct 15 – Nov 09, 2026 | Finalize 1-page proposal; implement Check 1 (Physical Minimums) and Check 2 (Production Technology) for cement and steel plants. | **M2: Proposal Approval (Oct 26, 2026)** & **Progress Report 1 (Nov 09)** |
| **Sprint 2** | Nov 10 – Nov 23, 2026 | Implement Check 3 (Historical Trends), Check 4 ($\text{NO}_x$ vs. $\text{CO}_2$ Pollutant Ratios), and Check 5 (Copernicus Sentinel-5P Satellite $\text{NO}_2$ extraction). | **M4: Progress Report 2 (Nov 23, 2026)** & 5-Check Data Pipeline |
| **Sprint 3** | Nov 24 – Dec 07, 2026 | Build the Bayesian Risk Fusion model and 5-fold Cross-Validated Logistic Regression model; run evaluation across the 325-case benchmark. | **M5: Progress Report 3 (Dec 07, 2026)** & Model Comparison Results |
| **Sprint 4** | Dec 08 – Dec 21, 2026 | Build the interactive Streamlit Web Dashboard, visual map inspector, 1-click Audit Dossier generator, and automated unit tests (`pytest`). | **M6: Progress Report 4 (Dec 21, 2026)** & Live Web Dashboard |
| **Sprint 5 & Defense** | Dec 22 – Jan 18, 2027 | Write and proofread the final Master Thesis manuscript, verify code reproducibility, and prepare the final defense presentation. | **M7: Final Submission (Jan 04, 2027)** & **M8: Defense (Jan 18, 2027)** |

---

### 2. Project Risk Management Matrix

| Identified Risk | Severity | Likelihood | Impact on Project | Mitigation Strategy |
| :--- | :---: | :---: | :--- | :--- |
| **Cloud Cover Blocking Satellite Data** | High | High | Missing satellite observations over northern Europe during winter. | Weight satellite evidence by cloud-free visibility; if data is too cloudy, automatically reduce its weight or output *"Insufficient Evidence"*. |
| **Shared Factory Energy / Off-Site Gases** | High | Medium | Some steel plants send furnace gas to nearby power plants, making their own stack emissions look artificially low. | Flag factories with off-site gas transfers in the plant registry so they are not falsely accused by the physical minimum check. |
| **Missing Data in Public Registries** | Medium | Medium | A few factories have missing reporting years in public databases. | Do not invent or guess missing years; leave them blank (`NaN`) and rely on the remaining available checks. |
| **Data Leakage in Machine Learning** | Critical | Low | Testing a model on the same factory it was trained on would give unrealistic accuracy. | Use **Grouped 5-Fold Cross-Validation** (`GroupKFold` by facility), ensuring all years of a factory are kept strictly in either training or testing. |
| **Lack of Public Fraud Examples** | High | Medium | Real fraudulent CBAM reports are legally confidential and not publicly available. | Create a transparent **325-case test benchmark** by combining 177 real compliant reports with controlled under-reporting scenarios ($5\%$ to $50\%$). |

---

### 3. Expected Deliverables & Resources Required
* **Core Deliverables:**
  1. **Python Data & Modeling Package (`src/`):** Clean, documented code implementing the five evidence checks, Bayesian risk fusion, and cross-validated logistic regression.
  2. **Interactive Streamlit Web Application (`src/ui/app.py`):** A visual dashboard allowing users to explore the 30 facilities on a map, test "what-if" reporting scenarios, view the risk breakdown, and export a 1-page Audit Dossier.
  3. **Automated Test & Reproduction Suite (`tests/`, `scripts/`):** Unit tests verifying code reliability and a single script to reproduce all thesis tables and charts.
* **Resources & Supervision:** Runs on a standard laptop using open-source Python libraries (`pandas`, `scikit-learn`, `streamlit`, `plotly`, `pytest`) and free public datasets (EEA E-PRTR, Global Energy Monitor, Copernicus Sentinel-5P), reviewed bi-weekly with **Dr. Humera Noor**.

---

### 4. Future Extension Roadmap (Stage 2 Horizon)
Once the Stage 1 system is complete, the framework can be extended with higher-resolution satellite data to estimate factory activity directly from space:
1. **Thermal Infrared Satellite Data (Landsat / NASA VIIRS):** Detecting heat directly from cement kilns and steel blast furnaces to verify how many months per year a plant was actively running.
2. **High-Resolution Optical Imagery (PlanetScope):** Observing factory rail yards and raw material stockpiles to confirm physical production activity independently of self-reported numbers.
