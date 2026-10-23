# VeriCBAM: Master Reference & Source Verification Guide
**Full Title:** *VeriCBAM: Multimodal Evidence Fusion & Decision Support for EU Carbon Border Adjustment Mechanism (CBAM) Emissions Consistency Assessment*  
**Document Purpose:** Comprehensive Theoretical, Legal, Regulatory, Institutional, Industrial, and Architectural Reference Guide designed for **Google NotebookLM Source Grounding** and Academic/Regulatory Verification.  
**Author:** Cristhian David Cáceres Mateus (M.Sc. Data Science, University of Europe for Applied Sciences, Berlin Campus)  
**Academic Supervisor:** Dr. Humera Noor  
**Date:** October 2026 | **Version:** 2.1 (Post-Review Verified Edition)  
**Repository:** https://github.com/CaceresCristhian/VeriCBAM  

---

## 1. Executive Summary & The Real-World Problem

### 1.1 The Operational Bottleneck in CBAM Definitive Enforcement
On **1 January 2026**, the European Union's **Carbon Border Adjustment Mechanism (CBAM)** exited its transitional reporting-only phase (2023–2025) and entered its **definitive financial enforcement regime**. Under **Regulation (EU) 2023/956**, EU importers (*Authorised CBAM Declarants*) importing carbon-intensive commodities—specifically **Iron & Steel, Cement, Aluminium, Fertilisers, Electricity, and Hydrogen**—must surrender CBAM certificates corresponding to the verified embedded greenhouse gas emissions ($t\text{CO}_2e$) of their imported goods, priced at the weekly average EU Emissions Trading System (EU ETS) allowance auction price (typically €65–€90+ per metric tonne of $\text{CO}_2$).

While the **Omnibus I Simplification Regulation (EU) 2025/2083** introduced a *de minimis* threshold exempting small importers bringing in less than **50 metric tonnes of mass per year**, approximately **99% of total embedded industrial emissions** remain strictly subject to mandatory third-party verification and financial surrender.

### 1.2 The Three Core Verification Challenges
1. **Severe Information Asymmetry Across Global Supply Chains:**  
   Unlike intra-EU installations that have been monitored for two decades under the EU ETS Monitoring and Reporting Regulation (**Regulation (EU) 2018/2066**), CBAM regulates production occurring at thousands of overseas industrial installations in third countries outside direct EU jurisdiction. Declarations rely heavily on operator self-reporting of fuel consumption, raw material calcination, production volumes, and process boundaries.
2. **Scarce Verification Capacity & High Inspection Costs:**  
   Under **Commission Implementing Regulation (EU) 2025/2546** and **Commission Delegated Regulation (EU) 2025/2551**, physical on-site installation visits are the regulatory default for initial verification, and declarations must satisfy a **5% materiality threshold at the goods (CN code) level**. However, accredited verification bodies face severe bottlenecks in global auditor manpower, and physical overseas site inspections of complex integrated steelworks or cement kilns incur substantial travel and engineering audit costs.
3. **Three Primary Technical Evasion / Inconsistency Vectors:**
   - **Vector A — Selective Quantitative Understatement:** Under-reporting annual fuel or process $\text{CO}_2$ emissions by 10%–50% to reduce certificate surrender liability while maintaining normal physical output.
   - **Vector B — Stoichiometric Floor & System Boundary Manipulation:** Reporting specific embedded emissions below the chemical conservation-of-mass limit required to reduce iron ore or calcine limestone, or exporting carbon-rich blast furnace off-gases across legal fence lines to adjacent power plants without accounting for them in the product boundary.
   - **Vector C — Process Route Misclassification ("Greenwashing"):** Declaring that high-carbon primary steel (produced via an integrated Blast Furnace – Basic Oxygen Furnace, BF-BOF, $\approx 1.85\text{ t CO}_2/\text{t}$) was manufactured via a low-carbon secondary route (Scrap – Electric Arc Furnace, Scrap-EAF, $\approx 0.08\text{ t CO}_2/\text{t}$ direct Scope 1).

### 1.3 What VeriCBAM Is (and What It Is Not)
**VeriCBAM** is an open-source, white-box **Multimodal Verification Decision-Support and Triage System**. It fuses chemical engineering stoichiometry, longitudinal multi-pollutant industrial registries (EEA E-PRTR), verified plant technology trackers (Global Energy Monitor), and auxiliary satellite remote sensing (ESA Copernicus Sentinel-5P) to rank incoming declarations by inconsistency risk and generate auditable inspection dossiers.

> **Important Scope Qualification:** VeriCBAM is a **pre-audit screening and triage co-pilot**, *not* an automated legal compliance determiner. Because public third-country CBAM declarations are confidential, VeriCBAM's empirical benchmark uses European facility-level Scope 1 emissions from the EEA E-PRTR database as an authentic physical proxy rather than product-level CBAM embedded emissions. Final legal determinations always rest with human accredited verifiers and National Competent Authorities.

---

## 2. How VeriCBAM Supports Professionals in the Field

VeriCBAM is architected around a **Dual-Stage Operational Workflow** tailored to three distinct professional groups operating in the CBAM ecosystem:

### 2.1 National Competent Authorities (NCAs) & Customs Authorities
- **Who They Are:** National enforcement agencies in each EU Member State (e.g., *DEHSt/UBA* in Germany, *DGEC* in France, *NEa* in the Netherlands, *KOBiZE* in Poland) and European Commission *DG TAXUD* / *DG CLIMA* analysts reviewing annual CBAM declarations in the CBAM Transitional/Definitive Registry.
- **Their Challenge:** Reviewing thousands of complex installation files under tight statutory deadlines with limited desk-review staff.
- **How VeriCBAM Helps Them (Stage 1 — High-Throughput Triage via Model E2):**
  - Ranks all incoming declarations using a supervised, facility-grouped Logistic Regression risk score (**Model E2**, $\text{ROC-AUC} = 0.9643$).
  - Under a simulated customs resource constraint where authorities can only inspect the **top 20% highest-risk declarations**, VeriCBAM achieves **100.0% Precision (2.71x lift over random sampling)** and captures **54.2% of all non-compliant declarations** (rising to **75.0% recall** at a 30% inspection budget).

