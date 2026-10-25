# VeriCBAM: Project Summary & Executive Status Report
**Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment**

* **Author:** Cristhian David Cáceres Mateus (M.Sc. Data Science, University of Europe for Applied Sciences, Potsdam Campus)
* **Faculty Supervisor:** Dr. Humera Noor
* **Interactive Cloud Cockpit:** [https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/](https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/)
* **Code Repository:** [https://github.com/CaceresCristhian/VeriCBAM](https://github.com/CaceresCristhian/VeriCBAM)

---

### 1. Project Overview & Codebase Architecture
VeriCBAM is an open-source, explainable decision-support framework designed to screen declared greenhouse gas emissions under the European Union’s Carbon Border Adjustment Mechanism (CBAM, Regulation (EU) 2023/956). Rather than treating emissions verification as a black-box machine learning estimation problem or relying on unverified spreadsheets, VeriCBAM implements a multimodal evidence-fusion copilot that tests self-reported declarations against first-principles physics, satellite Earth observation, and compliance registries before costly on-site physical audits are commissioned.

* **Codebase Structure (`src/`):**
  * `src/core/stoichiometry/`: First-principles thermodynamic mass-balance calculators for cement clinker calcination (`cement_models.py`) and steel carbothermic reduction (`steel_models.py`), implementing EU Best Available Techniques (BAT) reference benchmarks and scrap dilution limits.
  * `src/core/bayesian/`: Transparent log-odds fusion engine (`evidence_fusion.py`) combining evidence likelihood ratios with dynamic confidence factors ($C_k$), Monte Carlo weight sensitivity intervals, and an explicit `Insufficient Evidence` abstention gate ($C_{\text{overall}} < 0.50$).
  * `src/data_loaders/`: Ingestion pipelines for the EEA E-PRTR / IED panel registry, Global Energy Monitor technology trackers, and leave-one-year-out co-pollutant combustion ratio baselines (`nox_baseline.py`).
  * `src/satellite/`: Copernicus Data Space Ecosystem client (`copernicus_client.py`) extracting Sentinel-5P TROPOMI Level-2 tropospheric $\text{NO}_2$ column density with cloud-fraction gating.
  * `src/ui/`: Full-featured 8-tab Streamlit decision cockpit (`app.py`) featuring interactive geospatial maps, stoichiometric sandboxes, waterfall Bayesian evidence graphs, and 1-click audit dossier generation.
* **Test Suite & Tooling:** 28 modular unit and integration tests (`pytest`) covering physical mass conservation, boundary rules, and inference calibration. Built using Python 3.12, Streamlit, Scikit-Learn, ReportLab, Pandas, NumPy, SciPy, and Plotly.

---

### 2. Empirical Datasets & Benchmark Design
1. **Layer A — Real-World European Industrial Reference Panel:** 177 authentic facility-year observations (2018–2023) across 30 heavy industrial installations (15 Cement, 15 Steel) spanning 10 EU Member States, extracted from the official European Environment Agency (EEA) E-PRTR / IED v16 database.
2. **Layer B — Curated 325-Case Graded Evaluation Benchmark:** Because overseas fraudulent CBAM declarations are legally confidential, models are evaluated on a controlled 325-scenario suite comprising:
   * **177 Authentic Compliant Negatives:** Unperturbed facility-years capturing empirical operating variance.
   * **140 Graded Controlled Understatements:** Synthetic reporting understatements across five distinct magnitudes ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$; 28 cases each).
   * **8 Process Route Misclassifications:** Cross-route greenwashing anomalies (e.g., claiming secondary Scrap-EAF emissions for primary integrated BF-BOF works).
3. **Technology & Capacity Registry:** Grounded in Global Energy Monitor (GEM) Global Steel and Cement Trackers, cross-referenced against national environmental operating permits to establish nameplate capacities and off-gas export infrastructure flags.

---

