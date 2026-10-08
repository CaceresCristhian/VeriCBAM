# VeriCBAM Model Card: Multimodal Decision-Support for CBAM Auditing

**Model Version:** 2.0 (Post-Review Alignment & Graded Multi-Source Evaluation)  
**Date:** October 2026  
**Institution:** University of Europe for Applied Sciences (UE Germany), Berlin  
**Author:** Cristhian David Cáceres Mateus (M.Sc. Data Science) | **Supervisor:** Dr. Humera Noor  
**License:** MIT License  

---

## 1. Intended Use & Target Users
- **Primary Use Case:** Triage co-pilot for accredited verification bodies (under Commission Delegated Regulation (EU) 2025/2551) and national competent customs authorities to prioritize physical on-site inspections for high-risk industrial installations.
- **Secondary Use Case:** Standalone pre-audit plausibility screening for European importers and non-EU commodity exporters to evaluate declared specific intensities against first-principles stoichiometric constraints.
- **Out of Scope & Misuse:** VeriCBAM is **not** an autonomous legal certification authority. It cannot legally issue CBAM compliance certificates or replace accredited verifier sign-off mandated by Regulation (EU) 2023/956.

---

## 2. Theoretical Architecture & Modalities
VeriCBAM synthesizes multi-source evidence within a confidence-weighted Bayesian log-odds fusion formulation:

$$\operatorname{logit} P(H \mid E) = \operatorname{logit} P(H) + \sum_{i=1}^M w_i C_i \ln(\operatorname{LR}_i)$$

1. **Stoichiometric Mass Balance (Physics):** Deterministic stoichiometric lower bounds for limestone calcination ($\mathrm{CaCO}_3 \rightarrow \mathrm{CaO} + \mathrm{CO}_2$) and carbothermic reduction ($\mathrm{Fe}_2\mathrm{O}_3 + 3\mathrm{C} \rightarrow 2\mathrm{Fe} + 3\mathrm{CO}$) under conservative industrial utilization ranges $[0.50, 0.95]$.
2. **Multi-Pollutant Combustion Consistency:** Evaluates within-plant reported $\mathrm{NO}_x/\mathrm{CO}_2$ ratios (empirical median $\mathrm{CV} = 11.1\%$ across 28 European plants) to flag declarations where $\mathrm{CO}_2$ drops without corresponding reduction in combustion $\mathrm{NO}_x$.
3. **Robust Longitudinal Fingerprints:** Leave-one-year-out log-ratio deviations scaled by pooled Median Absolute Deviation ($\sigma_{\text{pooled}} = 0.0911$ across 177 plant-years), preventing false positives from facility-specific rounding. *Note on pooled historical scale (N4):* the historical scale ($\sigma_{\text{pooled}}$) is computed across all plant-years, including held-out plants; it is an unsupervised scale statistic and fold-wise recomputation is documented as future work.
4. **Orbital Remote Sensing (Sentinel-5P TROPOMI):** Tropospheric $\mathrm{NO}_2$ plume contrast $z$-scores extracted via Microsoft Planetary Computer STAC range-reads.
5. **Documentary Process Route Cross-Check:** Flags declarations where high-carbon routes (integrated BF-BOF) claim secondary low-carbon benchmarks (Scrap-EAF).

---

## 3. Empirical Evaluation on Graded Benchmark
Evaluated across 177 authentic real-year negatives, 140 graded understatements ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$), and 8 route misclassifications across 30 European installations (95% confidence intervals from 1,000 facility-level bootstrap resamples).

*Methodological Qualification:* The learned model is trained on labels defined by the synthetic perturbation generator; it demonstrates learnable structure in the benchmark, not real-world fraud detection or legal non-compliance. The effective independent sample size is 30 installations.

| Model Architecture | ROC-AUC (95% CI) | PR-AUC (95% CI) | Brier Score | ECE (10 Bins) | False Positive Rate (Real Years) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Model B (Stoichiometry Alone)** | 0.7081 [0.647, 0.791] | 0.5325 [0.463, 0.636] | 0.2673 | 0.2337 | 32.20% |
| **Model C (Satellite Alone)** | 0.5183 [0.499, 0.544] | 0.3781 [0.359, 0.396] | 0.3731 | 0.3474 | 96.61% |
| **Model D (Historical Alone)** | 0.9657 [0.960, 0.973] | 0.9470 [0.938, 0.959] | 0.2359 | 0.3400 | 51.98% |
| **Model E1 (Expert Bayesian Fusion)** | 0.7761 [0.703, 0.853] | 0.5740 [0.493, 0.695] | 0.2525 | 0.1159 | 22.60% |
| **Model E2 (Learned Logistic Regression - GroupKFold)** | 0.9615 [0.953, 0.971] | 0.9450 [0.934, 0.958] | 0.0818 | 0.0654 | 7.34% |