### 2.2 Accredited CBAM Verification Bodies & Lead Auditors
- **Who They Are:** Independent engineering verification bodies accredited under **Commission Delegated Regulation (EU) 2025/2551** and **ISO 14064-3** (e.g., *TÜV SÜD, DNV, SGS, Bureau Veritas, LRQA, GUTcert, TÜV Rheinland*).
- **Their Challenge:** Performing mandatory risk analyses under **Implementing Regulation (EU) 2025/2546** to decide whether a site visit can be waived or must be escalated, and knowing exactly *which* meters, invoices, or mass balances to audit on-site.
- **How VeriCBAM Helps Them (Stage 2 — Explainable Audit Dossier via Model E1):**
  - Evaluates each facility using **Model E1 (Expert Weighted Log-Odds Bayesian Fusion)**, which achieves a **near-zero Authentic False Positive Rate of 0.56%** (only 1 false alarm across 177 real historical plant-years) and $\text{ROC-AUC} = 0.8935$.
  - Produces a **100% transparent, white-box Audit Dossier** showing exact chemical mass-balance floors, leave-one-year-out historical Z-scores, $\text{NO}_x/\text{CO}_2$ combustion ratio drift, and an explicit `Insufficient Evidence` gate when satellite or capacity data is obscured.
  - Instructs the lead verifier on exact evidentiary artifacts to demand (e.g., *"Request raw meal $\text{CaCO}_3$ lab titration logs"*, *"Audit blast furnace off-gas export custody-transfer meters to external power station"*, or *"Verify electricity bills and scrap purchase invoices for claimed EAF route"*).

### 2.3 EU Authorised CBAM Declarants (Importers) & Non-EU Industrial Exporters
- **Who They Are:** European steel/cement trading houses, automotive and construction supply-chain compliance officers, and overseas mill operators (in Turkey, India, China, Brazil, Ukraine, South Korea, etc.).
- **Their Challenge:** Submitting inaccurate supplier data exposes EU importers to severe financial penalties under **Article 26 of Regulation (EU) 2023/956** (penalties of €100+ per tonne of unreported $\text{CO}_2$, indexed to inflation, without releasing the obligation to surrender certificates).
- **How VeriCBAM Helps Them (Tab 4 — Zero-History Supplier Plausibility Pre-Check):**
  - Provides a standalone calculator requiring *zero* historical database records or satellite overpasses.
  - An importer enters four numbers from a supplier's communication sheet: **Sector, Claimed Production Route, Nameplate Capacity, Declared Production, and Declared Direct $\text{CO}_2$**.
  - Instantly checks whether the supplier's declared intensity violates chemical stoichiometry or indicates a misclassified production route before the importer signs the legal customs declaration.

---

## 3. Complete Legal & Regulatory Framework (Primary Sources for NotebookLM)

All regulatory logic in VeriCBAM is grounded in official European Union legislation published in the *Official Journal of the European Union (EUR-Lex)* and international GHG standards.

### 3.1 Core EU CBAM Legislation
1. **Regulation (EU) 2023/956 of the European Parliament and of the Council of 10 May 2023 establishing a carbon border adjustment mechanism**  
   - *Role in VeriCBAM:* Primary founding law establishing CBAM scope (Annex I CN codes for cement, iron & steel, aluminium, fertilisers, electricity, hydrogen), calculation of embedded emissions (Annex IV), accreditation of verifiers (Article 18), declaration obligations (Article 6), verification mandate (Article 8), and penalties (Article 26).  
   - *Official EUR-Lex ELI:* http://data.europa.eu/eli/reg/2023/956/oj

2. **Commission Implementing Regulation (EU) 2023/1773 of 17 August 2023 laying down the rules for the application of Regulation (EU) 2023/956 as regards reporting obligations during the transitional period**  
   - *Role in VeriCBAM:* Defines the transitional reporting methodology (Oct 2023 – Dec 2025), installation boundary definitions, and communication templates between third-country operators and EU declarants.  
   - *Official EUR-Lex ELI:* http://data.europa.eu/eli/reg_impl/2023/1773/oj

3. **Commission Implementing Regulation (EU) 2025/2546 of 10 December 2025 on the application of the principles for verification of declared embedded emissions pursuant to Regulation (EU) 2023/956**  
   - *Role in VeriCBAM:* Governs definitive-phase verification rules starting 2026. **Article 5** establishes the **5% materiality threshold** defined at the *goods (CN code) level*. Establishes strategic analysis, risk analysis, verification plan, physical site visits as the default requirement, and specific conditions under which site visits may be waived.  
   - *Official EUR-Lex ELI:* http://data.europa.eu/eli/reg_impl/2025/2546/oj

4. **Commission Implementing Regulation (EU) 2025/2547 of 10 December 2025 laying down rules for the calculation, monitoring, and reporting of embedded emissions in goods imported into the customs territory of the Union**  
   - *Role in VeriCBAM:* Defines production processes, system boundaries, direct vs. indirect emissions, precursor goods accounting (e.g., cement clinker into cement; pig iron/DRI/ferro-alloys into crude steel), and rules for transferred $\text{CO}_2$ and waste gases (blast furnace gas, coke oven gas, converter gas).  
   - *Official EUR-Lex ELI:* http://data.europa.eu/eli/reg_impl/2025/2547/oj

5. **Commission Delegated Regulation (EU) 2025/2551 of 10 December 2025 supplementing Regulation (EU) 2023/956 with requirements for the accreditation, control, and oversight of verifiers**  
   - *Role in VeriCBAM:* Establishes legal accreditation requirements for CBAM verifiers by National Accreditation Bodies (NABs), verifier competence criteria, impartiality rules, and administrative oversight.  
   - *Official EUR-Lex ELI:* http://data.europa.eu/eli/reg_del/2025/2551/oj

6. **Regulation (EU) 2025/2083 of the European Parliament and of the Council (2025 Omnibus I CBAM Simplification Package)**  
   - *Role in VeriCBAM:* Replaces the legacy €150 consignment exemption with a cumulative **50-tonne annual mass *de minimis* threshold** for importers of iron/steel, aluminium, cement, and fertilisers, simplifying administrative burden for SMEs while retaining ~99% of embedded emissions under full CBAM compliance.  
   - *Official EUR-Lex ELI:* http://data.europa.eu/eli/reg/2025/2083/oj

