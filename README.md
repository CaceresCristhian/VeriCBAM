# VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Auditing

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live Cockpit](https://img.shields.io/badge/Live%20App-Streamlit%20Cloud-ff4b4b.svg)](https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/)
[![GitHub Repository](https://img.shields.io/badge/GitHub-VeriCBAM-blue?logo=github)](https://github.com/CaceresCristhian/VeriCBAM)

**Applied Capstone Project** — M.Sc. in Data Science, University of Europe for Applied Sciences (Potsdam Campus)  
**Author:** Cristhian David Cáceres Mateus (ID: 93515346) | **Supervisor:** Dr. Humera Noor

---

## 1. Purpose & Live Platform

Under **Regulation (EU) 2023/956** (CBAM) and **Implementing Regulation (EU) 2025/2546**, accredited verification bodies and customs authorities must screen thousands of self-reported cement and steel emissions declarations before commissioning €50k–€150k physical site inspections.

**VeriCBAM** provides an interactive, physics-and-satellite decision-support cockpit where verifiers, importers, and customs authorities can test any declaration in 30 seconds and export a **1-page Pre-Audit Screening Dossier PDF**:

* **Live Cloud Cockpit (Tab 1 Quick Audit):** [https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/](https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/)
* **External User Guide:** [`submissions/06_Quick_User_Guide.pdf`](submissions/06_Quick_User_Guide.pdf)

> VeriCBAM serves strictly as an advisory pre-audit screening tool (`Insufficient Evidence` when observational confidence $C_{\text{overall}} < 0.50$). It does not issue autonomous legal compliance certifications.

---

## 2. Six-Stream Multimodal Verification Architecture

```
CBAM Declaration (EU Plant, Third-Country Supplier, or CSV Upload)
   │
   ├── 1. Stoichiometric Mass Balance     (Cement calcination & Steel Fe2O3 reduction floors)
   ├── 2. Longitudinal E-PRTR Baseline    (2018–2023 leave-one-year-out robust MAD drift)
   ├── 3. Multi-Pollutant Ratio           (Within-plant leave-one-year-out NOx / CO2)
   ├── 4. Stage 1 Satellite Plumes        (Copernicus Sentinel-5P TROPOMI NO2 contrast)
   ├── 5. Stage 2 Multi-Sensor EO         (Landsat-8/9 30m TIR ΔT + VIIRS 375m + Planet/VHR)
   └── 6. Technology Route Registry       (GEM capacity & process gas-export boundaries)
   │
   ▼
Confidence-Weighted Bayesian Log-Odds Fusion & GroupKFold Logistic Triage
   └─► Verdict: Consistent | Potential Inconsistency | High Risk | Insufficient Evidence
   └─► 1-Click Pre-Audit Screening Dossier (1-Page PDF)
```

---

## 3. Empirical Results (325-Case Graded Benchmark)

Evaluated across **30 EU cement & steel facilities** (177 authentic real-year negatives from EEA E-PRTR v16 + 140 graded understatements $\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$ + 8 route misclassifications) with strict 5-fold `GroupKFold(groups=facility_id)` and 1,000 facility-cluster bootstrap CIs:

| Model Architecture | ROC-AUC (95% CI) | PR-AUC | Brier | Authentic FPR | Recall @ 10% FPR | Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Model B (Stoichiometry Alone)** | 0.7909 [0.719, 0.891] | 0.7326 | 0.1884 | 1.55% | 54.22% | Hard physical bound; abstains on off-gas exports |
| **Model C1 (Stage 1 Satellite: S-5P NO₂)** | 0.5183 [0.499, 0.544] | 0.3781 | 0.3731 | 96.61% | 10.83% | Auxiliary coarse plume check |
| **Model C2 (Stage 2 Multi-Sensor EO)** | **0.9658** [0.958, 0.975] | **0.9462** | 0.1634 | 24.86% | **92.50%** | Thermal + freight activity vs. declared CO₂ (works on zero-history third-country plants) |
| **Model D (Historical Alone)** | 0.9631 [0.957, 0.972] | 0.9428 | 0.0826 | 6.78% | 90.83% | Longitudinal drift anomaly detector |
| **Model E1 (Stage 1 Bayesian Fusion)** | 0.8935 [0.865, 0.924] | 0.8684 | 0.1530 | **0.56%** | 70.00% | Ultra-low false alarm dossier |
| **Model E2 (Stage 2 Bayesian Fusion)** | **0.9077** [0.885, 0.934] | **0.8763** | **0.1282** | 3.39% | **75.00%** | White-box verifier audit dossier |
| **Model E3 (Logistic GroupKFold Triage)** | **0.9646** [0.957, 0.974] | **0.9478** | **0.0777** | 7.34% | **92.50%** | High-throughput port triage queue ($2.71\times$ lift) |

---

## 4. Repository Structure

```text
VeriCBAM/
├── submissions/                      # Clean enumerated submission PDFs (01 through 06)
├── docs/                             # Data provenance, model card, deliverables playbook & MD sources
├── data/
│   ├── 01_raw/eprtr_reference/       # Official EEA E-PRTR / IED v16 database
│   ├── 02_processed/                 # 30-facility cohort, registry, NOx/CO2 ratios & 325-case benchmark
│   └── 03_satellite_cache/           # Cached Sentinel-5P, Landsat TIR, FIRMS VIIRS & VHR yard imagery
├── src/
│   ├── core/
│   │   ├── stoichiometry/            # Cement calcination & Steel reduction mass-balance models
│   │   └── bayesian/                 # Confidence-weighted log-odds evidence fusion engine
│   ├── data_loaders/                 # EEA cohort builder, CohortManager, GEM registry & LOO NOx ratios
│   ├── satellite/                    # Sentinel-5P client, plume analyzer & Stage 2 multi-sensor EO engine
│   ├── benchmark/                    # 325-case graded benchmark generator
│   └── ui/                           # Streamlined 7-tab Streamlit cockpit, theme & PDF dossier generator
├── experiments/
│   ├── run_graded_evaluation.py      # 325-case benchmark evaluation & Stage 2 EO comparison
│   └── results/                      # Summary CSVs, predictions parquet & sensitivity tables
├── scripts/                          # PDF builders (with shared pdf_utils.py) & reproduce_all.py
└── tests/                            # Automated pytest suite
```

---

## 5. Quick Start

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run automated test suite
pytest tests/ -v

# Reproduce data, 325-case benchmark evaluation & tests end-to-end
python scripts/reproduce_all.py

# Launch local Streamlit cockpit
python -m streamlit run src/ui/app.py
```