### M5 Historical Score Ablation Study (Methodological Sign Convention)
| Variant | ROC-AUC | PR-AUC | Brier Score | ECE | Authentic FPR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| E1 Bayesian: Primary One-Sided max(0, -z) | 0.7761 | 0.5740 | 0.2525 | 0.1159 | 22.60% |
| E1 Bayesian: Secondary Two-Sided |z| | 0.7697 | 0.5697 | 0.2538 | 0.1126 | 22.60% |
| E2 Logistic: Primary One-Sided max(0, -z) | 0.9615 | 0.9450 | 0.0818 | 0.0654 | 7.34% |
| E2 Logistic: Secondary Two-Sided |z| | 0.9295 | 0.8960 | 0.0943 | 0.0518 | 6.78% |

### M1 Label Sensitivity Evaluation (Screening Thresholds)
| Screening Threshold & Model | Class Balance | ROC-AUC | PR-AUC | Brier Score | ECE |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Primary Rule: delta >= 10%** — Model E1 (Bayesian) | 120/325 (36.9%) | 0.7761 | 0.5740 | 0.2525 | 0.1159 |
| **Primary Rule: delta >= 10%** — Model E2 (Logistic) | 120/325 (36.9%) | 0.9615 | 0.9450 | 0.0818 | 0.0654 |
| **Sensitivity: delta >= 5%** — Model E1 (Bayesian) | 148/325 (45.5%) | 0.7586 | 0.6409 | 0.2841 | 0.1743 |
| **Sensitivity: delta >= 5%** — Model E2 (Logistic) | 148/325 (45.5%) | 0.9458 | 0.9442 | 0.0969 | 0.0422 |

### Triage Audit Priority Efficiency (Auditor Capacity Simulation)
| Audit Capacity | Bayesian (E1) Caught | Bayesian Precision@k | Bayesian Recall@k | Logistic (E2) Caught | Logistic Precision@k | Logistic Recall@k |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Top 10% (32 cases)** | 27 | 84.4% | 22.5% | 32 | 100.0% | 26.7% |
| **Top 20% (65 cases)** | 46 | 70.8% | 38.3% | 65 | 100.0% | 54.2% |
| **Top 30% (97 cases)** | 60 | 61.9% | 50.0% | 89 | 91.8% | 74.2% |

## 4. Key Scientific Caveats & Inconclusive Pilot Findings
1. **Satellite Remote Sensing Limitation (Inconclusive / Underpowered Pilot Evidence):**
   - **Cross-Sectional Analysis (2023):** Spearman correlation between Sentinel-5P tropospheric $\mathrm{NO}_2$ plume contrast and annual reported $\mathrm{CO}_2$ across 28 European plants is statistically insignificant ($\rho = 0.198, p = 0.312$).
   - **Multi-Year Longitudinal Analysis (2019–2023 via CDSE):** Direct annual Sentinel-5P queries across 5 German cement plants (25 plant-years total) yielded inconclusive results: within-plant Spearman $\rho$ values range from $-0.70$ to $+0.70$ (mean $\rho = -0.100$). The pilot was underpowered ($n=5$ per plant, 2–13 clear overpasses per summer season, June–August window, without background ring subtraction).
   - **Physical Rationale:** TROPOMI pixel footprint ($5.5 \times 3.5\text{ km}$), regional background advection, meteorological variability, and variable stack combustion $\mathrm{NO}_x/\mathrm{CO}_2$ ratios preclude using orbital $\mathrm{NO}_2$ as an annual quantitative $\mathrm{CO}_2$ proxy at individual plant scale. In VeriCBAM, satellite remote sensing is strictly designated as an auxiliary operational activity indicator and assigned conservative weight ($w_{\text{sat}} \le 1.0$).
2. **Proxy vs. CBAM Embedded Emissions:** Historical baseline data reflects E-PRTR direct facility Scope 1 emissions, which serve as an independent regulatory proxy rather than product-level CBAM embedded intensities (EU Regulation 2025/2547).
3. **Geographic Coverage:** Current validated benchmarks cover European heavy industrial sites; performance on non-EU installations remains uncalibrated due to the absence of public third-country industrial registries.
