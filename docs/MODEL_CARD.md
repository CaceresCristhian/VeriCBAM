# VeriCBAM Model Card: Multimodal Decision-Support for CBAM Auditing

**Model Version:** 2.0 (Post-Review Alignment & Graded Multi-Source Evaluation)  
**Date:** October 2026  
**Institution:** University of Europe for Applied Sciences (UE Germany), Berlin  
**Author:** Cristhian David Cáceres Mateus (M.Sc. Data Science) | **Supervisor:** Dr. Humera Noor  
**License:** MIT License  

---

## 1. Intended Use & Target Users
- **Primary Use Case:** Triage co-pilot for accredited verification bodies (under EU Regulation 2025/2551) and national competent customs authorities to prioritize physical on-site inspections for high-risk industrial installations.
- **Secondary Use Case:** Standalone pre-audit plausibility screening for European importers and non-EU commodity exporters to evaluate declared specific intensities against first-principles thermodynamic constraints.
- **Out of Scope & Misuse:** VeriCBAM is **not** an autonomous legal certification authority. It cannot legally issue CBAM compliance certificates or replace accredited verifier sign-off mandated by Regulation (EU) 2023/956.

---

## 2. Theoretical Architecture & Modalities
VeriCBAM synthesizes multi-source evidence within a confidence-weighted Bayesian log-odds fusion formulation:

$$\operatorname{logit} P(H \mid E) = \operatorname{logit} P(H) + \sum_{i=1}^M w_i C_i \ln(\operatorname{LR}_i)$$

1. **Stoichiometric Mass Balance (Physics):** Deterministic thermodynamic lower bounds for limestone calcination ($\mathrm{CaCO}_3 \rightarrow \mathrm{CaO} + \mathrm{CO}_2$) and carbothermic reduction ($\mathrm{Fe}_2\mathrm{O}_3 + 3\mathrm{C} \rightarrow 2\mathrm{Fe} + 3\mathrm{CO}$) under conservative industrial utilization ranges $[0.50, 0.95]$.
2. **Multi-Pollutant Combustion Consistency:** Evaluates within-plant reported $\mathrm{NO}_x/\mathrm{CO}_2$ ratios (empirical median $\mathrm{CV} = 11.1\%$ across 28 European plants) to flag declarations where $\mathrm{CO}_2$ drops without corresponding reduction in combustion $\mathrm{NO}_x$.
3. **Robust Longitudinal Fingerprints:** Leave-one-year-out log-ratio deviations scaled by pooled Median Absolute Deviation ($\sigma_{\text{pooled}} = 0.0911$ across 177 plant-years), preventing false positives from facility-specific rounding.
4. **Orbital Remote Sensing (Sentinel-5P TROPOMI):** Tropospheric $\mathrm{NO}_2$ plume contrast $z$-scores extracted via Microsoft Planetary Computer STAC range-reads.
5. **Documentary Process Route Cross-Check:** Flags declarations where high-carbon routes (integrated BF-BOF) claim secondary low-carbon benchmarks (Scrap-EAF).

---

## 3. Empirical Evaluation on Graded Benchmark (326 Cases)
Evaluated across 177 authentic real-year negatives, 140 graded understatements ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$), and 9 route misclassifications across 30 European installations:

| Model Architecture | ROC-AUC | PR-AUC | Brier Score | ECE (10 Bins) | False Positive Rate (Real Years) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Model B (Stoichiometry Alone)** | 0.6897 | 0.5248 | 0.2865 | 0.2647 | 0.00% |
| **Model C (Satellite Alone)** | 0.5221 | 0.3859 | 0.3719 | 0.3461 | 0.00% |
| **Model D (Historical Alone)** | 0.9659 | 0.9479 | 0.2352 | 0.3390 | 0.00% |
| **Model E1 (Expert Bayesian Fusion)** | 0.7693 | 0.5625 | 0.2716 | 0.1108 | 25.42% |
| **Model E2 (Learned Logistic Regression - GroupKFold)** | **0.9654** | **0.9502** | **0.0754** | **0.0469** | **5.65%** |

### Detection Recall by Understatement Magnitude ($\delta$):
- $\delta = 5\%$: Bayesian 28.6% | Logistic Regression 35.7% (Within normal operational variance)
- $\delta = 10\%$: Bayesian 28.6% | Logistic Regression 50.0% (Material threshold under Reg. 2025/2546)
- $\delta = 20\%$: Bayesian 46.4% | Logistic Regression 96.4%
- $\delta \ge 30\%$: Bayesian $\ge 57.1\%$ | Logistic Regression **100.0%**

### Triage Audit Priority Efficiency (Auditor Capacity Simulation):
- **Top 10% Audit Capacity:** Captures **22.3%** of all material inconsistencies (2.2× random baseline).
- **Top 20% Audit Capacity:** Captures **40.5%** of all material inconsistencies (2.0× random baseline).
- **Top 30% Audit Capacity:** Captures **50.4%** of all material inconsistencies (1.7× random baseline).

---

## 4. Key Scientific Caveats & Negative Findings
1. **Satellite Remote Sensing Limitation (Empirical Negative Result):**
   - **Cross-Sectional Analysis (2023):** Spearman correlation between Sentinel-5P tropospheric $\mathrm{NO}_2$ plume contrast and annual reported $\mathrm{CO}_2$ across 28 European plants is statistically insignificant ($\rho = 0.198, p = 0.312$).
   - **Multi-Year Longitudinal Analysis (2019–2023 via CDSE):** Direct annual Sentinel-5P queries using official Copernicus credentials across 25 facility-years confirmed that within-plant year-over-year $\mathrm{NO}_2$ changes do not track annual reported $\mathrm{CO}_2$ (mean within-plant Spearman $\rho = -0.100$, median $\rho = -0.462$).
   - **Physical Rationale:** TROPOMI pixel footprint ($5.5 \times 3.5\text{ km}$), regional background advection, meteorological variability, and variable stack combustion $\mathrm{NO}_x/\mathrm{CO}_2$ ratios preclude using orbital $\mathrm{NO}_2$ as an annual quantitative $\mathrm{CO}_2$ proxy. In VeriCBAM, satellite remote sensing is strictly designated as an auxiliary operational activity indicator and assigned conservative weight ($w_{\text{sat}} \le 1.0$).
2. **Proxy vs. CBAM Embedded Emissions:** Historical baseline data reflects E-PRTR direct facility Scope 1 emissions, which serve as an independent regulatory proxy rather than product-level CBAM embedded intensities (EU Regulation 2025/2547).
3. **Geographic Coverage:** Current validated benchmarks cover European heavy industrial sites; performance on non-EU installations remains uncalibrated due to the absence of public third-country industrial registries.
