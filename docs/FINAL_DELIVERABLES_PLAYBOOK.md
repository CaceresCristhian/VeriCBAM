# VeriCBAM — Final Capstone Deliverables Playbook
**Prepared for Progress Updates 2 & 3 (Nov–Dec 2026) leading to Final Submission (Jan 04, 2027)**

* **Student:** Cristhian David Cáceres Mateus (ID: 93515346)
* **Program:** M.Sc. in Data Science — University of Europe for Applied Sciences (Potsdam Campus)
* **Supervisor:** Dr. Humera Noor
* **Live Cloud App:** https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/
* **GitHub Repository:** https://github.com/CaceresCristhian/VeriCBAM

---

## 1. Presentation Deck Outline (12-Slide Executive & Technical Structure)

| Slide | Title | Core Visual / Component | Key Talking Points |
| :---: | :--- | :--- | :--- |
| **01** | **Title & Executive Value Proposition** | VeriCBAM Logo + Live App QR/Link | Pre-audit decision support for EU CBAM (Regulation 2023/956): screening heavy industrial declarations before commissioning costly on-site audits. |
| **02** | **The CBAM Enforcement Bottleneck** | EU Border Map + Cost of On-Site Audits | Tens of thousands of cement & steel import declarations enter definitive financial enforcement in 2026. Manual spreadsheets are unverified; universal site audits are impossible. |
| **03** | **Why Naive Approaches Fail** | Stoichiometric Blind Spot Formula ($\delta^* \approx 55.6\%$) + Sentinel-5P Cloud Limits | Stoichiometric floors evaluated against nameplate capacity miss 10–30% fraud; coarse Sentinel-5P $\text{NO}_2$ alone gives 96.6% false alarms (ROC-AUC 0.518). |
| **04** | **The VeriCBAM 6-Stream Architecture** | Multimodal Architecture Diagram | Fuses (1) Thermodynamic Mass Balance, (2) Longitudinal E-PRTR Drift, (3) $\text{NO}_x/\text{CO}_2$ Ratio, (4) Sentinel-5P $\text{NO}_2$, (5) Landsat 30m / VIIRS 375m Thermal IR, (6) VHR Rail-Yard Freight. |
| **05** | **First-Principles Thermodynamic Floors** | Cement Calcination & Steel Reduction Equations + Gas-Export Boundary Fix | $\text{CaCO}_3 \rightarrow \text{CaO} + \text{CO}_2$ ($0.526\text{ t/t}$) and $\text{Fe}_2\text{O}_3$ reduction ($1.182\text{ t/t}$). Explains the `stoich_applicable = False` fix for off-site blast furnace gas export. |
| **06** | **Stage 2 Multi-Sensor Satellite EO** | Visual Proof Grid: Linz BF-BOF vs. GMHütte Scrap-EAF vs. Alcanar Cement | 30m Landsat TIRS ($\Delta T$ up to $+27.0^\circ\text{C}$), 375m VIIRS active operating months ($\rho = +0.778, p = 0.0010$), and VHR rail siding contrast achieve **100% BF-BOF vs. EAF route separation**. |
| **07** | **White-Box Bayesian Log-Odds & Supervised Triage** | Dual-Stage Decision Flow (`Model E2` + `Model E3`) | Supervised 5-Fold `GroupKFold` Logistic Triage (`Model E3`) prioritizes port queues ($2.71\times$ lift); White-Box Bayesian Log-Odds (`Model E2`) builds court-defensible audit dossiers with an explicit `<50%` confidence abstention gate. |
| **08** | **Empirical Benchmark Results (325 Cases)** | Comparative ROC-AUC & Recall@10% FPR Table | 177 real E-PRTR facility-years + 148 graded anomalies ($5\%\text{--}50\%$). Stage 2 Satellite (`Model C2`) achieves **ROC-AUC 0.966** (Recall@10% FPR = **92.5%**); Bayesian `Model E2` reaches **0.908** with **0.128 Brier error**. |
| **09** | **Auditing External Third-Country Suppliers** | Zero-History Non-EU Workflow Diagram | How Option B in Tab 1 audits overseas plants (Turkey, Morocco, India, China) with **zero prior EU registry history** using GPS coordinates, declared production/$\text{CO}_2$, and global satellite thermal/logistics data. |
| **10** | **Live Demo: Tab 1 Quick Audit & 1-Click PDF Dossier** | Screenshot of Tab 1 + Generated 1-Page PDF Dossier | 30-second workflow for verifiers (DNV, TÜV, Bureau Veritas) and authorities (DEHSt) to screen a declaration and export a signed 1-page Pre-Audit Dossier PDF. |
| **11** | **Engineering Quality & Reproducibility** | GitHub CI / `pytest` 32/32 Passing Badge | Modular Python 3.12 engine (`src/`), 32/32 automated unit & integration tests, strict `GroupKFold` anti-leakage validation, and live Streamlit Cloud deployment. |
| **12** | **Industry Adoption Roadmap & Stage 3 Horizon** | Sentinel-1 C-Band SAR + 3D Stereo Volumetrics | Current outreach to EU verifiers & importers; next-phase expansion to all-weather Sentinel-1 SAR radar and 3D stockpile volumetrics. |