### 3.2 Related EU Environmental & Industrial Regulations
7. **Directive 2003/87/EC (EU Emissions Trading System Directive):** Establishes the EU carbon market and benchmark free allocation rules to which CBAM mirrors its pricing and phase-out schedule. ELI: http://data.europa.eu/eli/dir/2003/87/oj
8. **Commission Implementing Regulation (EU) 2018/2066 (Monitoring and Reporting Regulation - MRR):** Source of standard calculation tiers, mass-balance methodologies, and stoichiometric emission factors for clinker and iron/steel. ELI: http://data.europa.eu/eli/reg_impl/2018/2066/oj
9. **Commission Implementing Regulation (EU) 2018/2067 (Accreditation and Verification Regulation - AVR):** Foundation for EU ETS verifier accreditation and risk-based verification auditing. ELI: http://data.europa.eu/eli/reg_impl/2018/2067/oj
10. **Directive 2010/75/EU (Industrial Emissions Directive - IED) & Regulation (EC) No 166/2006 / Regulation (EU) 2024/1244 (E-PRTR / Industrial Emissions Portal Regulation):** Legal basis for mandatory annual public reporting of facility-level air releases ($\text{CO}_2, \text{NO}_x, \text{SO}_x$) across European industrial installations used in VeriCBAM Layer A. ELI: http://data.europa.eu/eli/dir/2010/75/oj
11. **Commission Implementing Decision 2013/163/EU (BAT Conclusions for Cement, Lime and Magnesium Oxide - CLM BREF):** Official EU Best Available Techniques reference establishing thermal energy minimums ($2.9\text{--}3.3\text{ GJ/t}$ clinker) for dry preheater/precalciner kilns. ELI: http://data.europa.eu/eli/dec_impl/2013/163/oj
12. **Commission Implementing Decision 2012/135/EU (BAT Conclusions for Iron and Steel Production - IS BREF):** Official EU BAT reference establishing reducing agent consumption and process gas balances in sinter, coking, blast furnace, and BOF/EAF steelmaking. ELI: http://data.europa.eu/eli/dec_impl/2012/135/oj

### 3.3 International Scientific & Auditing Standards
13. **2006 IPCC Guidelines for National Greenhouse Gas Inventories (and 2019 Refinement), Volume 3: Industrial Processes and Product Use (IPPU):**
    - *Chapter 2 (Mineral Industry):* Defines the stoichiometric calcination factor of $0.51\text{--}0.525\text{ t CO}_2/\text{t}$ clinker ($0.7848\text{ t CO}_2/\text{t CaO}$).
    - *Chapter 4 (Metal Industry):* Defines carbon mass balances for BF-BOF, DRI, and EAF steelmaking.
    - *URL:* https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol3.html
14. **ISO 14064-1:2018 & ISO 14064-3:2019:** International standards for quantification, reporting, and verification of greenhouse gas assertions.
15. **EN 14181 & ISO 14164:** European and international standards for quality assurance of Automated Measuring Systems (AMS / CEMS) on industrial smokestacks (defining $\pm 2.5\%\text{--}5.0\%$ instrumental uncertainty bounds).

---

## 4. Scientific Theory & Mathematical Formulations

VeriCBAM integrates five mathematical and physical pillars:

### 4.1 Pillar 1: Chemical Engineering Stoichiometry (Conservation of Mass)
Rather than treating emissions as an arbitrary statistical variable, VeriCBAM enforces route-specific chemical lower bounds derived from atomic weights and EU BREF Best Available Techniques (BAT).

#### A. Cement Clinker Calcination & Kiln Combustion Floor
In any rotary cement kiln, limestone ($\text{CaCO}_3$, molar mass $100.0869\text{ g/mol}$) undergoes endothermic thermal decomposition at $\approx 900^\circ\text{C}$ to form calcium oxide ($\text{CaO}$, molar mass $56.0774\text{ g/mol}$) and carbon dioxide ($\text{CO}_2$, molar mass $44.0095\text{ g/mol}$):
$$\text{CaCO}_3 \xrightarrow{\Delta H = +178\text{ kJ/mol}} \text{CaO} + \text{CO}_2 \uparrow$$

- **Exact Stoichiometric Mass Ratio:**
  $$\gamma_{\text{CaO}} = \frac{M_{\text{CO}_2}}{M_{\text{CaO}}} = \frac{44.0095}{56.0774} = 0.78480\text{ t CO}_2\text{ per tonne of CaO}$$
- **Process Calcination Bound:** Standard Portland cement clinker requires a mass fraction $f_{\text{CaO}} \in [0.63, 0.67]$ (central $0.65$) to form alite ($\text{C}_3\text{S}$) and belite ($\text{C}_2\text{S}$), plus Cement Kiln Dust (CKD) calcination ($\approx 2\%$). Even at the conservative lower bound ($f_{\text{CaO}} = 0.63$), pure chemical calcination releases:
  $$EF_{\text{calc, min}} = 0.63 \times 0.78480 = 0.4944 \approx 0.495\text{ t CO}_2/\text{t clinker} \quad (\text{Central: } 0.525\text{ t CO}_2/\text{t clinker})$$
- **BAT Thermal Kiln Fuel Bound:** Driving the endothermic calcination reaction and sintering clinker at $1,450^\circ\text{C}$ in a state-of-the-art 5-stage cyclone preheater/precalciner kiln requires $\ge 2.9\text{--}3.3\text{ GJ/t clinker}$ (EU CLM BREF 2013). Under standard industrial fuel mixes, kiln combustion contributes a conservative minimum of:
  $$EF_{\text{thermal, min}} = 0.275\text{ t CO}_2/\text{t clinker}$$
- **Combined Engineering Lower Bound for Cement Clinker:**
  $$E_{\text{floor, cement}} = P_{\text{clinker}} \times (0.495 + 0.275) - E_{\text{CCUS, verified}} = 0.770\text{ t CO}_2/\text{t clinker} - E_{\text{CCUS, verified}}$$
  *(For blended finished cements, $P_{\text{clinker}} = P_{\text{cement}} \times r_{\text{clinker/cement}}$, where $r \in [0.65, 0.95]$).*

