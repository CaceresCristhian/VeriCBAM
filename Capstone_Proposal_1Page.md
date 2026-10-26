# Capstone Project Proposal (1-Page Core Summary): VeriCBAM
## Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment

* **Student Name:** Cristhian David Cáceres Mateus (Matriculation No: 93515346)
* **Degree Program:** Master of Science in Data Science (M.Sc. DSc)
* **Institution:** University of Europe for Applied Sciences (UE Germany), Potsdam Campus
* **Faculty Supervisor:** Dr. Humera Noor | **Submission Date:** October 2026 (Winter Semester 2026/2027)

---

### 1. Problem Statement & Regulatory Context
On **1 January 2026**, the European Union's Carbon Border Adjustment Mechanism (**CBAM**, Regulation (EU) 2023/956) entered its definitive financial regime. Authorised CBAM Declarants importing carbon-intensive goods (**Cement, Iron & Steel**) must declare verified embedded emissions and surrender CBAM certificates priced to EU ETS allowances (**Implementing Regulation (EU) 2025/2548**). While **Implementing Regulation (EU) 2025/2546** and **Delegated Regulation (EU) 2025/2551** mandate accredited third-party verification and physical installation audits, auditing thousands of third-country plants creates a severe global bottleneck ("arithmetic of scarcity"), forcing unverified importers onto punitive default mark-ups (**Implementing Regulation (EU) 2025/2621**).
* **Core Verification Challenge:** Customs authorities and accredited verifiers lack an automated, physics-informed pre-screening tool to triage declarations against three primary evasion vectors before commissioning costly overseas site inspections: **(A) Quantitative Understatement** of fuel/throughput, **(B) Stoichiometric Floor & Boundary Manipulation** (including uncounted off-site blast furnace gas transfers), and **(C) Process Route Misclassification** (e.g., declaring primary integrated BF-BOF steel as low-carbon Scrap-EAF).

### 2. Core Research Question & Technical Hypotheses
> **Research Question:** *Can heterogeneous physical, orbital, historical, and co-pollutant evidence streams be systematically fused into an explainable decision-support model that screens declared CBAM emissions inconsistencies more reliably than isolated single-modality sources?*
* **$H_1$ (Stoichiometric Floor & Detection Blind Spot):** Chemical mass-balance floors evaluated at conservative capacity utilization ($\eta_{\min} = 0.50$) deterministically catch severe violations and route fraud, but exhibit a mathematical blind spot $\delta^* = 1 - (\eta_{\min}/\eta_{\text{actual}})(EF_{\text{floor}}/EF_{\text{typical}})$ ($\approx 55.6\%$ for BF-BOF steel), necessitating statistical and observational fusion to catch moderate ($10\%\text{--}20\%$) understatements.
* **$H_2$ (Orbital Trace-Gas Gate):** Due to footprint dilution ($5.5 \times 3.5\text{ km}$), wind advection, and winter cloud cover, Copernicus Sentinel-5P TROPOMI tropospheric $\text{NO}_2$ cannot directly meter annual $\text{CO}_2$ mass, but serves as an auxiliary operational activity gate when weighted by cloud fraction ($C_{\text{sat}} = 1 - f_{\text{cloud}}$).
* **$H_3$ (Longitudinal & Co-Pollutant Fingerprinting):** Leave-one-year-out combustion ratios ($\text{NO}_x/\text{CO}_2$) and one-sided longitudinal deviations ($z_{\text{drop}}$) detect selective $\text{CO}_2$ under-reporting without penalizing legitimate production growth.
* **$H_4$ & $H_5$ (Dual-Stage Fusion & Abstention Gating):** Combining all streams via confidence-gated Bayesian log-odds fusion (**Model E1**, abstaining when $C_{\text{overall}} < 0.50$) and facility-grouped logistic regression (**Model E2**) suppresses false alarms at strict audit budgets ($\text{FPR} \le 5\%, 10\%$).

