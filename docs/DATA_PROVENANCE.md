# VeriCBAM Scientific Data Provenance & Lineage Specification
**Project:** VeriCBAM: Multimodal Decision-Support System for CBAM Emissions Auditing  
**Degree Program:** Master of Science in Data Science | University of Europe for Applied Sciences (Berlin)  
**Student:** Cristhian David Cáceres Mateus | **Supervisor:** Dr. Humera Noor  
**Document Version:** 2.0 (Post-Review Alignment)  
**Date:** October 7, 2026  

---

## 1. Overview of Data Architecture
VeriCBAM operates a strict dual-layer empirical architecture:
- **Layer A (Authentic Reference Observations):** Real, unperturbed industrial emissions, physical plant configurations, and remote sensing overpasses from official regulatory and orbital sources.
  - 177 plant-years (2018–2023) across 30 European heavy industrial facilities from the EEA Industrial Reporting Database.
  - Multi-pollutant co-emissions panel (`facility_nox_co2_ratios.csv`) capturing $\text{NO}_x/\text{CO}_2$ and $\text{SO}_x/\text{CO}_2$ combustion fingerprints.
  - Multi-year Sentinel-5P TROPOMI cache (2019–2023, `s5p_no2_annual_stats_2019_2023.csv`) covering 25 facility-years via CDSE / Planetary Computer STAC.
- **Layer B (Controlled & Graded Evaluation Suites):**
  - **101-Case Controlled Ablation Suite:** Initial benchmark testing 30 unperturbed, 30 physical violations, 30 historical drops, and 11 route mismatches.
  - **326-Case Graded Evaluation Benchmark (`graded_evaluation_benchmark.parquet`):** Advanced benchmark testing 177 authentic real-year negatives with natural operational variance (pooled MAD $\sigma = 0.0911$), 140 graded understatements across 5 perturbation magnitudes ($\delta \in \{5\%, 10\%, 20\%, 30\%, 50\%\}$), and 9 route mismatches under conservative capacity utilization $\eta \in [0.50, 0.95]$.

---

## 2. Dataset 1: EEA Industrial Emissions Reporting (E-PRTR / IED v16)
- **Dataset Name:** European Pollutant Release and Transfer Register (E-PRTR) & Industrial Emissions Directive (IED) Integrated Panel
- **Issuing Entity:** European Environment Agency (EEA)
- **Source Portal:** https://industry.eea.europa.eu/download
- **Catalogue Record:** https://sdi.eea.europa.eu/catalogue/srv/api/records/657ac3cb-affa-4295-a4a9-27b4f539adab
- **DOI:** 10.2909/657ac3cb-affa-4295-a4a9-27b4f539adab
- **Version:** v16.0 (Latest consolidated multi-year release)
- **Access / Download Date:** October 2026
- **License / Terms of Use:** Open Access under EEA Standard Re-use Policy / Directive 2003/98/EC
- **Variables Extracted:**
  - `FacilityInspireId`: Unique spatial INSPIRE identifier for heavy industrial sites
  - `facilityName`: Legal operating name of the installation
  - `countryName`: ISO alpha-2 / country name
  - `reportingYear`: Annual reporting year (2018–2023)
  - `pollutantName`: Direct emissions for $\text{CO}_2$, $\text{NO}_x$, and $\text{SO}_2$
  - `totalPollutantQuantityKg`: Total verified annual mass of direct emissions (kg, converted to metric tonnes)
  - `Latitude`, `Longitude`: WGS-84 decimal coordinates of the installation perimeter
  - `mainActivityName`: Industrial sector classification (Cement clinker kilns, Iron & Steel basic oxygen/electric furnaces)
- **Filtering Applied:**
  - Sector filter: Activity codes matching cement clinker production (IED 3.1.a) and primary/secondary iron & steel manufacturing (IED 2.2).
  - Completeness filter: Installations with multi-year reporting history across the 2018–2023 observation window.
  - Final cohort: Exactly 30 premier European production facilities (15 Cement, 15 Steel).
