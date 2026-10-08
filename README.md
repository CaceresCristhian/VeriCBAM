# VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 19/19 Passed](https://img.shields.io/badge/tests-19%2F19%20passed-brightgreen.svg)](tests/)
[![Real Copernicus EO](https://img.shields.io/badge/Copernicus-Sentinel--5P%20TROPOMI-orange.svg)](https://sentinel.esa.int/web/sentinel/missions/sentinel-5p)
[![GitHub Repository](https://img.shields.io/badge/GitHub-VeriCBAM-blue?logo=github)](https://github.com/CaceresCristhian/VeriCBAM)

**Master's Capstone Project**  
*M.Sc. Data Science | University of Europe for Applied Sciences (UE Germany)*  
*Candidate:* Cristhian David Cáceres Mateus (Matriculation No. 93515346)  
*Supervisor:* Dr. Humera Noor  
*Repository:* [https://github.com/CaceresCristhian/VeriCBAM](https://github.com/CaceresCristhian/VeriCBAM)  

---

## 1. Executive Summary & Research Question

Under **Regulation (EU) 2023/956**, **Implementing Regulation (EU) 2025/2546** (verification rules), **Implementing Regulation (EU) 2025/2551** (verifier accreditation), and **Implementing Regulation (EU) 2025/2547** (calculation of embedded emissions), EU importers of carbon-intensive commodities (**Cement and Steel**) declaring actual embedded Scope 1 emissions face an acute verification bottleneck:
- Complex facility audits cost **€50,000 to €150,000+** per integrated site when factoring in international auditor travel to third countries (India, China, Turkey, Brazil).
- Only **~403 verification bodies globally** hold accreditation under the EU Accreditation and Verification Regulation (**AVR 2018/2067** / **(EU) 2025/2551**) to serve over **~12,000 EU import entities**.
- Audit cycles require **3 to 6 months**, causing administrative backlogs and exposing importers to punitive mark-up penalties (+10% in 2026, +20% in 2027, +30% in 2028).

### Central Research Question
> **To what extent can independent physical, observational, historical, and documentary evidence be fused into an explainable decision-support model that identifies controlled CBAM emissions inconsistencies more reliably than isolated evidence sources?**

**Scientific Position:** VeriCBAM does **not** claim autonomous legal CBAM compliance certification. It provides explainable, probabilistic decision support for human verifiers and customs authorities to prioritize high-risk installations and clear concordant claims.

---

## 2. Four-Level Evidence Hierarchy

```
CBAM Importer Declaration
           ↓
 ┌─────────────────────┬─────────────────────┬─────────────────────┐
 ↓                     ↓                     ↓                     ↓
Level 1: Stoichiometry Level 2: Satellite   Level 3: Historical   Level 4: Registry
Chemical Mass Balance  Copernicus EO Plume   Longitudinal Drift    Nameplate Capacity
Process Lower Bounds   TROPOMI NO₂ Contrast  EEA E-PRTR 6-Yr Trend Verified Routes
 └─────────────────────┴─────────────────────┴─────────────────────┘
                                  ↓
           Probabilistic Evidence-Fusion Risk Engine
               logit P(H|E) = logit P(H) + Σ wᵢ Cᵢ log(LRᵢ)
                                  ↓
           ┌──────────────────────┴──────────────────────┐
           ↓                                             ↓
Inconsistency Risk P(H|E)                     Evidence Confidence C_overall
(Signal Strength)                             (Observational Completeness)
           ↓                                             ↓
                      Four Formal Outcomes:
  [Consistent | Potential Inconsistency | High Risk | Insufficient Evidence]
                                  ↓
                     Human Verifier Cockpit
```

- **Level 1 — Physical Consistency:** First-principles chemical calcination ($\text{CaCO}_3 \xrightarrow{\Delta} \text{CaO} + \text{CO}_2$) and carbothermic iron reduction ($\text{Fe}_2\text{O}_3 + 3\text{C} \rightarrow 2\text{Fe} + 3\text{CO}$) establishing model-based lower bounds under specified engineering assumptions.
- **Level 2 — Operational Consistency:** Real Copernicus Sentinel-5P TROPOMI Level-2 tropospheric $\text{NO}_2$ columns range-read over facility coordinates to infer active combustion plume enhancements ($Z$-scores) versus regional background (Sentinel-5P $\text{CO}$ and Sentinel-2 SWIR B11/B12 designed as planned extensions).
- **Level 3 — Historical Consistency:** Longitudinal multi-year reference trajectories (2018–2023) to detect abrupt, uncharacteristic emissions drops ($>3.5\sigma$).
- **Level 4 — Multimodal Synthesis:** Confidence-weighted log-odds fusion decoupling inconsistency risk from data confidence.

---

## 3. Data Layers (Zero Synthetic Data Fallback)

| Dataset Layer | Records / Scale | Data Provenance | Status |
| :--- | :---: | :--- | :---: |
| **Layer A: Reference Cohort** | 177 facility-years (30 facilities) | European Environment Agency (EEA) Industrial Reporting Database (E-PRTR / IED v16). Accounts for the 3 missing facility-years. | **Authentic Reference** |
| **Multi-Pollutant Panel** | 177 facility-years | Authentic $\text{NO}_x/\text{CO}_2$ and $\text{SO}_x/\text{CO}_2$ combustion co-emission ratios across 30 European installations. | **Multi-Pollutant** |
| **Technology Registry** | 30 facilities | Global Energy Monitor (GEM) Global Steel & Cement Trackers + Corporate Permits. Conservative utilization factors $\eta \in [0.50, 0.95]$. | **Verified Real Data** |
| **Sentinel-5P Earth Observation** | 301 overpasses + 2019–2023 panel | ESA Copernicus Sentinel-5P Level-2 OFFL product via Planetary Computer STAC & CDSE OAuth2. Zero synthetic fallback. | **Real Remote Sensing** |
| **Layer B: Graded Evaluation Benchmark** | **326 cases** | 177 authentic real-year negatives (pooled MAD $\sigma = 0.0911$), 140 graded understatements ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$), and 9 route mismatches. | **Graded Benchmark** |

---

## 4. Probabilistic Evidence-Fusion Formulation

$$\text{logit } P(H \mid E) = \text{logit } P(H) + \sum_{i=1}^M w_i \cdot C_i \cdot \ln(\text{LR}_i)$$

Where:
- $H$: Hypothesis of material declaration inconsistency.
- $P(H)$: Baseline prior probability ($8\%$ historical discrepancy baseline, evaluated via sensitivity analysis across $[2\%, 15\%]$).
- $\text{LR}_i = \frac{P(E_i \mid H)}{P(E_i \mid \neg H)}$: Evidence-specific likelihood ratio.
- $C_i \in [0, 1]$: Observational confidence factor (accounting for cloud fraction, QA flags, and historical data completeness).
- $w_i \in [0, 1]$: Evidential reliability weights ($w_1 = 1.0$ stoichiometry, $w_2 = 0.35$ satellite remote sensing, $w_3 = 0.80$ historical drift, $w_4 = 0.60$ multi-pollutant ratio).
- **Uncertainty Interval:** 95% sensitivity bounds generated via Monte Carlo sampling under likelihood-ratio parameter uncertainty.
- **Formal Insufficient Evidence Gate:** If $C_{\text{overall}} < 0.50$, the system automatically outputs `Insufficient Evidence` to prevent false positive screening under overcast skies.

---

## 5. Repository Structure

```
VeriCBAM/
├── docs/
│   ├── DATA_PROVENANCE.md            # Detailed scientific data lineage & metadata
│   ├── MODEL_CARD.md                 # Formal model card & empirical benchmark specifications
│   ├── STITCH_DESIGN.md              # Google Stitch UI design system tokens & specification
│   └── VeriCBAM_Project_Plan.md      # Sprint execution roadmap & academic plan
├── scripts/
│   ├── reproduce_all.py              # Master deterministic reproduction pipeline
│   └── build_reproducible_zip.py     # Self-contained distribution archiver
├── data/
│   ├── 01_raw/eprtr_reference/       # Official EEA E-PRTR / IED v16 database
│   ├── 02_processed/
│   │   ├── benchmark_cohort.parquet              # 177 authentic facility-year observations
│   │   ├── facility_technology_registry.csv      # Verified plant capacities, routes, and utilization
│   │   ├── facility_nox_co2_ratios.csv           # Multi-pollutant NOx/CO2 combustion ratios
│   │   ├── graded_evaluation_benchmark.parquet   # 326-case graded evaluation benchmark
│   │   └── controlled_perturbation_benchmark.parquet # 101-case ablation suite
│   └── 03_satellite_cache/
│       ├── s5p_no2_annual_stats_2019_2023.csv    # Multi-year Copernicus Sentinel-5P cache
│       └── s5p_no2_overpasses_2023.parquet       # Real Sentinel-5P Level-2 overpasses
├── src/
│   ├── core/
│   │   ├── stoichiometry/            # Cement & Steel chemical mass balance models
│   │   └── bayesian/                 # Weighted log-odds evidence fusion engine
│   ├── satellite/
│   │   ├── copernicus_client.py      # Real Sentinel-5P HDF5 range-read client
│   │   ├── copernicus_multiyear_client.py # Multi-year CDSE OAuth2 client
│   │   └── plume_analyzer.py         # Plume contrast Z-score & operational state analyzer
│   ├── benchmark/
│   │   ├── graded_benchmark_generator.py # 326-case graded benchmark generator
│   │   └── perturbation_generator.py # 101-case perturbation suite generator
│   ├── data_loaders/
│   │   ├── cohort_manager.py         # 30-facility cohort data access
│   │   ├── build_cohort.py           # Multi-pollutant cohort builder
│   │   └── technology_registry.py    # Verified technology metadata builder
│   └── ui/
│       ├── app.py                    # Streamlit decision-support cockpit (with dark Stitch theme)
│       └── stitch_cockpit.html       # Embedded Google Stitch high-fidelity decision cockpit
├── experiments/
│   ├── run_graded_evaluation.py      # Benchmark: Logistic Regression vs Expert Bayesian Fusion
│   ├── run_ablation_study.py         # Automated 5-Model Ablation Benchmark
│   ├── calibrate_probabilities.py    # Platt Scaling & Isotonic Regression (5-fold CV)
│   ├── run_grouped_validation.py     # GroupKFold (facility_id) out-of-facility cross-validation
│   ├── run_lr_sensitivity.py         # Likelihood Ratio & Prior sensitivity analyses
│   └── results/                      # Parquet predictions, CSV summaries, Plotly HTML
├── tests/                            # Pytest test suite (19/19 passing)
├── requirements.txt                  # Python environment dependencies
├── pytest.ini                       # Test configuration
├── .gitignore                       # Repository exclusions
├── admin/                           # Submission paperwork & official forms
│   ├── Capstone_Application_Form.pdf
│   ├── VeriCBAM_Capstone_Application_Form_Filled_v2.pdf
│   └── generate_official_application_pdf.py
└── Capstone_Proposal_Document.md    # Full academic capstone proposal
```

---

## 6. Experimental Benchmarks & Empirical Findings

### 6.1 Advanced Graded Evaluation Benchmark (326 Cases)
Evaluated across 177 authentic real-year negatives (pooled MAD $\sigma = 0.0911$), 140 graded understatements ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$), and 9 route mismatches across 30 European installations:

| Model Architecture | Mechanism | ROC-AUC | PR-AUC | Brier Score | ECE (10 Bins) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Model B** | Stoichiometry Alone | 0.6897 | 0.5248 | 0.2865 | 0.2647 |
| **Model C** | Satellite Alone (Sentinel-5P $\text{NO}_2$) | 0.5221 | 0.3859 | 0.3719 | 0.3461 |
| **Model D** | Historical Baseline Alone | 0.9659 | 0.9479 | 0.2352 | 0.3390 |
| **Model E1** | **VeriCBAM Expert Bayesian Fusion (Zero-Shot)** | **0.7693** | **0.5625** | **0.2716** | **0.1108** |
| **Model E2** | **Learned Logistic Regression (`GroupKFold` Baseline)** | **0.9654** | **0.9502** | **0.0754** | **0.0469** |

*Scientific Negative Result on Satellite Trace-Gas Sensing:* Multi-year Sentinel-5P overpasses (2019–2023) against 177 facility-years proved that satellite $\text{NO}_2$ plume contrast does not track annual facility $\text{CO}_2$ ($\rho = 0.198$, within-plant mean $\rho = -0.100$). This justifies why single-modality remote sensing fails and why multimodal Bayesian fusion is necessary.

### 6.2 5-Model Ablation Study Results (Layer B: 101 Controlled Cases)
Evaluated across 30 Baseline Concordant, 30 Physical Bound Violations, 30 Historical Drop Anomalies, and 11 controlled route-mismatch cases constructed from facilities with independently documented production routes:

| Model ID & Architecture | Precision | Recall | F1-Score | FPR | ROC-AUC | PR-AUC | Brier Score | ECE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model A (Declaration Baseline)** | 0.943 | 0.704 | 0.807 | 0.100 | 0.8671 | 0.9515 | 0.1807 | 0.1864 |
| **Model B (Stoichiometry Alone)** | **1.000** | 0.648 | 0.786 | **0.000** | 0.8692 | 0.9384 | 0.1685 | 0.1467 |
| **Model C (Satellite Alone)** | 0.000 | 0.000 | 0.000 | **0.000** | 0.5174 | 0.7112 | 0.5425 | 0.5751 |
| **Model D (Historical Alone)** | 0.000 | 0.000 | 0.000 | **0.000** | 0.9859 | 0.9916 | 0.3094 | 0.4525 |
| **Model E (VeriCBAM Fused)** | **1.000** | **0.930** | **0.964** | **0.000** | **0.9991** | **0.9996** | **0.0423** | **0.0763** |

### Probability Calibration & Facility-Grouped Generalization
> **Methodological Qualification:** Probability calibration is evaluated against the controlled evaluation benchmark (101 cases). Real-world prevalence calibration remains a stated research limitation due to absent public CBAM violation datasets.

| Calibration Method & Validation Scheme | Brier Score | ECE (10 Bins) | F1-Score | ROC-AUC | PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Raw Bayesian Posterior (Uncalibrated)** | 0.0423 | 0.0763 | 0.9635 | 0.9991 | 0.9996 |
| **Platt Scaling (Stratified 5-Fold CV)** | **0.0195** | 0.0322 | **0.9859** | 0.9972 | — |
| **Isotonic Regression (Stratified 5-Fold CV)** | 0.0297 | **0.0297** | 0.9790 | 0.9596 | — |
| **Platt Scaling (GroupKFold, groups=`facility_id`)** | **0.0168** | 0.0312 | **0.9859** | 0.9977 | 0.9991 |
| **Isotonic Regression (GroupKFold, groups=`facility_id`)** | 0.0186 | **0.0192** | **0.9859** | 0.9927 | 0.9958 |

*Key Result:* Facility-grouped cross-validation confirms that calibration generalizes cleanly to unseen industrial installations without facility data leakage.

---

## 7. Installation & Execution

### 1. Set Up Environment
```powershell
cd <path-to-repo>
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Test Suite
```powershell
pytest -v
```
*Expected: 19/19 tests pass.*

### 3. Run Master Deterministic Reproduction Pipeline
```powershell
python scripts/reproduce_all.py
```
*Executes all 7 data generation, experimental, calibration, and test stages end-to-end.*

### 4. Launch the Streamlit Cockpit
```powershell
python -m streamlit run src/ui/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 8. Compliance with Academic Capstone Guidelines

1. **Independent Reference vs. Controlled Evaluation:** Clear separation between Layer A (authentic historical reference from EEA) and Layer B (controlled evaluation cases). E-PRTR is never termed "ground truth".
2. **Zero Fabricated Satellite Data:** Complete removal of synthetic fallback branches; client extracts authentic Sentinel-5P granules with complete provenance.
3. **Decoupled Risk and Confidence:** Separate gauges for Inconsistency Risk and Evidence Confidence with explicit `Insufficient Evidence` gate.
4. **Prior Sensitivity Analysis:** Automated evaluation across base priors from $2\%$ to $15\%$ demonstrating risk ranking stability.
5. **Human-in-the-Loop Positioning:** System framed strictly as verification decision support, preserving human authority.