### 3. Proposed Stage 1 Methodology & 5-Stream Multimodal Architecture
VeriCBAM functions strictly as an **advisory screening copilot** (preserving human verifier authority under EU law) that fuses five evidence streams:
1. **Stream 1 — Chemical Stoichiometry & BAT Floors:** Limestone calcination ($\text{CaCO}_3 \rightarrow \text{CaO} + \text{CO}_2$, $0.495\text{ t CO}_2/\text{t clinker}$) plus EU CLM BREF minimum thermal fuel ($0.275\text{ t/t} \Rightarrow E_{\text{floor, clinker}} = 0.770\text{ t CO}_2/\text{t}$); iron ore reduction ($\text{Fe}_2\text{O}_3 + 3\text{C} \rightarrow 2\text{Fe} + 3\text{CO}$) yielding $EF_{\text{floor, BF-BOF}} = 1.350\text{ t/t}$, $EF_{\text{floor, DRI-EAF}} = 0.550\text{ t/t}$, and $EF_{\text{floor, Scrap-EAF}} = 0.040\text{ t/t}$. Explicitly abstains (`stoich_applicable = False`) when installations export process gas (BFG/COG) across legal boundaries.
2. **Stream 2 — Earth Observation Activity (Sentinel-5P TROPOMI):** Level-2 tropospheric $\text{NO}_2$ contrast between a $5\text{ km}$ plant target disk and a $15\text{--}30\text{ km}$ background ring: $z_{\text{sat}} = (\bar{V}_{\text{target}} - \bar{V}_{\text{bg}}) / (1.4826 \cdot \text{MAD}_{\text{bg}})$, filtered at $\text{qa\_value} \ge 0.50$.
3. **Stream 3 — Longitudinal Trajectory:** One-sided log-ratio drop against leave-one-year-out facility median scaled by pooled MAD ($\sigma_{\text{pooled}}$): $z_{\text{drop}, i, t} = \max(0, -(\ln E_{\text{declared}, i, t} - M_{i, -t}) / \sigma_{\text{pooled}})$.
4. **Stream 4 — Co-Pollutant Combustion Ratio:** Leave-one-year-out deviation in permit-monitored $\text{NO}_x / \text{CO}_2$ mass ratios ($R_{i, -t}$).
5. **Stream 5 — Technology & Route Verification:** Cross-checking declared routes and nameplate capacities against the Global Energy Monitor (GEM) Steel & Cement Trackers and national Industrial Emissions Directive (IED) permits.

* **Dual-Stage Decision Engines:**
  $$\operatorname{logit} P(H \mid E) = \operatorname{logit} P(H) + \sum_{k=1}^{5} w_k \cdot C_k \cdot \ln(\operatorname{LR}_k), \qquad C_{\text{overall}} = \frac{\sum_{k=1}^5 w_k C_k}{\sum_{k=1}^5 w_k}$$
  * **Model E1 (White-Box Bayesian Audit Dossier):** Uses prior $P(H)=0.08$, domain weights ($w \in [1.0, 2.0]$), 500 Monte Carlo weight-sensitivity draws, and an `Insufficient Evidence` gate ($C_{\text{overall}} < 0.50$) to generate traceable site-inspection dossiers.
  * **Model E2 (Supervised Triage Classifier):** $L_2$-regularized Logistic Regression trained via **5-Fold `GroupKFold(groups=facility_id)`** to rank-order customs declarations without cross-year facility identity leakage.

### 4. Empirical Reference Datasets & Validation Protocol
* **Layer A (Real-World European Proxy Panel):** Because overseas CBAM declarations are confidential, the project extracts **177 authentic facility-years (2018–2023)** across **30 European installations (15 Cement, 15 Steel across 10 EU Member States)** from the official **EEA E-PRTR / IED v16.0** registry (`DOI: 10.2909/657ac3cb-affa-4295-a4a9-27b4f539adab`), paired with GEM capacity metadata.
* **Layer B (325-Case Graded Benchmark):** Evaluates six architectures (**Model A** Naive Prior, **Model B** Stoichiometry, **Model C** Sentinel-5P Alone, **Model D** Historical Alone, **Model E1** Bayesian Fusion, **Model E2** Logistic Triage) across **177 authentic compliant negatives**, **140 graded synthetic understatements** ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$), and **8 route misclassifications**.
* **Validation Metrics:** ROC-AUC, PR-AUC, Brier Score, Expected Calibration Error (ECE), Authentic FPR, Recall at matched false-alarm budgets ($\text{FPR} = 5\%, 10\%$), Auditor Triage Lift (Top $10\%\text{--}30\%$), and **1,000 facility-clustered bootstrap 95% confidence intervals**.

### 5. Core Deliverables & Key Regulatory References
* **Deliverables:** Modular Python package (`src/`), 8-tab interactive Streamlit Decision Cockpit (`src/ui/app.py`) with 1-click PDF/Markdown audit dossier export and zero-history supplier pre-check, automated reproduction pipeline (`scripts/reproduce_all.py`), and `pytest` unit test suite.
* **Key References:** Regulation (EU) 2023/956 (CBAM); Implementing Regulations (EU) 2025/2546 (Verification), 2025/2547 (Monitoring), 2025/2621 (Default Values); Delegated Regulation (EU) 2025/2551 (Accreditation); EEA E-PRTR v16 (2026); JRC CLM/IS BREF (2012–2013); Beirle et al. (2019), *Science Advances* (TROPOMI $\text{NO}_2$).
