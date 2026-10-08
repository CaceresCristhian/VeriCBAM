# VeriCBAM Codebase & Methodology Changelog

All notable changes to the **VeriCBAM** decision-support system are documented in this file.

---

## [2.1.0] - 2026-10-08 — Phase 1 through Phase 5 Comprehensive Alignment

### Summary
This release executes the full scientific, regulatory, and methodological improvements defined in the project improvement specification (`VeriCBAM_Improvement_Prompt_Final.md`), achieving complete internal consistency, honest reporting, and deterministic offline reproducibility across all 11 pipeline stages.

---

### 1. Legal and Regulatory Corrections (Phase 1)
- **Commission Delegated Regulation (EU) 2025/2551:** Corrected regulatory classification from "Implementing Regulation" to "Delegated Regulation" across all documentation (`README.md`, `Capstone_Proposal_Document.md`, `docs/MODEL_CARD.md`, `docs/VeriCBAM_Project_Plan.md`), UI (`src/ui/app.py`), and admin forms (`admin/generate_official_application_pdf.py`). Regenerated official application PDF (`admin/VeriCBAM_Capstone_Application_Form_Filled_v2.pdf`). Added EUR-Lex ELI link: `http://data.europa.eu/eli/reg_del/2025/2551/oj`.
- **Materiality Threshold Clarification:** Stripped unsupported claims of a "10% legal materiality threshold" from benchmark descriptions and model cards. Relabeled to **project-defined screening threshold** and documented that Commission Implementing Regulation (EU) 2025/2546 (Article 5) defines materiality at the product level for specific embedded emissions, not facility-level E-PRTR Scope 1 totals.
- **Terminology Synchronization:**
  - Replaced *"independent evidence"* with **"heterogeneous evidence"**.
  - Replaced *"thermodynamic floor / absolute physical minimum"* with **"stoichiometric lower bound"** or **"route-specific engineering lower bound"**.
  - Replaced *"calibrated Bayesian"* with **"expert-parameterized Bayesian fusion"**.
  - Replaced fraud/violation detection terminology with **"material inconsistency screening"** and **"understatement detection"**.
- **Satellite Empirical Reframing:** Described Sentinel-5P remote sensing results strictly as **"inconclusive / underpowered pilot evidence at the tested plant-level temporal/spatial scale"**, documenting the weak empirical correlation ($\rho = 0.198$ cross-sectional; mean $\rho = -0.100$ within-plant) across 5 German cement plants.
- **Robust CDSE Credentials Loading:** Updated `src/satellite/copernicus_multiyear_client.py` to prioritize `CDSE_CLIENT_ID` and `CDSE_CLIENT_SECRET` environment variables with safe fallback. Excluded all credential files from git and packaging archives.
- **Authoritative Weights Table:** Documented exact weights matching `src/core/bayesian/evidence_fusion.py` ($w_{\text{stoich}}=1.5, w_{\text{sat}}=1.0, w_{\text{hist}}=1.0, w_{\text{nox}}=1.2, w_{\text{reg}}=0.8, w_{\text{route}}=2.0$) across documentation.

---

### 2. Methodological & Benchmark Code Fixes (Phase 2)

#### M3: Removal of Nameplate Capacity Fallback
- Completely eliminated the fallback `cap_mtpa = 2.0` in `src/benchmark/graded_benchmark_generator.py`.
- Facilities with unobserved crude steel capacity in `facility_technology_registry.csv` (*thyssenkrupp Werk Hamborn*, *thyssenkrupp Werk Beeckerwerth*, *DK Recycling und Roheisen GmbH*) receive `stoich_available=False`, `NaN` stoichiometric floors, and zero violation flags.
- Added a guard in the route-mismatch benchmark loop, skipping plants without crude steel capacity (skips Hamborn). The route mismatch set now contains exactly **8 controlled cases** (reduced from 9 pre-fix; 11 in legacy 101 suite).
- In Bayesian evidence fusion (`src/core/bayesian/evidence_fusion.py`), the stoichiometry stream cleanly abstains ($LR=1.0, C=0.0$) when capacity is unobserved. Model B (stoichiometry alone) outputs an uninformative baseline probability of $0.50$.
- Evaluated benchmark population updated from 326 to **325 cases** (177 authentic negatives, 140 graded understatements, 8 route mismatches). Exactly 33 cases have `stoich_available=False`.

#### M6: Leave-One-Year-Out NOx/CO2 Combustion Ratio Baseline
- Created pure function `compute_leave_one_year_out_nox_ratios` in `src/data_loaders/nox_baseline.py`.
- For each evaluated facility-year $(f, y)$, the baseline distribution strictly excludes year $y$ itself, preventing circularity and self-scoring contamination.
- Enforces a minimum of 3 remaining reference years (`min_years=3`); otherwise, outputs NaN (stream abstains).
- Integrated into `src/data_loaders/build_cohort.py` to generate `data/02_processed/facility_nox_co2_ratios.csv` (177 rows, 165 valid fingerprints).
- Generator and tests updated to query `(facility_id, reporting_year)`.

