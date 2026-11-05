# VeriCBAM Quick User Guide
## 30-Second Screening & Audit Dossier Guide for Companies & Institutions

**Live Web Application:** [https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/](https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/)  
**Document Purpose:** A concise, step-by-step walkthrough for external stakeholders (industrial importers, accredited verifiers, and customs authorities) to test emissions declarations and generate official pre-audit dossiers.

---

### Step 1: Open the Quick Audit Cockpit
1. Navigate to the live web application: https://vericbam-uqpz4jrnpteqetfvjxtslh.streamlit.app/
2. In the left navigation sidebar, ensure **Tab 1: 🚀 Quick Audit & PDF Dossier Generator** is selected (this is the default landing page).

---

### Step 2: Choose Your Testing Mode

The tool provides three zero-friction ways to test an industrial declaration:

#### Mode A: Test a Pre-Loaded Reference Plant (Fastest — 15 seconds)
* Select any facility from the **European Reference Facility** dropdown (e.g., *ThyssenKrupp Steel Europe Duisburg* or *Cementownia Górażdże*).
* The system automatically pulls verified nameplate capacities, country metadata, and real multi-sensor satellite observations (Landsat 30m thermal core $\Delta T$, NASA VIIRS 375m active operating months, and Planet VHR rail-yard contrast).
* Adjust the **Declared Production** or **Declared $\text{CO}_2$** numbers if you want to test a "what-if" under-reporting scenario.

#### Mode B: Test an External Foreign Supplier (Zero Prior History)
* Ideal for testing non-EU installations (e.g., in Turkey, India, China, or the USA) where historical European records do not exist.
* Enter the **Facility Name**, **Sector** (Cement or Steel), **Production Route** (e.g., Blast Furnace `BF-BOF`, Scrap Recycling `Scrap-EAF`, or `Dry Kiln`), **Annual Production (Tonnes)**, and **Declared $\text{CO}_2$ (Tonnes)**.
* Check the box: *"External Facility Lacks Past History (Use Satellite Data Only)"*.
* Expand the **Satellite Remote Sensing Parameters** to test different operational scenarios (e.g., 12 active firing months vs. an idling furnace).

#### Mode C: Upload a CSV Declaration File
* Drag and drop a `.csv` file containing factory declaration rows (`facility_name`, `sector`, `route`, `production_tonnes`, `declared_co2_tonnes`).
* Select any row from the uploaded table to audit it instantly.

---

### Step 3: Review the Automated Screening Diagnostic
The system instantly calculates and displays:
1. **Specific Carbon Intensity ($t\text{CO}_2/t$):** Compared directly against the chemical thermodynamic lower bound (e.g., $1.350\text{ t/t}$ for BF-BOF steel, $0.770\text{ t/t}$ for cement clinker).
2. **Physical Mass Balance Status:** Displays **FEASIBLE** (green) or **VIOLATION** (red) with the exact missing $\text{CO}_2$ tonnage.
3. **Satellite Kiln/Furnace Activity:** Verifies how many months per year the furnace operated hot and its thermal anomaly $\Delta T$.
4. **Inconsistency Risk Score ($0\%\text{--}100\%$):** 
   * 🟢 **CONSISTENT ($<25\%$):** Clear for expedited import clearance.
   * 🟡 **POTENTIAL INCONSISTENCY ($25\%\text{--}70\%$):** Request energy invoices / CEMS records.
   * 🔴 **HIGH INCONSISTENCY RISK ($>70\%$):** Mandatory on-site audit recommended.

---

### Step 4: Download the Official Pre-Audit Dossier (PDF)
* Scroll to the bottom of Tab 1.
* Click the blue button: **`📄 Download Official Pre-Audit Screening Dossier (PDF)`**.
* An official, publication-quality 1-page PDF document is instantly generated in your browser containing:
  * Facility metadata, timestamp, and regulatory reference (Regulation (EU) 2025/2546).
  * Color-coded verdict banner and recommended verification action.
  * Quantitative emissions vs. physical bound breakdown table.
  * Multi-source evidence synthesis matrix (physics, satellite, and registry).
  * Official lead verifier sign-off block with SHA256 audit reference.

---
*For technical inquiries or demonstration requests: Cristhian David Cáceres Mateus (M.Sc. Data Science Candidate, University of Europe for Applied Sciences, Potsdam Campus).*