### 3. Scope Evolution & Technical Learnings
During project execution, several critical real-world industrial constraints necessitated significant refinements from initial naive assumptions:
* **The Process Gas Export Dilemma:** In academic literature, blast furnace reduction is modeled as an isolated system. In reality, European steelworks pipe blast furnace gas (BFG) across fence lines to external utility power plants. Evaluating such plants naively against stack stoichiometry generates false violations. VeriCBAM resolved this by mapping legal boundaries and setting `stoich_applicable = False` for gas-exporting plants, preventing false alarms.
* **Mathematical Derivation of the Stoichiometric Blind Spot:** Stoichiometric floors evaluated against nameplate capacity ($\eta_{\min} = 0.50$) possess an inherent mathematical blind spot:
  $$\delta^* = 1 - \left(\frac{\eta_{\min}}{\eta_{\text{actual}}}\right) \cdot \left(\frac{EF_{\text{floor}}}{EF_{\text{typical}}}\right)$$
  For an integrated mill operating at $\eta_{\text{actual}} = 0.80$ with typical intensity $1.90\text{ t CO}_2/\text{t}$, the floor ($1.35\text{ t/t}$) can only catch understatements exceeding $\delta^* \approx 55.6\%$. Moderate fraud ($10\%–20\%$) remains above the floor. This proved the mathematical necessity of fusing longitudinal baselines and co-pollutant ratios.
* **Satellite Role Realignment:** Initial assumptions that Sentinel-5P could directly meter factory annual $\text{CO}_2$ were disproved due to coarse spatial resolution ($5.5 \times 3.5\text{ km}$), atmospheric dispersion, and winter cloud decks. Satellite trace-gas data was formally repositioned from an emissions meter to an auxiliary operational presence gate.
* **Proxy Qualification:** Recognized that public registries report annual facility mass emissions ($t\text{CO}_2$), whereas CBAM regulates product-level specific intensities ($t\text{CO}_2e/t$). To prevent circularity or false claims, E-PRTR was formally qualified as an empirical proxy testing bed, and strict 5-fold `GroupKFold` by `facility_id` was enforced to prevent identity leakage.

---

### 4. Benchmarked Models & Empirical Results

| Candidate Model | Statistical Paradigm | ROC-AUC (95% CI) | PR-AUC | Brier Score | Recall @ 5% FPR | Triage Lift (Top 20%) | Operational Role |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Model A: Naive Prior** | Constant Uninformative | 0.500 | 0.369 | 0.233 | 0.050 | $1.00\times$ | Null reference baseline |
| **Model B: Stoichiometry** | First-Principles Bounds | 0.791 [0.72, 0.89] | 0.733 | 0.188 | 0.337 | $1.85\times$ | Hard physical veto; abstains on gas exports |
| **Model C: Satellite Alone** | Sentinel-5P $\text{NO}_2$ Contrast | 0.518 [0.50, 0.54] | 0.378 | 0.373 | 0.067 | $1.04\times$ | Standalone failure (96.6% authentic FPR) |
| **Model D: Historical Alone** | Longitudinal Pooled-MAD | 0.963 [0.96, 0.97] | 0.943 | 0.083 | 0.833 | $2.65\times$ | Highly sensitive to multi-year drift |
| **Model E1: Bayesian Fusion** | Weighted Log-Odds + Gating | 0.894 [0.87, 0.92] | 0.868 | 0.153 | 0.692 | **$2.67\times$** | **0.56% false alarms; auditable dossiers** |
| **Model E2: Logistic Triage** | Supervised GroupKFold | **0.964** [0.96, 0.97] | **0.948** | **0.079** | **0.850** | **$2.71\times$** | **Optimal rank-order screening queue** |