#### B. Primary & Secondary Iron & Steelmaking Floors
Steelmaking emissions depend fundamentally on the physical reduction route:
1. **Integrated Blast Furnace – Basic Oxygen Furnace (BF-BOF):**
   Hematite iron ore ($\text{Fe}_2\text{O}_3$, molar mass $159.688\text{ g/mol}$) is reduced by carbon/coke ($3\text{C}$, $36.032\text{ g/mol}$) to produce liquid hot metal ($2\text{Fe}$, $111.690\text{ g/mol}$) and $\text{CO}/\text{CO}_2$ ($3\text{CO}_2 = 132.029\text{ g/mol}$):
   $$\text{Fe}_2\text{O}_3 + 3\text{C} \rightarrow 2\text{Fe} + 3\text{CO}, \qquad \text{Fe}_2\text{O}_3 + 3\text{CO} \rightarrow 2\text{Fe} + 3\text{CO}_2$$
   - **Chemical Reduction Minimum:** $\frac{3 \times 44.0095}{2 \times 55.845} = 1.1821\text{ t CO}_2/\text{t Fe}$.
   - **Route-Specific Engineering Lower Bound (accounting for blast furnace thermal reserve zone equilibrium, sintering/coking, and up to 15%–20% scrap charge dilution in the LD/BOF converter):**
     $$EF_{\text{floor, BF-BOF}} = 1.350\text{ t CO}_2/\text{t crude steel} \quad (\text{Typical European average: } 1.75\text{--}1.95\text{ t CO}_2/\text{t})$$
2. **Direct Reduced Iron – Electric Arc Furnace (DRI-EAF, Natural Gas Shaft):**
   $$\text{Fe}_2\text{O}_3 + 3\text{H}_2 \rightarrow 2\text{Fe} + 3\text{H}_2\text{O}, \qquad \text{Fe}_2\text{O}_3 + 3\text{CO} \rightarrow 2\text{Fe} + 3\text{CO}_2$$
   $$EF_{\text{floor, DRI-EAF}} = 0.550\text{ t CO}_2/\text{t crude steel (Direct Scope 1)}$$
3. **Secondary Scrap – Electric Arc Furnace (Scrap-EAF):**
   No iron ore reduction occurs; direct Scope 1 emissions derive solely from graphite electrode oxidation ($\approx 1.5\text{--}3\text{ kg/t}$), oxy-fuel burners, and slag foaming carbon:
   $$EF_{\text{floor, Scrap-EAF}} = 0.040\text{ t CO}_2/\text{t crude steel (Direct Scope 1)}$$