#### M5: Historical Drift Score Ablation
- Verified sign convention: $\log(declared / historical\_median) < 0$ for understatements, producing robust $z < 0$.
- Implemented and evaluated both historical score variants in `experiments/run_graded_evaluation.py`:
  - **Primary Variant (Methodological):** One-sided score $\max(0, -z)$. Justification: Declarations cannot understate emissions by expanding them; legitimate production growth should not be penalized.
  - **Secondary Variant:** Two-sided score $|z|$.
- Findings: One-sided scoring improves Model E1 Bayesian ROC-AUC from $0.7697$ to $0.7761$, and Model E2 Logistic Regression ROC-AUC from $0.9295$ to $0.9615$.

#### M1: Benchmark Label Threshold Sensitivity
- Evaluated both project-defined screening rules in `experiments/run_graded_evaluation.py`:
  - **Primary Rule:** $\delta \ge 10\%$ (Prevalence: $120 / 325 = 36.9\%$).
  - **Sensitivity Rule:** $\delta \ge 5\%$ (Prevalence: $148 / 325 = 45.5\%$).
- Saved results to `experiments/results/graded_label_sensitivity.csv`.

#### M8: Facility-Level Cluster Bootstrap & Auditor Triage
- Implemented cluster bootstrap resampling $1,000$ times at the installation level (`facility_id`, seed 0), preserving intra-facility correlation across repeated years.
- Reported 95% confidence intervals for ROC-AUC, PR-AUC, Brier score, ECE, and authentic negative FPR ($\tau = 0.50$).
- Simulated customs auditor prioritization for top 10%, 20%, and 30% capacity constraints, reporting Precision@k and Recall@k for **both** Bayesian (E1) and Logistic Regression (E2) models. Saved to `experiments/results/triage_auditor_simulation.csv`.

#### Attribution Study
- Generated `experiments/results/attribution_study.csv` tracing metrics at each milestone:
  $$\text{Baseline} \rightarrow \text{+M3 (No Cap Fallback)} \rightarrow \text{+M6 (LOYO NOx)} \rightarrow \text{+M5 Primary } \max(0, -z) \rightarrow \text{Sensitivity } (\delta \ge 5\%)$$

#### N5: Pytest Unit Test Suite Expansion
- Created `tests/test_graded_benchmark_and_fixes.py` with 5 rigorous tests:
  1. `test_m3_capacity_fallback_removal`: validates `stoich_available=False` and NaN floors for Hamborn, Beeckerwerth, and DK Recycling; verifies Hamborn excluded from route mismatch.
  2. `test_m1_label_thresholds_sensitivity`: verifies label assignment under both 5% and 10% rules.
  3. `test_m6_leave_one_year_out_nox_baseline`: verifies strict exclusion of evaluated year and 3-year minimum requirement.
  4. `test_duplicate_resolution_rule`: tests deterministic maximum-release deduplication.
  5. `test_m5_one_sided_historical_score`: tests one-sided vs two-sided sign logic and Bayesian engine response.
- Total pytest suite passing: **24/24 tests passed** (increased from 19/19 baseline).

---

### 3. Documentation & Verification Tooling (Phase 3)
- Created `scripts/render_results_tables.py` to inject empirical results from CSVs directly into `README.md` and `docs/MODEL_CARD.md`.
- Updated test badge in `README.md` to "24/24 tests pass".
- Added note on unsupervised pooled historical scale (N4) across documentation.
- Documented CO2 variable choice in `docs/DATA_PROVENANCE.md` (N3).

---

### 4. UI Tier A Implementation (Phase 4)
- **`src/ui/app.py`:**
  - Added persistent `scope_banner()` across all pages.
  - Tab 7 rebuilt to display primary 325-case graded benchmark results, 95% bootstrap CIs, M5 ablation, M1 sensitivity, and auditor triage simulation.
  - Collapsed legacy 101-case ablation suite into an expander labelled strictly for regression testing.
  - Removed hardcoded captions ("Zero False Positives", "Lowest Error").
  - Removed external image and font dependencies; implemented system font fallbacks.
  - Applied `html.escape(...)` to dynamic variables inserted into raw HTML.
  - Relabeled "Thermodynamic Floor" to "Stoichiometric Lower Bound".
  - Moved author and supervisor metadata to Tab 8 ("About & Proposal").
- **`src/ui/stitch_cockpit.html`:**
  - Removed static unverified numbers (`0.9984`, `99.2%`).
  - Aligned evidence weights table with authoritative values ($1.5, 1.0, 1.0, 1.2, 2.0$).
  - Reframed decision synthesis panel around 4-tier screening verdicts.
  - Converted external Google Fonts to local system fonts for offline defense readiness.

---

### 5. Master Pipeline & Reproducibility (Phase 5)
- Updated `scripts/reproduce_all.py` to execute all 11 stages end-to-end, including documentation rendering and full test suite execution.
