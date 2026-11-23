# VeriCBAM Model Card: Multimodal Decision-Support for CBAM Auditing

**Model Version:** 2.2 (Stage 2 Multi-Sensor EO & Quick Audit Dossier Engine)  
**Date:** November 2026  
**Institution:** University of Europe for Applied Sciences (UE Germany), Potsdam Campus  
**Author:** Cristhian David Cáceres Mateus (M.Sc. Data Science) | **Supervisor:** Dr. Humera Noor  
**License:** MIT License

---

## 1. Intended Use & Target Users
- **Primary Use Case:** Pre-audit triage co-pilot for accredited verification bodies (under Commission Delegated Regulation (EU) 2025/2551) and customs authorities (DEHSt) to prioritize physical on-site inspections before certificate settlement under Implementing Regulation (EU) 2025/2546.
- **Secondary Use Case:** Zero-history third-country supplier screening for importers and regulators evaluating external facilities via stoichiometric mass balances and global Stage 2 Earth observation (Landsat 30m TIR + NASA FIRMS 375m VIIRS + VHR rail-yard freight).
- **Out of Scope:** VeriCBAM is advisory decision support and does not replace accredited physical verification statements.

---

## 2. Six-Stream Evidence Architecture
VeriCBAM fuses heterogeneous evidence streams within a confidence-weighted Bayesian log-odds formulation alongside a supervised `GroupKFold` triage model:

$$\operatorname{logit} P(H \mid E) = \operatorname{logit} P(H) + \sum_{i=1}^M w_i C_i \ln(\operatorname{LR}_i)$$

1. **Stoichiometric Mass Balance (Physics):** Chemical lower bounds for cement calcination ($\mathrm{CaCO}_3 \rightarrow \mathrm{CaO} + \mathrm{CO}_2$) and steel carbothermic reduction ($\mathrm{Fe}_2\mathrm{O}_3 + 3\mathrm{C} \rightarrow 2\mathrm{Fe} + 3\mathrm{CO}$) over conservative capacity utilization $[0.50, 0.95]$, abstaining explicitly (`stoich_applicable = False`) on blast-furnace plants exporting off-gases across permit boundaries.
2. **Longitudinal E-PRTR Drift:** Leave-one-year-out log-ratio deviations scaled by pooled MAD ($\sigma_{\text{pooled}} = 0.0911$ across 177 plant-years) using one-sided $\max(0, -z)$ scoring so legitimate growth is never penalized.
3. **Multi-Pollutant Combustion Consistency:** Leave-one-year-out $\mathrm{NO}_x/\mathrm{CO}_2$ baseline ratios flagging selective $\mathrm{CO}_2$ understatement relative to unperturbed combustion $\mathrm{NO}_x$.
4. **Stage 1 Atmospheric Plumes (Copernicus Sentinel-5P):** Tropospheric $\mathrm{NO}_2$ contrast weighted by clear-sky fraction ($w \le 1.0$).
5. **Stage 2 Multi-Sensor Thermal & Logistics EO:** USGS Landsat-8/9 30m core $\Delta T$, NASA FIRMS 375m VIIRS monthly active hotspot timelines ($\rho = +0.778, p = 0.0010$ on cement kilns), and VHR optical rail-yard/stockpile contrast achieving 100% separation between continuous BF-BOF and batch Scrap-EAF routes.
6. **Documentary Technology Registry Check:** Grounded in Global Energy Monitor (GEM) trackers and national environmental permits.

---

## 3. Empirical Evaluation on 325-Case Graded Benchmark
Evaluated across 177 authentic real-year negatives, 140 graded understatements ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$), and 8 route misclassifications across 30 European installations (95% CIs from 1,000 facility-cluster bootstrap resamples):

*Methodological Qualification:* Positives reflect controlled synthetic understatements applied to authentic reference facilities; effective independent facility sample size is $N = 30$.

| Model Architecture | ROC-AUC (95% CI) | PR-AUC (95% CI) | Brier Score | ECE | Authentic FPR | Recall @ 10% FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model B (Stoichiometry Alone)** | 0.7909 [0.719, 0.891] | 0.7326 [0.641, 0.845] | 0.1884 | 0.1571 | 1.55% | 54.22% |
| **Model C1 (Stage 1 Satellite: TROPOMI NO2)** | 0.5183 [0.499, 0.544] | 0.3781 [0.359, 0.396] | 0.3731 | 0.3474 | 96.61% | 10.83% |
| **Model C2 (Stage 2 Satellite: Thermal & Freight EO)** | **0.9658** [0.958, 0.975] | **0.9462** [0.934, 0.961] | 0.1634 | 0.2619 | 24.86% | **92.50%** |
| **Model D (Historical Alone)** | 0.9631 [0.957, 0.972] | 0.9428 [0.931, 0.957] | 0.0826 | 0.0632 | 6.78% | 90.83% |
| **Model E1 (Stage 1 Expert Bayesian Fusion)** | 0.8935 [0.865, 0.924] | 0.8684 [0.832, 0.901] | 0.1530 | 0.1652 | **0.56%** | 70.00% |
| **Model E2 (Stage 2 Multi-Sensor Bayesian Fusion)** | **0.9077** [0.885, 0.934] | **0.8763** [0.845, 0.910] | **0.1282** | 0.0978 | 3.39% | **75.00%** |
| **Model E3 (Learned Logistic Regression - GroupKFold)** | **0.9646** [0.957, 0.974] | **0.9478** [0.937, 0.961] | **0.0777** | **0.0596** | 7.34% | **92.50%** |

### Triage Prioritization Efficiency (Top-$k$ Audit Queue)
| Audit Capacity | Bayesian Caught | Bayesian Prec@k | Bayesian Lift | Logistic (E3) Caught | Logistic Prec@k | Logistic Lift |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Top 10% (32 cases)** | 32 | 100.0% | 2.71x | 32 | 100.0% | 2.71x |
| **Top 20% (65 cases)** | 64 | 98.5% | 2.67x | 65 | 100.0% | 2.71x |
| **Top 30% (97 cases)** | 83 | 85.6% | 2.32x | 91 | 93.8% | 2.54x |

---

## 4. Key Scientific Caveats
1. **Stage 1 Satellite Footprint Constraint:** Coarse Sentinel-5P TROPOMI $\mathrm{NO}_2$ ($5.5 \times 3.5\text{ km}$) yields near-random plant discrimination ($\rho = 0.198, p = 0.312$), which motivated the Stage 2 30m/375m Thermal Infrared & VHR Logistics upgrade (`Model C2`, ROC-AUC `0.9658`).
2. **Proxy Qualification:** Historical panels measure annual facility Scope 1 mass $\mathrm{CO}_2$, serving as an empirical testbed for product-level CBAM embedded intensities.
3. **Transferred Process Gases:** Five integrated blast-furnace steelworks export BF/COG gas to external power plants; VeriCBAM enforces `stoich_applicable = False` to eliminate false boundary violations.
