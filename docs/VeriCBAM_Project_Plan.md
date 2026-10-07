# VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment

**Project Title:** VeriCBAM (Verification & Consistency Assessment for Carbon Border Adjustment Mechanism)  
**Academic Module:** Data Science Capstone Project (Winter 2026/2027)  
**Institution:** University of Europe for Applied Sciences (UE Germany)  
**Supervisor:** Dr. Humera Noor  
**Student:** Cristhian David Cáceres Mateus  
**Target Milestone 1 Approval:** October 12, 2026  
**Final Submission & Defense:** January 2027  

---

## 1. Executive Summary & Problem Framing

### 1.1 The Regulatory Context
In **2026, the European Union's Carbon Border Adjustment Mechanism (CBAM) entered its definitive financial enforcement phase** under Regulation (EU) 2023/956. European importers of heavy industrial goods—primarily **Cement, Iron & Steel, Aluminium, Fertilisers, Hydrogen, and Electricity**—are legally required to report the specific embedded direct (Scope 1) and indirect (Scope 2) greenhouse gas emissions of their non-EU manufacturing installations and surrender corresponding financial CBAM certificates.

### 1.2 The Industrial & Compliance Challenge
European industrial buyers, customs brokers, and National Competent Authorities (such as Germany's *DEHSt*) face an acute operational and economic bottleneck under the CBAM definitive regime:

1. **The Escalating Financial Cost of Physical Audits:**
   Under Regulation (EU) 2023/956 (Articles 8 & 9), Commission Implementing Regulation (EU) 2025/2546 (verification rules), Implementing Regulation (EU) 2025/2551 (verifier accreditation), and Implementing Regulation (EU) 2025/2547 (calculation of embedded emissions), physical on-site audits are mandatory for initial verification when claiming actual embedded emissions. Empirical industry research (GMK Center, 2024; European Commission SWD(2021) 643 final) demonstrates that third-party verification costs scale steeply with industrial complexity:
   * **Simple / Single-Product Units:** €5,000 to €15,000 per facility (e.g. standalone scrap EAF or rolling mill with pre-existing ISO 14064 MRV).
   * **Medium Heavy Industrial Sites:** €15,000 to €50,000 per facility (e.g. merchant cement clinker rotary kiln).
   * **Complex Integrated Heavy Industry (The VeriCBAM Target Focus):** **€50,000 to €150,000+ per site visit** for integrated Blast Furnace–Basic Oxygen Furnace (BF-BOF) steelworks and multi-kiln cement mega-complexes. When factoring in mandatory international auditor travel to non-EU jurisdictions (e.g. India, China, Turkey, Brazil), forensic chemical assay of raw meal/coke, and local security/logistics, full compliance costs frequently reach **€75,000 to €210,000+ per enterprise**.

2. **The "Arithmetic of Scarcity" & Administrative Timeline Delays:**
   A severe structural market failure compounds this cost burden:
   * **Demand vs. Supply Deficit:** Approximately **12,000 EU import entities** are seeking authorized CBAM declarant status across tens of thousands of supplying installations, yet only **~403 verification bodies globally** hold active accreditation under the EU Accreditation and Verification Regulation (**AVR - Commission Implementing Regulation (EU) 2018/2067** / **(EU) 2025/2551**).
   * **Extended Verification Lead Times:** A complete physical site verification cycle takes **3 to 6 months** from initial engagement, monitoring plan reconciliation, on-site physical walk-through, to final report sign-off. Importers failing to contract verifiers 6–9 months ahead of annual deadlines face complete scheduling lockouts.
   * **The Punitive Alternative (Default Value Mark-Up):**
     If an overseas installation cannot secure physical verification in time, importers are forced to surrender CBAM certificates calculated via the European Commission's **default emissions values**, which carry punitive administrative mark-ups:
     $$\text{Markup} = +10\% \text{ (2026)} \longrightarrow +20\% \text{ (2027)} \longrightarrow +30\% \text{ (from 2028)}.$$
     For an integrated steel mill exporting 500,000 tonnes of steel, this default surcharge imposes an unrecoverable **€5,000,000 to €20,000,000+** financial penalty.

3. **Audit Prioritization Dilemma:**
   Because comprehensive physical inspection of every non-EU supplier is mathematically and economically impossible, compliance officers urgently require an objective, automated, and legally defensible pre-audit screening mechanism to **triage which declarations represent genuine compliance and which warrant deep-dive accredited physical audits**.

### 1.3 The VeriCBAM Solution
**VeriCBAM** is an **explainable, multimodal industrial intelligence and decision-support system** designed to screen and assess the consistency of self-reported CBAM declarations. 

Rather than claiming to replace accredited legal certification bodies or directly measure facility CO₂ emissions from space, VeriCBAM functions as an **evidence-fusion auditor copilot**:
* It establishes **physical plausibility** via first-principles chemical engineering process bounds and BAT benchmarks.
* It evaluates **operational consistency** via Copernicus Sentinel-5P TROPOMI tropospheric $\text{NO}_2$ atmospheric activity anomalies (with Sentinel-5P $\text{CO}$ and Sentinel-2 SWIR designated as planned extensions).
* It compares behavior against **facility historical fingerprints** from verified industrial registries.
* It integrates these independent data streams through a **deterministic Bayesian evidence-fusion engine** that quantifies risk alongside explicit confidence and uncertainty intervals.
* It delivers an **explainable reasoning graph and audit dossier** for human decision-makers.

---

## 2. Central Research Formulation

### 2.1 Dominant Research Question
> **To what extent can independent physical, observational, historical, and documentary evidence be fused into an explainable decision-support model that identifies controlled CBAM emissions inconsistencies more reliably than isolated evidence sources?**

### 2.2 Supporting Research Sub-Questions
* **RQ1 (Physical Plausibility):** How accurately can chemical engineering mass-balance and stoichiometric lower bounds identify physically implausible declared specific emissions ($SEE_g$)?
* **RQ2 (Earth Observation Activity):** Can Copernicus Sentinel-5P TROPOMI tropospheric $\text{NO}_2$ provide a statistically valid operational activity indicator that correlates with reported industrial activity?
* **RQ3 (Historical Behavior & Fingerprinting):** Can facility-specific multivariate historical profiles (E-PRTR, production capacity, emissions intensity) detect anomalous deviations in newly declared reporting periods?
* **RQ4 (Multimodal Evidence Fusion):** Does combining physical, observational, and historical evidence streams yield superior Precision, Recall, F1, and False Positive Rates compared to single-modality baselines?
* **RQ5 (Uncertainty Quantification):** How do atmospheric observation gaps (cloud cover, resolution limits) and parameter uncertainties propagate into the final consistency confidence score?
* **RQ6 (Explainability & Human-in-the-Loop):** Can the system generate auditable, evidence-grounded reasoning chains that enable compliance officers to inspect, understand, and justify audit prioritization decisions?

---

## 3. System Architecture & Evidence-Fusion Pipeline

VeriCBAM follows a decoupled, deterministic-first architecture where AI models serve as extractors, anomaly detectors, and explainers, while core scoring logic remains strictly auditable and reproducible.

```text
                             [ CBAM Declaration (PDF / Excel / XML) ]
                                                │
                                                ▼
                         ┌──────────────────────────────────────────────┐
                         │      DOCUMENT INTELLIGENCE & EXTRACTION      │
                         │   • Pydantic Schema-Enforced Field Parser    │
                         │   • Facility Coords, Route, Output, SEE      │
                         └──────────────────────┬───────────────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 ▼                              ▼                              ▼
  ┌─────────────────────────────┐┌─────────────────────────────┐┌─────────────────────────────┐
  │     EVIDENCE STREAM 1:      ││     EVIDENCE STREAM 2:      ││     EVIDENCE STREAM 3:      │
  │     CHEMICAL PROCESS &      ││   EARTH OBSERVATION SENSING ││    HISTORICAL PROFILES &    │
  │     STOICHIOMETRIC BOUNDS   ││     (Copernicus Sentinel)   ││    FACILITY FINGERPRINTS    │
  │                             ││                             ││                             │
  │ • Route mass/carbon balance ││ • Sentinel-5P TROPOMI NO2   ││ • Global Energy Monitor     │
  │ • Fuel/electricity inputs   ││ • Background deconvolution  ││ • E-PRTR multi-year history │
  │ • Process lower bounds:     ││ • Sentinel-2 SWIR Hotspot   ││ • Capacity utilization     │
  │   E_min(route, assumptions) ││ • Observation quality flag  ││ • Temporal anomaly score    │
  │ • Plausibility Index (0-1)  ││ • Activity Index (0-1)      ││ • Historical Drift (0-1)    │
  └──────────────┬──────────────┘└──────────────┬──────────────┘└──────────────┬──────────────┘
                 │                              │                              │
                 └──────────────────────────────┼──────────────────────────────┘
                                                │ Structured Evidence Vectors (e_i, c_i)
                                                ▼
                         ┌──────────────────────────────────────────────┐
                         │         EVIDENCE FUSION & RISK LAYER         │
                         │                                              │
                         │  • Deterministic Bayesian Fusion             │
                         │  • Calibrated Risk Score: P(Inconsistency|E) │
                         │  • Uncertainty & Coverage Quantification     │
                         │  • "Insufficient Evidence" State Trigger     │
                         └──────────────────────┬───────────────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
  ┌─────────────────────────────┐                               ┌─────────────────────────────┐
  │   COUNTERFACTUAL REASONING  │                               │    EXPLAINABLE AUDITOR &    │
  │                             │                               │     REPORT GENERATOR        │
  │ • "What fuel/CCUS scenario  │                               │                             │
  │    could explain 0.8 t/t?"  │                               │ • LLM Narrative Synthesis   │
  │ • Recommended next evidence │                               │ • Interactive Streamlit UI  │
  │   needed to reduce entropy  │                               │ • PDF Audit Dossier Export  │
  └─────────────────────────────┘                               └─────────────────────────────┘
```

### 3.1 The Evidence-Fusion Formulation & Hierarchy

VeriCBAM organizes verification into an auditable four-level evidence hierarchy:
* **Level 1 — Physical Consistency:** Process-specific lower bounds conditioned on declared technology (limestone calcination and hematite reduction stoichiometry). Deterministically flags physical impossibilities.
* **Level 2 — Operational Consistency:** Sentinel-5P TROPOMI trace-gas plumes ($NO_2/CO$) and Sentinel-2 Short-Wave Infrared (SWIR Bands 11/12) operational activity indicators.
* **Level 3 — Historical Consistency:** Multivariate facility fingerprints and longitudinal drift ($Z_{\text{temp}}$) from verified reference reporting baselines.
* **Level 4 — Multimodal Synthesis:** Confidence-weighted Bayesian log-odds synthesis:

$$\text{logit } P(H \mid E) = \text{logit } P(H) + \sum_{i} C_i \cdot \log(LR_i)$$

$$P(H \mid E) = \sigma\left(\text{logit } P(H) + \sum_{i} C_i \log(LR_i)\right)$$

Where:
* $H$: Material inconsistency event in the declaration.
* $P(H) \approx 0.08$: Base prior probability (derived from international ETS audit baseline discrepancies).
* $LR_i = \frac{P(E_i \mid H)}{P(E_i \mid \neg H)}$: Likelihood ratio of evidence stream $i$.
* $C_i \in [0, 1]$: Observational confidence/reliability factor (e.g. $C_{\text{sat}} = \max(0, 1 - \text{cloud\_fraction})$).
* The model approximates conditional independence between evidence channels while applying explicit confidence weights and dependency-aware adjustments.

### 3.2 Explicit Uncertainty & Four Categorical System Outcomes
VeriCBAM strictly separates **Inconsistency Risk** ($P(H \mid E)$) from **Observational Confidence** ($C_{\text{overall}}$). When cloud cover or missing records degrade data quality, the system enters an explicit **Insufficient Evidence** state rather than forcing a binary classification:

$$\text{System Outcome} \in \begin{cases}
\text{Consistent} & \text{if } P(H \mid E) < 0.25 \text{ and } C_{\text{overall}} \ge 0.50 \\
\text{Potential Inconsistency} & \text{if } 0.25 \le P(H \mid E) < 0.70 \text{ and } C_{\text{overall}} \ge 0.50 \\
\text{High Inconsistency Risk} & \text{if } P(H \mid E) \ge 0.70 \text{ and } C_{\text{overall}} \ge 0.50 \\
\text{Insufficient Evidence} & \text{if } C_{\text{overall}} < 0.50 \text{ (cloud obscuration or missing baselines)}
\end{cases}$$

---

## 4. Sector-Aware Chemical Engineering Models (Tier 1 MVP)

### 4.1 Sector 1: Cement & Clinker (Primary Benchmark Route)
* **Chemical Foundation:** Limestone decarbonation process emissions represent an inescapable material constraint:
  $$CaCO_3 \xrightarrow{\Delta} CaO + CO_2 \uparrow$$
* **Mass Balance Bound:** With typical clinker composition containing $\approx 64-67\%$ reactive $CaO$:
  $$\text{Process Emission Factor} = \text{CaO Content} \times \frac{44.01}{56.08} \approx 0.51 - 0.54\text{ }tCO_2 / t_{\text{clinker}}$$
* **Engineering Fuel Boundary:** Adding minimum thermal energy required for kiln sintering ($2.9 - 3.3\text{ }GJ/t_{\text{clinker}}$) establishes the parametric lower bound:
  $$E_{\min, \text{clinker}} = f(\text{Clinker Ratio}, \text{Thermal Efficiency}, \text{Fuel Mix}) \ge 0.68\text{ }tCO_2 / t_{\text{cement}}$$

### 4.2 Sector 2: Iron & Steel (Secondary Benchmark Route)
* **Route A: Blast Furnace - Basic Oxygen Furnace (BF-BOF):**
  * Primary reduction of hematite ore via carbon:
    $$Fe_2O_3 + 3C \rightarrow 2Fe + 3CO \rightarrow 3CO_2$$
  * Stoichiometric reduction minimum: $1.182\text{ t }CO_2/\text{t crude iron}$.
  * Constrained by thermodynamic enthalpy balance, blast furnace coke consumption ($300-360\text{ }kg/t$), and hot metal carbon saturation.
  * Baseline lower bound: $\approx 1.35 - 1.70\text{ }tCO_2 / t_{\text{crude steel}}$ (conditioned on scrap fraction and pig iron ratio).
* **Route B: Direct Reduced Iron - Electric Arc Furnace (DRI-EAF):**
  * Methane/Syngas-based reduction: lower stoichiometric minimum bound ($\approx 0.55 - 0.95\text{ }tCO_2 / t$), strongly dependent on local electrical grid emissions factor.
  * Green Hydrogen DRI ($100\%\text{ H}_2$): $\approx 0.04 - 0.15\text{ }tCO_2 / t$ (electrode wear and recarburizer only).

---

## 5. Authentic Data Architecture & Controlled Benchmark Design

VeriCBAM strictly separates real-world reference analysis from controlled predictive benchmarking:

### 5.1 Layer A: Real-World Reference Datasets
* **EEA Industrial Reporting Database (E-PRTR / IED v16.0, Feb 2026):**
  Independent facility-level historical emissions observations ($CO_2$, $NO_x$, $SO_2$) across European heavy industry.
  > *Methodological Note:* The EEA database provides an independent reference dataset for historical baselines and operational consistency analysis; it is **not treated as ground truth for legal CBAM non-compliance**.
* **Benchmark Cohort (30 Facilities, 177 Observations):**
  Curated cohort of 15 cement plants and 15 steelworks across Germany and Europe covering 2018–2023. Across the 180 theoretical facility-year combinations ($30 \times 6$), exactly **177 observations are present**. Three facility-years are missing from the raw EEA submissions: Górażdże Cement (Poland, 2020: delayed reporting during pandemic lockdown), HeidelbergCement Schelklingen (Germany, 2023), and U.S. Steel Košice (Slovakia, 2023).
* **Copernicus Sentinel-5P (TROPOMI Level-2):**
  Tropospheric $\text{NO}_2$ and $\text{CO}$ column densities ($\text{mol/m}^2$) queried via the Copernicus Data Space Ecosystem (CDSE) API (Regulation (EU) 1159/2013). Re-framed strictly as **independent atmospheric indicators of industrial operational activity**, rather than direct measurements of facility-level $\text{CO}_2$ emissions.
* **Copernicus Sentinel-2 (MSI Level-2A):**
  20m resolution **Short-Wave Infrared (SWIR Bands 11/12)** for Normalized Hotspot Index (NHI) activity classification (not thermal infrared).
* **Global Energy Monitor (GEM) Registries:**
  Nameplate capacities, furnace models, and geocoded coordinates from the *Global Steel Plant Tracker* and *Global Cement and Concrete Tracker*.

### 5.2 Layer B: Controlled Inconsistency Benchmark
Because authentic regulatory violation labels for overseas CBAM declarations do not exist publicly during the transitional phase, a separate benchmark introduces **controlled, explicitly documented synthetic perturbations applied to real facility observations** (101 labeled cases: 30 unperturbed concordant baselines, 30 physical calcination/reduction violations, 30 abrupt historical drops, and 11 verified route misclassifications).
> *Methodological Boundary:* These perturbations are used solely to evaluate detection sensitivity and probability calibration under known conditions, and are never presented as real regulatory violations.

| Dataset Identifier | Authority / Provider | Legal Access / License | Exact Content & Role in VeriCBAM |
| :--- | :--- | :--- | :--- |
| **Copernicus Sentinel-5P (TROPOMI Level-2)** | European Space Agency (ESA) / European Commission | Free, Open & Full Data Policy (Regulation (EU) 1159/2013) | Offline & Near-Real-Time $NO_2$, $CO$, and $SO_2$ Tropospheric Vertical Column Densities. Operational activity indicator. |
| **Copernicus Sentinel-2 (MSI Level-2A)** | European Space Agency (ESA) | Free, Open & Full Data Policy | 20m resolution Short-Wave Infrared bands (B11: $1.61\mu m$, B12: $2.19\mu m$) for Normalized Hotspot Index (NHI) kiln/furnace activity tracking (SWIR, not thermal IR). |
| **European Industrial Emissions Portal (E-PRTR)** | European Environment Agency (EEA) | Open Public Data (Directive 2010/75/EU & Regulation (EC) 166/2006) | Legally verified annual emissions ($CO_2, NO_x, SO_2$) and operational activity for $>30,000$ European heavy industrial sites. Used as our **independent reference validation cohort**. |
| **Global Steel Plant Tracker (GSPT)** | Global Energy Monitor (GEM) | Creative Commons CC BY 4.0 (Open Data) | Exact geolocations, capacities, operational statuses, parent entities, and metallurgical furnace technologies for all major steel plants globally. |
| **Global Cement and Concrete Tracker** | Global Energy Monitor (GEM) | Creative Commons CC BY 4.0 (Open Data) | Precise facility coordinates, kiln types (wet/dry), clinker capacities, and operating timelines. |
| **Official DG TAXUD CBAM Communication Templates** | European Commission (DG TAXUD) | Public EU Regulatory Documentation | Official Excel/XML template structure, default emissions parameters, and calculation formulas mandated for EU customs declarations. |
| **ECMWF ERA5 Reanalysis** | Copernicus Climate Change Service (C3S) | Open Data (Copernicus License) | Planetary boundary layer height, $10m$ wind vectors ($u, v$) for atmospheric plume dispersion filtering. |

### Protocol for Acquiring Additional Real-World Data Legally:
Should expanded facility records or pilot CBAM submissions be required, the following legal and academic channels are available:
1. **German Federal Environmental Information Act (*Umweltinformationsgesetz* - UIG / Directive 2003/4/EC):** Any student or researcher at a German university has the statutory right to request environmental data held by public authorities, including the German Emissions Trading Authority (*Deutsche Emissionshandelsstelle* - DEHSt at *Umweltbundesamt*), which serves as the German Competent Authority for CBAM.
2. **Academic Institutional Outreach:** A formal university data-request letter signed by supervisor Dr. Humera Noor to industrial research institutes (e.g., *Verein Deutscher Zementwerke* - VDZ, *VDEh-Betriebsforschungsinstitut* - BFI) for anonymized benchmarking declarations.
3. **Corporate Sustainability Disclosures (CSRD / CDP):** Standardized, legally audited annual Scope 1 and Scope 2 disclosure filings published under EU CSRD rules by publicly traded steel and cement producers (ArcelorMittal, Thyssenkrupp, Salzgitter, Heidelberg Materials).

---

## 6. Experimental Design & Model Ablation Benchmark

To guarantee rigorous scientific defense, VeriCBAM does not merely showcase a functioning application. It conducts an **ablation experiment comparing five distinct models** across a validated cohort of 30 European industrial installations (15 cement, 15 steel) with verified E-PRTR reference data:

| Model ID | Model Name | Evidence Inputs Utilized | Hypothesis / Test Purpose |
| :--- | :--- | :--- | :--- |
| **Model A** | Declaration-Only Baseline | Reported declaration values compared against standard regional default averages. | Measures baseline statistical screening ability. |
| **Model B** | Stoichiometric Physical Model | Reported values evaluated strictly against mass-balance lower bounds ($E_{\min}$). | Measures how many physical impossibilities are caught by chemical engineering alone. |
| **Model C** | Satellite Activity Model | Evaluates reported operating uptime against Sentinel-5P/Sentinel-2 activity indicators. | Tests remote sensing capability in isolation. |
| **Model D** | Historical Behavioral Model | Evaluates deviation from the facility's multi-year E-PRTR historical fingerprint. | Tests longitudinal registry anomaly detection. |
| **Model E** | **VeriCBAM Multimodal Fusion** | **Fused integration of Models B + C + D with Bayesian calibration.** | **Proves whether multimodal fusion achieves superior F1-score, calibration, and lower false-positive rates.** |

### Evaluated Quantitative Metrics:
* **Precision, Recall, and F1-Score** in identifying injected and historical reporting inconsistencies.
* **False Positive Rate (FPR):** Ensuring compliant installations are not erroneously flagged.
* **Brier Score & Expected Calibration Error (ECE):** Demonstrating that an 80% risk rating corresponds to an actual 80% empirical inconsistency frequency.
* **Uncertainty Calibration:** Accuracy of predicted confidence bounds under varying atmospheric cloud cover.

---

## 7. Project Repository & File Structure

```text
VeriCBAM/
├── .github/workflows/           # Automated pytest, flake8, and data validation CI
├── config/
│   ├── cbam_taxud_rules.yaml    # Official CN codes, precursor boundaries, default values
│   └── settings.py              # Environment configuration and CDSE API credentials
├── data/
│   ├── 01_raw/
│   │   ├── gem_registries/      # Global Steel & Cement Plant Tracker original CSVs
│   │   ├── eprtr_reference/     # European Industrial Emissions Portal verified extracts
│   │   └── cbam_templates/      # Official DG TAXUD Excel/XML schemas
│   ├── 02_processed/
│   │   ├── facility_fingerprints.parquet # Multi-year historical baselines per plant
│   │   └── benchmark_cohort.parquet      # 30 curated test facilities with complete data
│   └── 03_satellite_cache/      # Cached Sentinel-5P NetCDF4 and Sentinel-2 GeoTIFF arrays
├── docs/
│   ├── methodology/
│   │   ├── 01_regulatory_scope.md        # CBAM Annex IV accounting boundaries
│   │   ├── 02_stoichiometric_models.md   # Mathematical derivations of mass-balance bounds
│   │   ├── 03_remote_sensing_physics.md  # Satellite atmospheric retrieval & SWIR proxy math
│   │   └── 04_uncertainty_propagation.md # Bayesian fusion and calibration formulas
│   ├── data/
│   │   ├── data_dictionary.md            # Variables, units, resolutions, and quality flags
│   │   └── data_provenance.md            # Official access APIs, retrieval dates, licenses
│   └── reports/                          # Bi-weekly progress reports and Capstone deliverables
├── experiments/
│   ├── configs/                 # YAML ablation experiment specifications
│   ├── notebooks/
│   │   ├── 01_cohort_selection_eda.ipynb # Quality filtering of real facilities
│   │   ├── 02_stoichiometry_validation.ipynb # Testing mass balance bounds
│   │   ├── 03_satellite_plume_processing.ipynb # Sentinel-5P/2 extraction pipeline
│   │   ├── 04_temporal_fingerprinting.ipynb # Historical anomaly detection
│   │   └── 05_ablation_benchmarking.ipynb # Running Models A through E comparison
│   └── results/                 # Evaluation metrics, confusion matrices, reliability diagrams
├── src/
│   ├── core/
│   │   ├── stoichiometry/       # First-principles mass balance solvers (Cement & Steel)
│   │   ├── remote_sensing/      # CDSE Copernicus downloader, TROPOMI & SWIR processors
│   │   ├── fingerprinting/      # Facility historical profile and anomaly detector
│   │   └── fusion/              # Deterministic Bayesian Evidence-Fusion & Risk Scorer
│   ├── document_ai/             # Pydantic declaration parser and schema validator
│   ├── agent/                   # LLM auditor orchestrator, counterfactual explainer
│   └── report/                  # PDF audit dossier builder (ReportLab/WeasyPrint)
├── web/
│   ├── app.py                   # Streamlit Interactive Audit Cockpit
│   └── components/              # Leaflet plume visualizer, risk gauges, counterfactual sliders
├── tests/                       # Unit tests for conservation of mass, API queries, and fusion
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 8. 12-Week Milestone Schedule & Sprint Plan

Aligned with Dr. Humera Noor’s Course Milestones:

```
[Oct 12] Topic Approval ──> [Oct 26] Proposal & Plan ──> [Nov 9] Sprint 1 Report ──> [Nov 23] Sprint 2 Report ──> [Dec 7] Sprint 3 Report ──> [Dec 21] Sprint 4 Report ──> [Jan 4] Final Report ──> [Jan 18] Pitch & Defense
```

### Sprint 0: Scoping & Dataset Setup (Weeks 1–3: Oct 03 – Oct 26)
* **Milestone 1 (Oct 12):** Approval of Topic Pitch with Dr. Humera Noor; Google Sheet entry.
* **Core Tasks:**
  * [COMPLETED] Ingested EEA E-PRTR v16.0 database (16 tables, 72,000+ emissions records).
  * [COMPLETED] Curated 30-facility European heavy industrial cohort (15 cement, 15 steel) and documented the 3 missing facility-years (177 total records).
  * [COMPLETED] Generated Layer B Controlled Inconsistency Benchmark (101 labeled evaluation cases).
  * [COMPLETED] Formulated chemical engineering stoichiometry models (`cement_models.py`, `steel_models.py`).
  * [COMPLETED] Built initial Streamlit decision support cockpit (`app.py`).
* **Milestone 2 (Oct 26):** Submission of Capstone Proposal Document, System Diagram, Sprint Gantt Chart, LinkedIn Post #1, and Conversation with AI log.

### Sprint 1: Chemical Bound Engine Validation & Document Parser (Weeks 4–5: Oct 27 – Nov 09)
* Comprehensive unit tests and thermodynamic boundary checks for cement and steel stoichiometry.
* Build Pydantic schema-enforced parser for official DG TAXUD CBAM Excel/XML declaration templates.
* **Milestone 3 (Nov 09):** Progress Report 1 + Individual LinkedIn Post #2.

### Sprint 2: Earth Observation Pipeline Extension & Facility Fingerprints (Weeks 6–7: Nov 10 – Nov 23)
* [OPERATIONAL] Sentinel-5P TROPOMI plume contrast client and disk caching (`copernicus_client.py`, `plume_analyzer.py`).
* Integrate Sentinel-2 SWIR Bands (B11/B12) Normalized Hotspot Index (NHI) for kiln operational state detection.
* Build longitudinal multivariate historical fingerprints from verified E-PRTR multi-year reference baselines.
* Link facility capacities and furnace models from Global Energy Monitor (GEM) trackers.
* **Milestone 4 (Nov 23):** Progress Report 2 + Individual LinkedIn Post #3.

### Sprint 3: Evidence Fusion Core & Uncertainty Calibration (Weeks 8–9: Nov 24 – Dec 07)
* [OPERATIONAL] Confidence-weighted Bayesian log-odds fusion core (`evidence_fusion.py`).
* [OPERATIONAL] Separation of Inconsistency Risk from Observational Confidence with explicit "Insufficient Evidence" state.
* Implement Monte Carlo uncertainty interval propagation and counterfactual scenario explorer.
* **Milestone 5 (Dec 07):** Progress Report 3 + Individual LinkedIn Post #4.

### Sprint 4: 5-Model Ablation Benchmark & Cockpit Refinement (Weeks 10–11: Dec 08 – Dec 21)
* Execute the 5-Model Ablation Study (Models A through E) on the 101-case controlled perturbation benchmark.
* Compute Precision, Recall, F1, ROC-AUC, PR-AUC, Brier score, and Expected Calibration Error (ECE).
* Refine Streamlit cockpit with interactive Leaflet/Mapbox plume overlays and automated audit dossier exports.
* **Milestone 6 (Dec 21):** Progress Report 4 + Individual LinkedIn Post #5.

### Sprint 5: Final Report, Video Demonstration & Defense (Weeks 12–14: Dec 22 – Jan 18)
* Final synthesis of scientific findings, limitations, and future policy implications.
* **Milestone 7 (Jan 04, 2027):** Submission of Comprehensive Final Report.
* Record 15–20 minute video presentation, live software walkthrough, and 2-minute elevator pitch video.
* **Milestone 8 (Jan 18, 2027):** Final Presentation Defense & Final LinkedIn Project Post.

---

## 8. Academic & Regulatory Reference Bibliography

Every empirical cost metric, timeline delay, baseline dataset, and stoichiometric bound utilized in VeriCBAM is grounded in the following official statutes, impact assessments, and industrial literature:

1. **European Commission (2021):** *Commission Staff Working Document: Impact Assessment Report Accompanying the document Proposal for a Regulation of the European Parliament and of the Council establishing a Carbon Border Adjustment Mechanism.* **SWD(2021) 643 final**, Brussels. [URL: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021SC0643]
   * *Key Evidence:* Section 6.6 & Annex 6 quantify MRV compliance burdens, administrative authority expenditures (€15M/year), and technical installation verification costs.

2. **European Union (2023):** *Regulation (EU) 2023/956 of the European Parliament and of the Council of 10 May 2023 establishing a carbon border adjustment mechanism.* Official Journal of the European Union, L 130/52.
   * *Key Evidence:* Articles 8 & 9 mandate independent third-party verification for actual emissions and govern on-site inspection requirements; Annex IV specifies system boundaries for clinker calcination and crude steel reduction.

3. **European Commission (2018 & 2025):**
   * *Commission Implementing Regulation (EU) 2025/2546 laying down principles and rules for the verification of emissions declarations under Regulation (EU) 2023/956.*
   * *Commission Implementing Regulation (EU) 2025/2551 laying down rules for the accreditation of verifiers under Regulation (EU) 2023/956.*
   * *Commission Implementing Regulation (EU) 2025/2547 laying down rules for the calculation of embedded emissions under Regulation (EU) 2023/956.*
   * *Commission Implementing Regulation (EU) 2018/2067 on the verification of data and on the accreditation of verifiers pursuant to Directive 2003/87/EC (Accreditation and Verification Regulation - AVR).*
   * *Key Evidence:* Establishes ISO 14065/ISO 14064-3 accreditation requirements, physical site visit rules, and documents the limited global pool of ~403 accredited verification bodies.

4. **GMK Center Industrial Metallurgy Think Tank (2024):** *CBAM Verification: Requirements, Costs and Industry Bottlenecks in the Steel Sector.* Kyiv/Brussels. [URL: https://gmk.center]
   * *Key Evidence:* Empirically documents the €50,000–€150,000+ verification fee per site visit for complex integrated metallurgical complexes (BF-BOF), the €10/t steel default value penalty differential, and verifier travel friction.

5. **European Environment Agency (EEA) (2026):** *Industrial Reporting Database: Industrial Emissions Directive (IED) 2010/75/EU and European Pollutant Release and Transfer Register (E-PRTR) Regulation (EC) No 166/2006 (Version 16.0, February 2026).* Copenhagen. [DOI: 10.2909/657ac3cb-affa-4295-a4a9-27b4f539adab]
   * *Key Evidence:* Serves as VeriCBAM's empirical validation baseline, providing verified multi-year Scope 1 emissions ($CO_2$, $NO_x$, $SO_2$) for 30 benchmark European heavy industrial facilities.

6. **ERCST (European Roundtable on Climate Change and Sustainable Transition) (2023):** *Implementation of the EU Carbon Border Adjustment Mechanism: Administrative Costs, Verification Hurdles, and International Competitiveness.* Brussels. [URL: https://ercst.org]
   * *Key Evidence:* Details operational bottlenecks in third-country data collection, customs integration, and verifier capacity constraints.

7. **OECD (2023):** *Carbon-Related Border Adjustments and Developing Country Exporters: Technical Barriers, Verification Capacity, and Trade Impacts.* OECD Trade and Environment Working Papers, OECD Publishing, Paris. [DOI: 10.1787/5jlv2348-en]
   * *Key Evidence:* Quantifies the disproportionate administrative and financial compliance friction imposed on developing nation producers lacking digitized MRV infrastructure.

8. **European Commission Joint Research Centre (JRC) (2013 & 2022):**
   * *Best Available Techniques (BAT) Reference Document for the Production of Cement, Lime and Magnesium Oxide (Industrial Emissions Directive 2010/75/EU).* JRC Reference Reports, Seville.
   * *Best Available Techniques (BAT) Reference Document for Iron and Steel Production.* JRC Reference Reports, Seville.
   * *Key Evidence:* Derives the stoichiometric calcination floor ($0.510–0.525\text{ t }CO_2/\text{t clinker}$), BAT thermal consumption ($3,000\text{ MJ/t clinker}$), and BF-BOF carbon reduction limits ($1.182\text{ t }CO_2/\text{t iron}$).