---

## 2. Long-Form Walkthrough Video Script (15–20 Minutes)

* **00:00 – 02:30 | Part 1: Problem Statement & Real-World CBAM Regulatory Context**
  * Introduce EU CBAM Regulation (EU) 2023/956 and Implementing Regulation (EU) 2025/2546.
  * Explain why accredited verifiers (DNV, TÜV, Bureau Veritas) and national authorities (DEHSt) need a pre-audit screening filter to triage declarations and catch carbon under-reporting or route greenwashing (claiming Scrap-EAF on a blast furnace plant).
* **02:30 – 06:00 | Part 2: First-Principles Physics & The Stoichiometric Blind Spot**
  * Walkthrough of `src/core/stoichiometry/cement_models.py` and `steel_models.py`.
  * Demonstrate the mathematical blind spot ($\delta^* \approx 55.6\%$) and why we had to solve the off-site blast furnace gas export boundary problem (`stoich_applicable = False`).
* **06:00 – 10:30 | Part 3: Stage 1 vs. Stage 2 Multi-Sensor Satellite Earth Observation**
  * Show why Sentinel-5P $\text{NO}_2$ alone fails as a direct meter (coarse $5.5 \times 3.5\text{ km}$ footprint + winter clouds).
  * Show the breakthrough in **Stage 2 Multi-Sensor EO** (`src/satellite/multisensor_client.py`): combining 30m USGS Landsat-8/9 thermal core anomalies ($\Delta T$), 375m NASA FIRMS VIIRS daily kiln/furnace operating timelines, and Planet VHR rail-yard freight contrast across all 30 European plants.
* **10:30 – 14:30 | Part 4: Live Cockpit Walkthrough & 30-Second Quick Audit (Tab 1)**
  * Open the live app (`https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/`).
  * **Demo 1 (Option A — Pre-Loaded EU Plant):** Audit an authentic compliant plant vs. a 35% under-reporting simulation and download the **1-Page PDF Pre-Audit Dossier**.
  * **Demo 2 (Option B — External Non-EU Exporter):** Audit an overseas integrated steelworks with zero EU reporting history using only satellite thermal/freight observations + stoichiometry.
  * **Demo 3 (Tabs 2–8):** Briefly tour the Geospatial Map, Multi-Sensor Visual Cards, Bayesian Log-Odds Waterfall, and 325-Case Empirical Benchmark tab.
* **14:30 – 17:30 | Part 5: Codebase Architecture, 32/32 Automated Tests & Industry Next Steps**
  * Show the clean repository layout, `GroupKFold` cross-validation without facility leakage, and `pytest` passing 32/32 tests.

---

## 3. Elevator Pitch Video Script (1–2 Minutes / ~220 Words)