#### C. Conservative Capacity Proxy & Transferred Process Gas Boundary Rule
When only nameplate capacity $C_{\text{nameplate}}$ is known from external registries (rather than audited production), VeriCBAM evaluates the conservative floor at **minimum plausible industrial utilization ($\eta_{\min} = 0.50$)**:
$$E_{\text{floor, conservative}} = C_{\text{nameplate}} \times 0.50 \times EF_{\text{floor, route}}$$
Furthermore, if an integrated steelworks exports its blast furnace gas (BFG) across the installation perimeter to a third-party utility power station registered under a separate E-PRTR ID (verified for 5 cohort steelworks: *ArcelorMittal Bremen, ArcelorMittal Eisenhüttenstadt, Acciaierie d'Italia Taranto, HKM Duisburg, and Tata Steel IJmuiden*), VeriCBAM sets `stoich_applicable = False` and **abstains** from firing a false physical violation on stack-only Scope 1 totals.

---

### 4.2 Pillar 2: Multi-Pollutant Co-Emission Ratio ($\text{NO}_x/\text{CO}_2$)
High-temperature kilns and furnaces generate nitrogen oxides ($\text{NO}_x$) alongside $\text{CO}_2$. Because $\text{NO}_x$ is regulated locally under the EU Industrial Emissions Directive (Directive 2010/75/EU) via independent environmental permits, operators attempting to under-report $\text{CO}_2$ for carbon accounting often fail to proportionately adjust their reported $\text{NO}_x$ releases.

For facility $i$ in target year $t$, VeriCBAM computes the **leave-one-year-out** baseline median ratio $R_{i, -t} = \text{Median}_{s \neq t}(E_{\text{NO}_x, i, s} / E_{\text{CO}_2, i, s})$ and robust scale $\sigma_{R, i, -t}$. An abnormally elevated observed ratio $R_{i, t} \gg R_{i, -t}$ indicates that declared $\text{CO}_2$ dropped without a corresponding reduction in physical combustion activity.

---

### 4.3 Pillar 3: Longitudinal Historical Trajectory (One-Sided Pooled MAD Z-Score)
For facility $i$ in evaluation year $t$, let $M_{i, -t} = \text{Median}_{s \neq t}(\ln E_{\text{CO}_2, i, s})$ be the leave-one-year-out historical log-median. Across all 177 authentic facility-years in the 30-plant cohort, the pooled Median Absolute Deviation is:
$$\sigma_{\text{pooled}} = 1.4826 \times \text{Median}_{i, t}\left|\ln E_{\text{CO}_2, i, t} - M_{i, -t}\right| = 0.0911 \quad (\approx 9.1\%\text{ typical annual operational swing})$$
The one-sided historical drop Z-score is:
$$z_{\text{drop}, i, t} = \max\left(0, -\frac{\ln E_{\text{declared}, i, t} - M_{i, -t}}{\sigma_{\text{pooled}}}\right)$$
Using $\max(0, -z)$ ensures that legitimate production expansions ($E_{\text{declared}} > M_{i, -t}$) receive $z_{\text{drop}} = 0$ and are never penalized as fraud.

---

### 4.4 Pillar 4: Orbital Earth Observation (Sentinel-5P TROPOMI $\text{NO}_2$) & Its Scientific Limits
VeriCBAM ingests authentic Level-2 tropospheric $\text{NO}_2$ vertical column density granules (`S5P_L2__NO2____`) from the **European Space Agency (ESA) Copernicus Sentinel-5P** satellite via Microsoft Planetary Computer STAC and the Copernicus Data Space Ecosystem (CDSE).
- **Quality Filtering:** Only clear-sky pixels with `qa_value >= 0.50` are accepted. Zero synthetic satellite fallback is permitted; if fewer than 3 valid overpasses exist, the stream abstains.
- **Spatial Plume Contrast:** Compares mean column density within a $5\text{ km}$ target radius ($\bar{V}_{\text{target}}$) against a $15\text{--}30\text{ km}$ regional background annulus ($\bar{V}_{\text{bg}}$):
  $$z_{\text{sat}} = \frac{\bar{V}_{\text{target}} - \bar{V}_{\text{bg}}}{1.4826 \times \text{MAD}_{\text{bg}}}$$
- **Documented Negative / Inconclusive Empirical Finding:** Cross-sectional analysis across 28 facilities ($\rho = 0.198, p = 0.312$) and multi-year 2019–2023 longitudinal analysis across German cement kilns (mean within-plant Spearman $\rho = -0.100$) demonstrate that coarse $5.5 \times 3.5\text{ km}^2$ orbital $\text{NO}_2$ columns do not correlate reliably with annual $\text{CO}_2$ variance. Consequently, satellite evidence is restricted to a low-weight auxiliary stream ($w_{\text{sat}} = 1.0$) modulated by cloud confidence $C_{\text{sat}} = \max(0, 1 - f_{\text{cloud}})$.

---

### 4.5 Pillar 5: Multimodal Fusion Architectures (Model E1 & Model E2)

#### Model E1: Expert Weighted Log-Odds Bayesian Fusion (White-Box Audit Engine)
Updates a baseline prior probability of material inconsistency $P(H) = 0.08$ ($\operatorname{logit} P(H) = -2.4423$) across $M=6$ evidence streams:
$$\operatorname{logit} P(H \mid E) = \operatorname{logit} P(H) + \sum_{k=1}^{6} w_k \cdot C_k \cdot \ln(\operatorname{LR}_k)$$
- **Stream Reliability Weights ($w_k$):**
  1. `Technology_Route_Match` ($w = 2.00$): Flags BF-BOF installations claiming Scrap-EAF benchmarks ($\text{LR} = 28.0$).
  2. `Stoichiometry` ($w = 1.50$): Capped engineering lower-bound breach ($\text{LR} = 500.0, C = 0.95$) or tight margin. Abstains ($C = 0$) when capacity is unknown or process gases are transferred off-site.
  3. `MultiPollutant_NOx_CO2` ($w = 1.20$): Flags decoupled $\text{NO}_x/\text{CO}_2$ combustion ratios ($\text{LR} \in [0.6, 5.8]$).
  4. `Historical_Fingerprint` ($w = 1.00$): Evaluates longitudinal drop $z_{\text{drop}}$ ($\text{LR} \in [0.5, 5.2]$), scaled by history completeness $C_{\text{hist}} = \min(1.0, N_{\text{years}}/5)$.
  5. `Satellite_Operational` ($w = 1.00$): Auxiliary plume contrast scaled by clear-sky confidence $C_{\text{sat}} = 1 - f_{\text{cloud}}$.
  6. `Registry_Capacity` ($w = 0.80$): Checks utilization ratio against GEM/permit nameplate bounds.
- **Monte Carlo Uncertainty & Confidence Gating:** Runs 500 Monte Carlo log-likelihood perturbations ($\sigma_{\ln \text{LR}} = 0.15$) to output a 95% credible interval. If overall weighted confidence $C_{\text{overall}} < 0.50$, the verdict automatically defaults to `Insufficient Evidence`.

#### Model E2: Supervised Logistic Regression with Facility-Grouped Cross-Validation (Triage Engine)
Trains an $L_2$-regularized Logistic Regression classifier on the standardized multimodal feature vector using **5-Fold `GroupKFold(n_splits=5, groups=facility_id)`** so that all years and perturbation scenarios of any given plant are strictly held out together during validation.

---

## 5. Directory of Participating Entities, Agencies, and Companies

### 5.1 European & International Institutions and Data Providers
| Entity / Organization | Acronym | Jurisdiction / Location | Role in CBAM & VeriCBAM | Official Website / Source |
| :--- | :---: | :---: | :--- | :--- |
| **Directorate-General for Taxation and Customs Union** | DG TAXUD | European Commission (Brussels) | Manages the central CBAM Registry, customs portal, declarant authorization, and verification rules | https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en |
| **Directorate-General for Climate Action** | DG CLIMA | European Commission (Brussels) | Oversees EU ETS carbon pricing alignment, free allocation phase-out, and climate policy | https://climate.ec.europa.eu |
| **Joint Research Centre (European IPPC Bureau)** | JRC | European Commission (Seville) | Authors CBAM technical embedded emissions methodology and EU BAT Reference Documents (BREFs) | https://eippcb.jrc.ec.europa.eu |
| **European Environment Agency** | EEA | European Union (Copenhagen) | Publishes the official E-PRTR / IED v16 Industrial Reporting Database (DOI: `10.2909/657ac3cb-affa-4295-a4a9-27b4f539adab`) | https://industry.eea.europa.eu |
| **European Space Agency & Copernicus Programme** | ESA / CDSE | European Union / ESA | Operates Sentinel-5P TROPOMI satellite and Copernicus Data Space Ecosystem API | https://dataspace.copernicus.eu |
| **Global Energy Monitor** | GEM | International (NGO) | Publishes the Global Steel Plant Tracker & Global Cement and Concrete Tracker (CC BY 4.0) | https://globalenergymonitor.org |
| **German Emissions Trading Authority (Umweltbundesamt)** | DEHSt / UBA | Germany (Berlin / Dessau) | National Competent Authority (NCA) for CBAM & EU ETS in Germany; manages German PRTR (Thru.de) | https://www.dehst.de |
| **National Centre for Emissions Management (GIOŚ / KOBiZE)** | KOBiZE / GIOŚ | Poland (Warsaw) | Polish National Competent Authority for CBAM/ETS and Chief Inspectorate of Environmental Protection | https://www.kobize.pl |
| **Dutch Emissions Authority & RIVM** | NEa / RIVM | Netherlands (The Hague / Bilthoven) | Dutch National Competent Authority for CBAM and National Pollutant Release Register | https://www.emissionsauthority.nl |
| **Institute for Environmental Protection and Research** | ISPRA | Italy (Rome) | Manages the Italian national E-PRTR industrial emissions inventory | https://www.isprambiente.gov.it |
| **Austrian Environment Agency** | UBA-AT | Austria (Vienna) | Manages the Austrian industrial emissions register and verification oversight | https://www.umweltbundesamt.at |
| **French Ministry for Ecological Transition** | DGEC / GEREP | France (Paris) | French CBAM Competent Authority and operator of the GEREP pollutant registry | https://www.ecologie.gouv.fr |
| **European Cement Association & German Cement Assoc.** | CEMBUREAU / VDZ | Brussels / Düsseldorf | Industry technical bodies publishing clinker ratios, kiln thermal efficiency, and decarbonization data | https://www.vdz-online.de |
| **European Steel Association & World Steel Assoc.** | EUROFER / worldsteel | Brussels / Brussels | Industry bodies publishing BF-BOF and EAF steel production routes and mass balances | https://www.eurofer.eu |
| **European co-operation for Accreditation & NABs** | EA / DAkkS / COFRAC | Pan-European | National Accreditation Bodies accrediting CBAM verifiers under Delegated Reg. (EU) 2025/2551 | https://european-accreditation.org |
| **Accredited Third-Party Verification Bodies** | VBs | Global / EU | Engineering audit firms (*TÜV SÜD, DNV, SGS, Bureau Veritas, LRQA, GUTcert, RINA*) executing CBAM audits | ISO 14064-3 / Reg. 2025/2551 |

---

### 5.2 Complete Registry of the 30 Industrial Facilities & Parent Companies in VeriCBAM

#### A. Cement Sector Cohort (15 Major European Installations)
| # | Facility Name (E-PRTR Legal Name) | Parent Company / Group | Location (City, Country) | Verified Technology Route | Clinker / Cement Cap. (Mtpa) | Util. ($\eta$) | Primary Verification Source |
| :-: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 1 | **CEMEX Zement GmbH** | CEMEX S.A.B. de C.V. | Rüdersdorf bei Berlin, Germany | Dry Kiln with 4-Stage Preheater/Precalciner | 2.00 / 2.40 | 80% | https://www.cemex.de/zementwerk-ruedersdorf |
| 2 | **Dyckerhoff GmbH, Werk Deuna** | Buzzi S.p.A. (Dyckerhoff) | Niederorschel, Germany | Dry Kiln with Preheater/Precalciner | 1.50 / 1.80 | 78% | https://www.dyckerhoff.com/standorte/werk-deuna |
| 3 | **Dyckerhoff GmbH (Lengerich)** | Buzzi S.p.A. (Dyckerhoff) | Lengerich, Germany | Dry Kiln with Preheater/Precalciner | 1.20 / 1.50 | 76% | https://www.dyckerhoff.com/standorte/werk-lengerich |
| 4 | **Holcim (Deutschland) GmbH** | Holcim Group | Lägerdorf, Germany | Semi-Dry / Preheater Kiln (Oxyfuel Project) | 1.20 / 1.40 | 80% | https://www.holcim.de/ueber-uns/standorte/werk-laegerdorf |
| 5 | **Heidelberg Materials AG, Werk Burglengenfeld** | Heidelberg Materials AG | Burglengenfeld, Germany | Dry Kiln with Preheater/Precalciner | 1.10 / 1.30 | 78% | https://www.heidelbergmaterials.de/standorte/zementwerk-burglengenfeld |
| 6 | **HeidelbergCement (Werk Schelklingen)** | Heidelberg Materials AG | Schelklingen, Germany | Modernized 5-Stage Preheater Kiln (SCR) | 1.20 / 1.45 | 82% | https://www.heidelbergmaterials.de/standorte/zementwerk-schelklingen |
| 7 | **Schwenk Zement (Allmendingen)** | SCHWENK Zement GmbH & Co. KG | Allmendingen, Germany | Dry Kiln with Preheater/Precalciner | 1.05 / 1.25 | 78% | https://www.schwenk.de/standorte/allmendingen |
| 8 | **Zementwerk Rohrdorf** | Rohrdorfer Gruppe | Rohrdorf, Germany | Dry Kiln with Precalciner & $\text{CO}_2$ Capture Pilot | 1.15 / 1.40 | 80% | https://www.rohrdorfer.eu/ueber-uns/standorte/rohrdorf |
| 9 | **Heidelberg Materials AG, Werk Lengfurt** | Heidelberg Materials AG | Triefenstein, Germany | Dry Kiln with Preheater/Precalciner | 1.00 / 1.20 | 78% | https://www.heidelbergmaterials.de/standorte/zementwerk-lengfurt |
| 10 | **Dyckerhoff GmbH (Göllheim)** | Buzzi S.p.A. (Dyckerhoff) | Göllheim, Germany | Dry Kiln with Preheater/Precalciner | 0.95 / 1.20 | 76% | https://www.dyckerhoff.com/standorte/werk-goellheim |
| 11 | **Górażdże Cement S.A.** | Heidelberg Materials AG | Chorula, Poland | Dry Kiln with Multi-Stage Precalciner | 3.60 / 4.20 | 85% | https://www.gorazdze.pl |
| 12 | **HERACLES G.C.Co, Milaki Plant** | Holcim Group (Heracles) | Aliveri (Evia), Greece | Dry Kiln with Precalciner (Coastal Export) | 2.20 / 2.60 | 85% | https://www.lafarge.gr |
| 13 | **Grupa Ożarów S.A.** | CRH plc | Karsy / Ożarów, Poland | Dry Kiln with Preheater/Precalciner | 2.40 / 2.90 | 80% | https://www.ozarow.com.pl |
| 14 | **Aalborg Portland A/S** | Cementir Holding N.V. | Aalborg Øst, Denmark | Dry + Semi-Wet White & Grey Cement Kilns | 2.50 / 3.20 | 85% | https://www.aalborgportland.dk |
| 15 | **Heidelberg Materials Cement Sverige AB** | Heidelberg Materials AG | Slite (Gotland), Sweden | Dry Kiln with Precalciner (Slite CCS Project) | 2.00 / 2.30 | 82% | https://www.heidelbergmaterials.se/sv/slite |

#### B. Iron & Steel Sector Cohort (15 Major European Installations)
| # | Facility Name (E-PRTR Legal Name) | Parent Company / Group | Location (City, Country) | Verified Technology Route & Boundary Status | Crude Steel / Iron Cap. (Mtpa) | Util. ($\eta$) | Primary Verification Source |
| :-: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 16 | **Salzgitter Flachstahl GmbH** | Salzgitter AG | Salzgitter, Germany | BF-BOF Integrated (3 BFs, 3 LD Converters) | 4.70 / 4.40 | 86% | https://www.salzgitter-ag.com |
| 17 | **Hüttenwerke Krupp Mannesmann (HKM)** | thyssenkrupp / Salzgitter / Vallourec | Duisburg, Germany | BF-BOF Integrated (*Transferred BFG Boundary*) | 5.60 / 5.20 | 45% | https://www.hkm.de |
| 18 | **ArcelorMittal Bremen GmbH** | ArcelorMittal S.A. | Bremen, Germany | BF-BOF Integrated (*Transferred BFG to SWB Power*) | 3.60 / 3.40 | 38% | https://bremen.arcelormittal.com |
| 19 | **ArcelorMittal Eisenhüttenstadt GmbH** | ArcelorMittal S.A. | Eisenhüttenstadt, Germany | BF-BOF Integrated (*Transferred BFG to Vattenfall*) | 2.40 / 2.00 | 42% | https://eisenhuettenstadt.arcelormittal.com |
| 20 | **thyssenkrupp Steel Europe Werk Hamborn** | thyssenkrupp AG | Duisburg, Germany | Partial Complex: Ironmaking Only (Schwelgern BFs) | 0.00 / 7.20 | 12% | https://www.thyssenkrupp-steel.com |
| 21 | **thyssenkrupp Steel Europe Werk Beeckerwerth** | thyssenkrupp AG | Duisburg, Germany | Partial Complex: Downstream Hot/Cold Rolling Only | 0.00 / 0.00 | 80% | https://www.thyssenkrupp-steel.com |
| 22 | **DK Recycling und Roheisen GmbH** | DK Recycling Group | Duisburg, Germany | Specialized Ferrous Waste Blast Furnace (Pig Iron) | 0.00 / 0.35 | 80% | https://www.dk-duisburg.de |
| 23 | **thyssenkrupp Steel Europe Werk Bruckhausen** | thyssenkrupp AG | Duisburg, Germany | Partial Complex: LD-BOF Converter Shop & Casting | 5.80 / 0.00 | 80% | https://www.thyssenkrupp-steel.com |
| 24 | **ArcelorMittal Hochfeld GmbH** | ArcelorMittal S.A. | Duisburg, Germany | Secondary Scrap-EAF Electric Mini-Mill (Wire Rod) | 1.05 / 0.00 | 82% | https://germany.arcelormittal.com |
| 25 | **Georgsmarienhütte GmbH** | GMH Gruppe | Georgsmarienhütte, Germany | Secondary Scrap-EAF (100% Scrap DC Electric Arc) | 1.00 / 0.00 | 75% | https://www.gmh-gruppe.de |
| 26 | **voestalpine Stahl GmbH** | voestalpine AG | Linz, Austria | BF-BOF Integrated (Birthplace of LD Process; 3 BFs) | 6.00 / 5.40 | 78% | https://www.voestalpine.com/stahl/en |
| 27 | **ArcelorMittal Méditerranée** | ArcelorMittal S.A. | Fos-sur-Mer, France | BF-BOF Integrated Coastal Steelworks (BF1, BF2) | 4.50 / 4.20 | 80% | https://mediterranee.arcelormittal.com |
| 28 | **Tata Steel IJmuiden BV** | Tata Steel Ltd. | Velsen-Noord, Netherlands | BF-BOF Integrated (*Transferred BFG to Velsen Power*) | 7.50 / 7.00 | 45% | https://www.tatasteel.nl |
| 29 | **U.S. Steel Košice s.r.o.** | United States Steel Corp. | Košice, Slovakia | BF-BOF Integrated (BF1, BF2, BF3) | 4.50 / 4.20 | 78% | https://www.usske.sk |
| 30 | **Stabilimento di Taranto** | Acciaierie d'Italia (ex-Ilva) | Taranto, Italy | BF-BOF Integrated (*Transferred BFG to CET Power*) | 8.00 / 7.50 | 35% | https://www.gruppoadi.com |

---

## 6. How the Project Works: End-to-End Architecture & Empirical Results

### 6.1 Four-Layer System Architecture
1. **Layer 1 — Authentic Reference Data Ingestion (`src/data_loaders/`):**
   - Extracts 177 real facility-year reporting records (2018–2023) across the 30 European plants from the EEA E-PRTR v16 relational tables (`F1_4_Air_Releases_Facilities.csv` and `F1_1_Facilities.csv`).
   - Computes leave-one-year-out $\text{NO}_x/\text{CO}_2$ combustion baselines (`nox_baseline.py`, 165 valid fingerprints) and maps verified GEM/corporate capacities (`technology_registry.py`).
   - Queries authentic Copernicus Sentinel-5P Level-2 $\text{NO}_2$ netCDF/HDF5 granules via STAC/CDSE (`copernicus_client.py`), storing 301 clear-sky overpasses with full orbit and QA provenance (`data/03_satellite_cache/`).
2. **Layer 2 — Stoichiometric & Statistical Engines (`src/core/`):**
   - `cement_models.py` and `steel_models.py`: Compute exact chemical calcination/reduction lower bounds, scrap dilution adjustments, and route misclassification flags.
   - `evidence_fusion.py`: Executes weighted log-odds Bayesian updating, Monte Carlo sensitivity simulation, and confidence gating.
3. **Layer 3 — Graded Benchmark & Evaluation Pipeline (`src/benchmark/`, `experiments/`):**
   - Generates the **325-case Graded Evaluation Benchmark** (`graded_evaluation_benchmark.parquet`): 177 authentic real-year negatives, 140 graded understatements ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$), and 8 verified route misclassifications.
   - Executes 1,000 facility-clustered bootstrap resamples (`run_graded_evaluation.py`) to compute 95% confidence intervals across all six models.
