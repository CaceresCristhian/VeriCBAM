# VeriCBAM Baseline Reproduction & Pipeline Classification

Recorded on: 2026-10-08
Python Environment: Python 3.12.10 (win32)
Test Suite Status: 19 passed, 0 failed, 0 skipped, 0 errors (in 2.72s)

## Step-by-Step Classification of `scripts/reproduce_all.py`

| Step | Pipeline Stage | Status Classification | Details / Evidence |
| :--- | :--- | :--- | :--- |
| **1** | Rebuild Multi-Pollutant Cohort from Raw EEA Tables (`src/data_loaders/build_cohort.py`) | **Passed** | Raw EEA E-PRTR tables present in `data/01_raw/eprtr_reference/csv_tables/`. Extracted 649 air pollutant records across 30 facilities, 177 plant-years. Runtime: 1.54s. |
| **2** | Rebuild Verified Technology Registry (`src/data_loaders/technology_registry.py`) | **Passed** | 30 facilities (15 steel, 15 cement) re-verified and output to `data/02_processed/facility_technology_registry.csv`. Runtime: 0.56s. |
| **3** | Generate Controlled Evaluation Benchmark (Legacy 101 cases) (`src/benchmark/perturbation_generator.py`) | **Passed** | Generated 101 cases (30 concordant, 71 perturbations across A/B/C/D). Output saved to `data/02_processed/controlled_perturbation_benchmark.parquet`. Runtime: 0.99s. |
| **4** | Generate Graded Multi-Source Benchmark (326 cases) (`src/benchmark/graded_benchmark_generator.py`) | **Passed** | Generated 326 graded cases (177 real negatives, 140 synthetic perturbations, 9 route mismatches). Runtime: 0.80s. |
| **5** | Execute 5-Model Ablation Study (`experiments/run_ablation_study.py`) | **Passed** | 5 models evaluated on 101 legacy cases. Summary written to `ablation_study_summary.csv`. Runtime: 2.14s. |
| **6** | Execute Probability Calibration (`experiments/calibrate_probabilities.py`) | **Passed** | 5-fold Platt scaling and isotonic regression on 101 legacy cases. Runtime: 2.09s. |
| **7** | Execute Facility-Grouped Cross-Validation (`experiments/run_grouped_validation.py`) | **Passed** | GroupKFold (5 splits, 30 groups). Runtime: 1.84s. |
| **8** | Execute Graded Benchmark Evaluation & ML Baseline Comparison (`experiments/run_graded_evaluation.py`) | **Passed** | 326 cases evaluated (Models A, B, C, D, E1 Expert, E2 Learned Logistic). Runtime: 3.20s. |
| **9** | Execute Likelihood Ratio & Prior Sensitivity (`experiments/run_lr_sensitivity.py`) | **Passed** | Sensitivity across priors [0.02, 0.15]. Runtime: 1.85s. |
| **10** | Run Automated Pytest Test Suite (`pytest -v`) | **Passed** | 19/19 test functions passed cleanly in 2.72s. |

### Note on Satellite Data / CDSE
Network calls to CDSE were NOT executed during this offline reproduction. Cached satellite data in `data/03_satellite_cache/` was used as specified in hard rules.