- **Transformations:**
  - `co2_tonnes = totalPollutantQuantityKg / 1000.0`
  - Longitudinal baseline metrics: Mean $\mu_{\text{facility}}$ and standard deviation $\sigma_{\text{facility}}$ computed across available reference years.
  - Multi-pollutant ratios: $\text{NO}_x/\text{CO}_2$ ($\text{kg}/\text{t}$) and $\text{SO}_x/\text{CO}_2$ ($\text{kg}/\text{t}$) calculated across 177 plant-years.
- **Missing Data Handling (177 vs. 180 Observations):**
  - Theoretical panel: $30\text{ facilities} \times 6\text{ years} = 180\text{ facility-year combinations}$.
  - Available observations: Exactly 177 authentic observations.
  - Missing records (3 combinations): Documented non-reporting years due to scheduled facility relining or reporting exemption thresholds (e.g., ArcelorMittal Bremen 2020 blast furnace relining). Not imputed synthetically; statistics calculated strictly over available observations.
- **Spatial Processing:** Point coordinates verified against GEM Global Steel/Cement Plant Trackers and Google Satellite imagery.
- **Temporal Window:** 2018–2022 used as historical reference baseline; 2023 used as the evaluation reporting year.
- **Frozen Artifact & Integrity Verification:**
  - File: `data/02_processed/benchmark_cohort.parquet`
  - Dimensions: 177 rows × 18 columns across 30 facilities (2018–2023)
  - SHA-256 Checksum: `134505d14b6232e42d3b097dd5ea5c7557a922c23eda76a81761b4e781df1ef1`
  - Source Tables: Extracted from EEA IED/E-PRTR v16 Air Releases (`F1_4_Air_Releases_Facilities.csv`) matched against Facility Register (`F1_1_Facilities.csv`).
- **Known Limitations:** E-PRTR records represent historical regulatory compliance under the EU ETS/E-PRTR reporting framework, serving as an independent reference baseline rather than ground truth for CBAM import fraud.

---

## 3. Dataset 2: Verified Technology & Capacity Registry
- **Dataset Name:** European Heavy Industrial Plant Technology & Capacity Registry
- **Sources & URLs:**
  - Global Energy Monitor (GEM) Global Steel Plant Tracker: https://globalenergymonitor.org/projects/global-steel-plant-tracker/
  - Global Energy Monitor (GEM) Global Cement and Concrete Tracker: https://globalenergymonitor.org/projects/global-cement-and-concrete-tracker/
  - Verein Deutscher Zementwerke (VDZ) Environmental Data Reports: https://www.vdz-online.de
  - EUROFER European Steel in Figures / Annual Reports: https://www.eurofer.eu
  - Official national environmental operating permits (e.g., Bezirksregierung Düsseldorf, Arpa Puglia)
  - Corporate Annual Sustainability Reports (ArcelorMittal, Thyssenkrupp, Heidelberg Materials, Holcim, CEMEX)
- **Version / Publication Dates:** 2022–2025 releases
- **Access Date:** October 2026
- **License:** GEM Creative Commons CC BY 4.0; public corporate financial & environmental disclosures
- **Variables Extracted:**
  - `facility_id` (`FacilityInspireId`)
  - `verified_technology_route`: Primary chemical conversion route (e.g., "BF-BOF integrated", "Scrap-EAF", "Dry Kiln with Precalciner", "Secondary converter shop")
  - `clinker_capacity_mtpa`: Nameplate clinker production capacity (Million metric tonnes per annum)
  - `crude_steel_capacity_mtpa`: Nameplate crude steel production capacity (Mt/yr)
  - `primary_iron_capacity_mtpa`: Nameplate blast furnace hot metal capacity (Mt/yr)
  - `typical_capacity_utilization_ratio`: Independently verified conservative capacity utilization factor ($\eta \in [0.50, 0.95]$)
  - `utilization_source_basis`: External industrial report documenting the plant's operational rate
  - `is_partial_site`: Flag indicating whether the E-PRTR permit encompasses only a specific sub-unit of a wider complex (e.g., Thyssenkrupp Hamborn blast furnaces vs. Bruckhausen converter shop)
  - `mapping_method`: Explicit provenance linking E-PRTR facility coordinates and registry names to GEM ID / corporate permits