4. **Layer 4 — Interactive 8-Tab Streamlit Decision Cockpit (`src/ui/app.py`):**
   - **Tab 1:** Executive Overview & System Architecture.
   - **Tab 2:** Facility Cohort & Geospatial Inspector (interactive map + historical trajectory timeline with legal threshold overlays).
   - **Tab 3:** Stoichiometric Feasibility & Route Sandbox (interactive chemical mass-balance simulator).
   - **Tab 4:** Standalone Supplier Plausibility Pre-Check (zero-history screening for non-EU suppliers).
   - **Tab 5:** Copernicus Sentinel-5P Satellite Inspector (orbital $\text{NO}_2$ plume contrast & cloud-gating viewer).
   - **Tab 6:** Bayesian Evidence Fusion & Audit Dossier Generator (waterfall log-odds chart, prior sensitivity curve, and 1-click Markdown dossier download).
   - **Tab 7:** Empirical Benchmark Evaluation & Ablation Suite (full statistical comparison, triage simulation, and methodological attribution).
   - **Tab 8:** Capstone Proposal, Regulatory ELI Links & Roadmap.

### 6.2 Definitive Empirical Benchmark Results (325 Graded Cases, $\delta \ge 10\%$)
| Model Architecture | ROC-AUC (95% CI) | PR-AUC (95% CI) | Brier Score | ECE | Authentic FPR | Recall @ 5% FPR | Recall @ 10% FPR | Abstention Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model A: Naive Prior ($P=0.08$)** | 0.5000 [0.500, 0.500] | 0.3692 [0.369, 0.369] | 0.2329 | 0.3192 | 0.00% | 0.00% | 0.00% | 0.0% |
| **Model B: Stoichiometry Alone** | 0.7909 [0.719, 0.891] | 0.7326 [0.641, 0.845] | 0.1884 | 0.1571 | 1.55% | 33.73% | 54.22% | 28.6% |
| **Model C: Satellite S-5P Alone** | 0.5183 [0.499, 0.544] | 0.3781 [0.359, 0.396] | 0.3731 | 0.3474 | 96.61% | 6.67% | 10.83% | 0.0% |
| **Model D: Historical Trajectory Alone** | 0.9631 [0.957, 0.972] | 0.9428 [0.931, 0.957] | 0.0826 | 0.0632 | 6.78% | 83.33% | 90.83% | 0.0% |
| **Model E1: Expert Bayesian Fusion** | 0.8935 [0.865, 0.924] | 0.8684 [0.832, 0.901] | 0.1530 | 0.1652 | **0.56%** | 69.17% | 70.00% | 0.0% |
| **Model E2: Learned Logistic (GroupKFold)** | **0.9643** [0.956, 0.973] | **0.9484** [0.938, 0.961] | **0.0787** | **0.0630** | 6.78% | **85.00%** | **91.67%** | 0.0% |

