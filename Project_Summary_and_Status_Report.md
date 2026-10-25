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
  * `src/satellite/`: Copernicus Data Space Ecosystem client (`copernicus_client.py`) extracting Sentinel-5P TROPOMI Level-2 tropospheric $\text{NO}_2$ column density, alongside the **Stage 2 Multi-Sensor Thermal & Logistics Extractor** (`multisensor_client.py`) integrating USGS M2M Landsat-8/9 Collection-2 Level-2 TIRS 30 m surface temperature ($\Delta T$), NASA FIRMS VIIRS 375 m daily active kiln/furnace timelines, and PlanetScope / VHR optical rail-yard logistics analysis across all 30 facilities.
  * `src/ui/`: Full-featured 8-tab Streamlit decision cockpit (`app.py`) featuring interactive geospatial maps, stoichiometric sandboxes, visual multi-sensor thermal/freight verification cards, waterfall Bayesian evidence graphs, and 1-click audit dossier generation.
* **Test Suite & Tooling:** 30 modular unit and integration tests (`pytest`) covering physical mass conservation, boundary rules, and inference calibration. Built using Python 3.12, Streamlit, Scikit-Learn, ReportLab, Pandas, NumPy, SciPy, Rasterio, and Plotly.

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

### 4. Benchmarked Models & Empirical Results (Stage 1 + Stage 2 Multi-Sensor EO)

| Candidate Model | Statistical Paradigm | ROC-AUC (95% CI) | PR-AUC | Brier Score | Recall @ 5% FPR | Recall @ 10% FPR | Operational Role |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Model A: Naive Prior** | Constant Uninformative | 0.500 | 0.369 | 0.233 | 0.050 | 0.100 | Null reference baseline |
| **Model B: Stoichiometry** | First-Principles Bounds | 0.791 [0.72, 0.89] | 0.733 | 0.188 | 0.337 | 0.542 | Hard physical veto; abstains on gas exports |
| **Model C1: Stage 1 Satellite** | Sentinel-5P $\text{NO}_2$ Plume | 0.518 [0.50, 0.54] | 0.378 | 0.373 | 0.067 | 0.108 | Coarse plume check (96.6% authentic FPR) |
| **Model C2: Stage 2 Multi-Sensor EO** | Landsat 30m TIR + VIIRS + Freight | **0.966** [0.96, 0.98] | **0.946** | 0.163 | 0.842 | **0.925** | **Independent physical activity vs. declared $\text{CO}_2$** |
| **Model D: Historical Alone** | Longitudinal Pooled-MAD | 0.963 [0.96, 0.97] | 0.943 | 0.083 | 0.833 | 0.908 | Highly sensitive to multi-year drift |
| **Model E1: Stage 1 Bayesian** | Log-Odds + TROPOMI $\text{NO}_2$ | 0.894 [0.87, 0.92] | 0.868 | 0.153 | 0.692 | 0.700 | **0.56% false alarms; conservative dossier** |
| **Model E2: Stage 2 Bayesian** | Log-Odds + TIR & Freight EO | **0.908** [0.89, 0.93] | **0.876** | **0.128** | 0.675 | **0.750** | **Multi-Sensor Verifier Audit Dossier** |
| **Model E3: Logistic Triage** | Supervised 7-Feature GroupKFold | **0.965** [0.96, 0.97] | **0.948** | **0.078** | **0.858** | **0.925** | **Optimal port triage queue ($2.71\times$ lift)** |

*Key Findings:*
1. **Stage 2 Multi-Sensor EO (`Model C2`) overcomes Stage 1 atmospheric trace-gas limits:** While coarse Sentinel-5P $\text{NO}_2$ (`Model C1`) yields near-random discrimination (ROC-AUC 0.518), integrating 30 m USGS Landsat-8/9 TIRS thermal core anomalies ($\Delta T$ up to $+27.0^\circ\text{C}$), 375 m NASA FIRMS VIIRS daily operating months ($\rho = +0.778, p = 0.0010$ with cement $\text{CO}_2$), and VHR freight rail-yard contrast elevates satellite-based discrepancy detection to **ROC-AUC 0.966** (Recall@10% FPR = **92.5%**).
2. **Stage 2 Bayesian Fusion (`Model E2`) improves discrimination and calibration:** Fusing thermal kiln/furnace activity and optical freight logistics into the white-box Bayesian log-odds engine increases ROC-AUC from **0.894 to 0.908**, boosts Recall@10% FPR from **70.0% to 75.0%**, and lowers Brier error from **0.153 to 0.128**.
3. **100% Blast Furnace vs. Scrap-EAF Route Separation:** Every integrated BF-BOF steelworks exhibits 11–12 active thermal months and 85–706 VIIRS hotspots, whereas batch Scrap-EAF (`Georgsmarienhütte`) exhibits 8 active months and 37 hotspots, defeating cross-route greenwashing.

---

### 5. Verdict on the Completed Stage 2 System
* **Core Strength:** VeriCBAM now operates a complete 6-stream multimodal verification architecture combining thermodynamic mass-balance bounds, longitudinal E-PRTR baselines, co-pollutant ratios, Sentinel-5P $\text{NO}_2$, 30 m/375 m thermal infrared operating timelines, and VHR freight rail-yard activity across all 30 European reference installations.
* **Remaining Scope Boundaries:**
  1. *Proxy Qualification:* Public E-PRTR records report annual facility mass emissions ($t\text{CO}_2$), whereas CBAM regulates product-level specific embedded emissions ($t\text{CO}_2e/t$).
  2. *Optical Cloud Constraint:* Passive VHR optical imagery and Landsat thermal passes remain subject to cloud cover; all-weather Synthetic Aperture Radar (SAR) is the logical next step.

---

### 6. Next-Phase Horizon: All-Weather SAR & Stereo Volumetrics (Stage 3 Roadmap)
1. **All-Weather Synthetic Aperture Radar (Copernicus Sentinel-1 C-Band SAR):**
   * *Mechanism:* Dual-polarization (VV/VH) radar backscatter penetrates winter cloud cover day and night across northern Europe.
   * *Impact:* Interferometric coherence and double-bounce metallic scattering over raw-material yards and torpedo ladle tracks provide a cloud-immune daily logistics index.
2. **3D Stereo Stockpile Volumetrics & Fine-Tuned YOLOv10 Railcar Counting:**
   * *Mechanism:* Sub-meter commercial stereo imagery and oriented bounding-box (OBB) detection of hopper cars and slag pots.
   * *Impact:* Reconstructs absolute physical throughput $\hat{Q}$ (tonnes of clinker/crude steel) directly from space, closing the mass-balance loop ($E_{\text{floor}} = \hat{Q} \times EF_{\text{floor}}$) for third-country exporters with zero prior reporting history.