- **Independence Principle (Addressing Finding #4 / Red R3):**
  - Production activity in the controlled benchmark is strictly calculated as:
    $$\text{Annual Production} = \text{Nameplate Capacity (t)} \times \eta$$
  - It is completely decoupled from reported emissions, eliminating circular dependencies.

---

## 4. Dataset 3: Copernicus Sentinel-5P TROPOMI Satellite Observations
- **Dataset Name:** Sentinel-5 Precursor TROPOMI Tropospheric Nitrogen Dioxide Level-2 Product
- **Satellite Platform:** Sentinel-5 Precursor (S5P), Copernicus Program
- **Instrument:** TROPOMI (TROPOspheric Monitoring Instrument), push-broom UV-VIS-NIR-SWIR grating spectrometer
- **Product ID:** `S5P_L2__NO2____` (Level-2 Tropospheric NO₂ Vertical Column Density)
- **Collection / Processor:** Collection 02 / Processor Version v02.04.00+
- **Data Source / API:** Microsoft Planetary Computer STAC API (`planetary-computer`) with Azure Blob Storage range reads & Copernicus Data Space Ecosystem (CDSE) OAuth2
- **License:** Copernicus Open Access Policy (Directive (EU) 2019/1024)
- **Extraction Protocol:**
  - Spatial Filter: Bounding box centered on facility coordinates ($\Delta \text{lat} = \pm 0.15^\circ, \Delta \text{lon} = \pm 0.15^\circ$)
  - Quality Assurance (QA): Observations filtered strictly at `qa_value >= 0.50` (eliminating cloud-obscured pixels, snow, and retrieval anomalies as recommended in Sentinel-5P Product User Manual)
  - Spatial Resolution: $3.5 \times 5.5\text{ km}^2$ nadir pixel footprint
- **Operational Activity Indicators Derived:**
  - `tropospheric_no2_vcd`: Tropospheric vertical column density ($\text{mol}/\text{m}^2$)
  - `plume_anomaly_zscore`: Standardized contrast between facility near-field ($\le 5\text{ km}$) and surrounding regional background annulus ($15\text{–}30\text{ km}$):
    $$z_{\text{plume}} = \frac{\bar{V}_{\text{facility}} - \bar{V}_{\text{background}}}{\text{MAD}_{\text{background}} \times 1.4826}$$
- **Provenance Attributes Recorded for Every Overpass:**
  - `granule_id`, `orbit_number`, `processor_version`, `qa_value`, `cloud_fraction`, `observation_date`, `wind_u`, `wind_v`
- **Zero Synthetic Fallback Policy:**
  - Synthetic or simulated satellite substitution is disabled.
  - If fewer than 3 cloud-free overpasses are available (`qa_value >= 0.50`), the engine returns `satellite_data_source = "no_data"` and triggers the `Insufficient Evidence` triage state.
- **Observation Statistics:**
  - 301 clear-sky Level-2 overpasses cached across the European cohort.
  - Multi-year pipeline: 2019–2023 annual mean NO2 composites extracted across 25 industrial facility-years via CDSE.
  - Benchmark coverage: 326 cases evaluated across 177 authentic real-year negatives, 140 graded understatements, and 9 route mismatches.

---

## 5. Summary of Data Governance & Integrity Controls
| Control Requirement | Implementation Status | Evidence / Verification |
| :--- | :---: | :--- |
| **No Synthetic Data in Reference Cohort** | Fully Satisfied | 177 real E-PRTR records from EEA Industrial Reporting Database |
| **Decoupled Activity Benchmark** | Fully Satisfied | Production calculated from capacity $\times$ industrial utilization factor $\eta \in [0.50, 0.95]$ |
| **Zero Synthetic Satellite Fallback** | Fully Satisfied | Real Planetary Computer S5P L2 granules; missing overpasses return `Insufficient Evidence` |
| **Documented Missing Data** | Fully Satisfied | 3 non-reporting facility-years explicitly identified (relining/exemption) |
| **Out-of-Facility Generalization** | Fully Satisfied | Evaluated via `GroupKFold(n_splits=5, groups=facility_id)` with zero leakage |