### 6.3 Key Scientific Conclusions & Methodological Honesty
1. **Recall Parity at Matched False-Positive Rates (Step 6 Finding):**  
   When evaluated at matched false-alarm budgets ($\text{FPR} = 5\%, 10\%$), **Model D (Historical Alone: 83.3% / 90.8% recall)** performs nearly identically to **Model E2 (Learned Logistic: 85.0% / 91.7% recall)**. This proves that longitudinal historical drift is the primary statistical driver of recall in facility time series, whereas multimodal fusion (**Model E1**) provides *physical explainability, boundary-aware mass-balance enforcement, and near-zero false alarms (0.56% FPR)* for legal audit dossiers.
2. **Biomass Reporting Sparsity in Official EEA Data (Step 11 Finding):**  
   Inspection of the EEA E-PRTR database confirms that `Carbon dioxide (CO2) excluding biomass` is missing (`NaN`) for **163 out of 177 facility-years (92.1%)**. Total direct `Carbon dioxide (CO2)` is therefore the only complete pan-European regulatory series.
3. **Deterministic Reproducibility:**  
   Running `python scripts/reproduce_all.py` executes all 11 data, modeling, calibration, and testing stages end-to-end, passing **28/28 automated `pytest` unit and integration tests**.

---

## 7. Quick-Copy Source URL Index for Google NotebookLM
To add original authoritative primary sources directly into your **Google NotebookLM** notebook alongside this PDF, copy and paste the following URLs into NotebookLM's *"Add Source -> Website"* dialog:

