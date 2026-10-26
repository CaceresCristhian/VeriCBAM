# Capstone Project Proposal: VeriCBAM
## A Data-Driven Decision-Support Tool for Screening Carbon Border (CBAM) Emissions Reports

* **Student Name:** Cristhian David Cáceres Mateus (Matriculation No: 93515346)
* **Degree Program:** Master of Science in Data Science (M.Sc. DSc)
* **Institution:** University of Europe for Applied Sciences (UE Germany), Potsdam Campus
* **Faculty Supervisor:** Dr. Humera Noor | **Submission Date:** October 2026 (Winter Semester 2026/2027)

---

### 1. Background & Problem Statement
Under the European Union's **Carbon Border Adjustment Mechanism (CBAM)**, companies importing carbon-intensive goods such as **Cement** and **Iron & Steel** into the EU must report the greenhouse gas ($\text{CO}_2$) emissions generated during production and pay a corresponding carbon fee.

* **The Real-World Problem:** To prevent companies from under-reporting their emissions to save money, reports must be verified by independent auditors. However, sending human inspectors to physically audit thousands of overseas factories is slow, expensive, and logistically difficult.
* **The Data Science Opportunity:** Before sending an inspector on an expensive site visit, regulators and auditors need a **pre-screening tool** that automatically cross-checks a factory's self-reported $\text{CO}_2$ number against independent public data to flag suspicious or unrealistic declarations.

### 2. Research Question & Project Objectives
> **Core Research Question:** *How can we combine basic industrial physics, historical emissions records, air pollutant ratios, and satellite observations into an explainable Data Science model that reliably flags inconsistent $\text{CO}_2$ declarations while minimizing false alarms?*

* **Objective 1 (Multi-Source Data Integration):** Collect and align real-world factory emissions, production capacities, and satellite air-quality data for 30 major cement and steel plants.
* **Objective 2 (Multi-Stream Anomaly Detection):** Build five complementary checks that test a factory's declared emissions from different angles (physical minimums, technology type, historical trends, co-pollutants, and satellite plumes).
* **Objective 3 (Explainable Risk Scoring):** Combine these five checks into an interpretable risk score that tells a human auditor **why** a report looks suspicious—or explicitly states **"Insufficient Evidence"** when data is missing or cloudy.

### 3. Proposed Methodology: How VeriCBAM Works
Instead of acting as a "black box," **VeriCBAM** evaluates each emissions report using **five intuitive evidence checks**:

1. **Physical Minimum Check:** Producing 1 tonne of cement or steel requires a known minimum amount of raw material and fuel. If a factory declares less $\text{CO}_2$ than is physically possible for its size and technology, it is flagged immediately.
2. **Production Technology Check:** Cross-checks the factory against global industry registries to ensure a high-emission coal blast furnace is not falsely claiming to be a low-emission scrap recycling plant.
3. **Historical Trend Check:** Compares the factory's newly declared $\text{CO}_2$ against its own past multi-year average to detect sudden, unexplained drops in reported emissions.
4. **Co-Pollutant Cross-Check ($\text{NO}_x$ vs. $\text{CO}_2$):** High-temperature furnaces produce nitrogen oxides ($\text{NO}_x$) alongside $\text{CO}_2$. If a factory claims its $\text{CO}_2$ dropped sharply while its $\text{NO}_x$ pollution stayed high, it indicates potential under-reporting.
5. **Satellite Activity Check (Copernicus Sentinel-5P):** Uses free European Space Agency satellite data to check whether an active nitrogen dioxide ($\text{NO}_2$) plume is visible over the plant during the reporting year.

* **Combining the Evidence (Data Science Models):**
  * **Explainable Bayesian Fusion Model:** Combines the five checks into a transparent probability score ($0\%\text{ to }100\%$ risk) and weights each source by its data reliability (for example, reducing the weight of satellite data when clouds block the view).
  * **Supervised Logistic Regression Model:** Trained with 5-fold cross-validation (grouped by facility so the model is always tested on unseen factories) to rank declarations from highest to lowest audit priority.

### 4. Datasets & Evaluation Plan
* **Public Datasets Used:**
  1. **European Environment Agency (E-PRTR Registry):** 177 real annual emissions records (2018–2023) across **30 European cement and steel facilities** (15 Cement, 15 Steel across 10 countries).
  2. **Global Energy Monitor (GEM):** Independent database of factory production capacities and furnace technologies.
  3. **Copernicus Data Space (Sentinel-5P):** Satellite atmospheric $\text{NO}_2$ measurements over each facility.
* **Validation Benchmark (325 Test Cases):** Because real fraudulent reports are confidential, the models will be tested on a benchmark of **325 scenarios** combining the 177 real compliant factory-years with 148 simulated under-reporting cases (ranging from subtle $5\%\text{--}10\%$ reductions to severe $30\%\text{--}50\%$ understatements and technology misclassifications). Models will be compared using **ROC-AUC**, **Precision-Recall**, **False Positive Rate**, and **Ablation Studies** (testing whether combining all five sources beats using any single source alone).

### 5. Expected Deliverables
1. **Modular Python Pipeline (`src/`):** Clean, reproducible Python code for data ingestion, feature extraction, and risk modeling.
2. **Interactive Streamlit Web Dashboard:** A user-friendly visual application where an auditor can select any facility on a map, inspect the five evidence checks side-by-side, see the step-by-step risk breakdown, and export a 1-page **Audit Dossier**.
3. **Final Master Thesis & Evaluation Report:** Complete academic analysis comparing single-source vs. multi-source screening performance.