*Key Findings:*
1. **Model C confirms physical remote sensing limits:** Satellite $\text{NO}_2$ plume contrast alone yields near-random discrimination (ROC-AUC 0.518) and a disastrous 96.6% false positive rate on compliant plants, mathematically demonstrating that orbital trace gas cannot act as a direct $\text{CO}_2$ meter.
2. **Model E1 provides unmatched verifier safety:** The expert Bayesian fusion engine achieves an authentic false alarm rate of just **0.56%**, suppressing virtually all false accusations while providing a fully explainable, white-box waterfall chart for each audited declaration.
3. **Dual-Stage Regulatory Synergy:** Model E2 provides optimal high-throughput triage (ROC-AUC 0.964, catching 85% of understatements at a strict 5% false-alarm budget and delivering a **$2.71\times$ triage lift** over random auditing), while Model E1 generates the legally defensible site-visit dossier.

---

### 5. Verdict on the Current Stage
* **Core Strength:** VeriCBAM successfully establishes that multimodal evidence fusion works as an explainable, physics-informed decision-support tool. It bridges the gap between legal regulations (EU 2023/956, 2025/2546) and technical data science, solving boundary issues and achieving high triage efficiency ($2.71\times$ lift) without making black-box accusations.
* **Current Limitations:**
  1. *Historical Dependency:* Model E2 relies heavily on multi-year reporting history ($z_{\text{drop}}$). While available for EU facilities, non-EU third-country suppliers often lack verified multi-year records.
  2. *Proxy Mismatch:* Facility-level annual mass ($t\text{CO}_2$) cannot distinguish between an emissions reporting drop and a real drop in physical production volume ($Q$).
  3. *Satellite Gaps:* Sentinel-5P trace gas resolution ($5.5 \times 3.5\text{ km}$) remains too coarse and weather-dependent for point-source facility accounting.

---

### 6. Improvement Roadmap: Multi-Sensor Satellite Remote Sensing (VeriCBAM 2.0)
To eliminate reliance on self-reported production volumes ($Q$) and provide an independent physical activity baseline for overseas suppliers without historical records, the next development phase integrates multi-sensor Earth observation:

1. **Thermal Infrared (TIR) Operating Timelines (Landsat-8/9 TIRS, ECOSTRESS, SatVu):**
   * *Mechanism:* Cement rotary kilns operate at $1,400^\circ\text{C}$ with external steel shells radiating heat at $200^\circ\text{C}\text{--}350^\circ\text{C}$; blast furnace tapholes pour molten iron at $1,500^\circ\text{C}$.
   * *Impact:* High-resolution thermal sensors detect persistent heat signatures regardless of gas visibility. By tracking thermal anomalies over time, the system can reconstruct an independent calendar of operating days versus maintenance cooling periods, verifying whether a declared production decline corresponds to actual furnace idling.
2. **All-Weather Synthetic Aperture Radar (SAR, Copernicus Sentinel-1 C-Band):**
   * *Mechanism:* Sentinel-1 radar penetrates clouds, fog, and rain, operating day and night.
   * *Impact:* Heavy metallic structures, gantry cranes, and outdoor scrap piles generate distinctive double-bounce radar backscatter. Time-series interferometric and amplitude change detection over raw material storage yards establishes a continuous, weather-independent physical activity index across cloud-covered regions.
3. **Computer Vision for Freight & Stockpile Volumetrics (Sentinel-2, PlanetScope):**
   * *Mechanism:* Applying deep learning object detection (YOLOv8/v10) and photogrammetric shadow/stereo analysis to high-resolution optical satellite imagery (0.5m–3m resolution).
   * *Impact:*
     * *Logistics Counting:* Automated counting of bulk freight railcars, raw material hopper barges, and finished steel coil trucks at plant transport terminals.
     * *Stockpile Volumetric Depletion:* Measuring height and volume changes in raw limestone, iron ore, and metallurgical coal stockpiles.
     * *Closing the Loop:* Stockpile consumption and freight throughput provide an **independent estimate of physical production volume ($\hat{Q}$)**. Multiplying estimated volume by stoichiometric intensity bounds ($E_{\text{floor}} = \hat{Q} \times EF_{\text{floor}}$) completely eliminates the capacity blind spot, allowing VeriCBAM to detect moderate understatements ($10\%–20\%$) even for third-country plants with zero reporting history.