1. **Primary EU CBAM Regulation (EU) 2023/956:** https://eur-lex.europa.eu/eli/reg/2023/956/oj
2. **CBAM Transitional Reporting Regulation (EU) 2023/1773:** https://eur-lex.europa.eu/eli/reg_impl/2023/1773/oj
3. **CBAM Verification Principles Implementing Regulation (EU) 2025/2546:** https://eur-lex.europa.eu/eli/reg_impl/2025/2546/oj
4. **CBAM Embedded Emissions Calculation Regulation (EU) 2025/2547:** https://eur-lex.europa.eu/eli/reg_impl/2025/2547/oj
5. **CBAM Verifier Accreditation Delegated Regulation (EU) 2025/2551:** https://eur-lex.europa.eu/eli/reg_del/2025/2551/oj
6. **European Commission DG TAXUD Official CBAM Portal:** https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en
7. **EEA European Industrial Emissions Portal (E-PRTR / IED v16):** https://industry.eea.europa.eu/
8. **EEA E-PRTR Dataset Metadata Record:** https://sdi.eea.europa.eu/catalogue/srv/api/records/657ac3cb-affa-4295-a4a9-27b4f539adab
9. **Global Energy Monitor — Global Steel Plant Tracker:** https://globalenergymonitor.org/projects/global-steel-plant-tracker/
10. **Global Energy Monitor — Global Cement and Concrete Tracker:** https://globalenergymonitor.org/projects/global-cement-and-concrete-tracker/
11. **IPCC 2019 Refinement to the 2006 GHG Inventory Guidelines (Vol. 3 IPPU):** https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol3.html
12. **EU JRC Best Available Techniques (BREF) — Cement & Lime (2013/163/EU):** https://eippcb.jrc.ec.europa.eu/reference/production-cement-lime-and-magnesium-oxide
13. **EU JRC Best Available Techniques (BREF) — Iron & Steel (2012/135/EU):** https://eippcb.jrc.ec.europa.eu/reference/iron-and-steel-production
14. **ESA Copernicus Sentinel-5P TROPOMI Mission Portal:** https://sentiwiki.copernicus.eu/web/s5p-mission
15. **VeriCBAM Public GitHub Repository:** https://github.com/CaceresCristhian/VeriCBAM