> **[00:00 – 00:20 | The Hook]**  
> "Starting in 2026, the European Union's Carbon Border Adjustment Mechanism—CBAM—puts a hard carbon price on every tonne of cement and steel imported into Europe. But there is a massive enforcement bottleneck: thousands of overseas factories submit self-reported emissions spreadsheets, and regulators cannot send physical inspectors to every plant on Earth."
>
> **[00:20 – 00:50 | The Solution]**  
> "That's why I built **VeriCBAM**—an open-source, physics-and-satellite decision-support copilot for CBAM verifiers and customs authorities. Instead of trusting a spreadsheet or a black-box AI guess, VeriCBAM cross-examines every declaration across six independent evidence streams: chemical mass-balance floors for cement calcination and iron ore reduction, historical registries, and multi-sensor satellite Earth observation—including 30-meter Landsat thermal infrared kiln temperatures, daily VIIRS furnace hotspots, and optical freight rail-yard activity."
>
> **[00:50 – 01:20 | The Proof & Impact]**  
> "Tested across 30 industrial installations and a 325-case benchmark, our Stage 2 multi-sensor satellite engine achieves a **0.966 ROC-AUC** and **100% separation** between primary blast furnaces and low-carbon electric arc furnaces—even for external third-country exporters with zero prior EU reporting history."
>
> **[01:20 – 01:45 | Live Call to Action]**  
> "Best of all, VeriCBAM is live on the cloud today. In Tab 1, any verifier, importer, or customs officer can screen a facility in 30 seconds and export a 1-page legally structured Pre-Audit Dossier PDF with one click. Try the live platform today."

---

## 4. LinkedIn Launch Post Draft (Ready for Final Deliverable)

**Headline:** Can you verify a factory's carbon emissions from space before signing an EU CBAM certificate? 🛰️🏭⚖️

As the EU Carbon Border Adjustment Mechanism (**CBAM**, Regulation 2023/956) enters definitive financial enforcement, accredited verifiers, importers, and customs authorities face a critical challenge: **how do you screen thousands of self-reported industrial emissions declarations before commissioning costly on-site audits?**

Over the past semester at the **University of Europe for Applied Sciences (Potsdam)**, I developed **VeriCBAM**—an explainable multimodal decision-support platform for screening cement and steel emissions declarations.

🔍 **What VeriCBAM does in 30 seconds:**
1. **First-Principles Thermodynamics:** Tests declared intensities against stoichiometric calcination ($\text{CaCO}_3 \rightarrow \text{CaO} + \text{CO}_2$) and carbothermic reduction floors while accounting for off-site process gas exports.
2. **Multi-Sensor Satellite Earth Observation:** Fuses 30m **USGS Landsat-8/9 Thermal Infrared** kiln/furnace anomalies ($\Delta T$ up to $+27^\circ\text{C}$), 375m **NASA FIRMS VIIRS** active operating calendars, **Copernicus Sentinel-5P** $\text{NO}_2$, and **VHR freight rail-yard** activity.
3. **Zero-History External Supplier Screening:** Audits third-country exporting plants with zero prior EU registry history using satellite operational signatures + stoichiometry (**ROC-AUC 0.966**, **92.5% Recall @ 10% FPR** across our 325-case benchmark).
4. **1-Click Pre-Audit Dossier PDF:** Exports a transparent, white-box Bayesian evidence dossier mapped directly to Implementing Regulation (EU) 2025/2546.

🚀 **Try the 30-Second Quick Audit live (no installation required):**  
👉 Live Cloud App: https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/  
💻 Open-Source GitHub: https://github.com/CaceresCristhian/VeriCBAM  

If you work in **CBAM compliance, industrial decarbonization, accredited GHG verification (DNV, TÜV, Bureau Veritas), or Earth Observation**, I would love your feedback!

#CBAM #CarbonBorderAdjustmentMechanism #DataScience #EarthObservation #Decarbonization #GreenSteel #Cement #ClimateTech #EUETS #ExplainableAI
