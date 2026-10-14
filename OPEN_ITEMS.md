# VeriCBAM: Open Items & Decision Register

This register records methodological choices, unverified claims, credentials actions, and items pending user decisions.

---

## 1. Urgent Security Action
- [ ] **Rotate Copernicus Client Secret:**  
  *User must rotate the previously exposed Copernicus client secret.*  
  Although `Copernicus.txt` has been purged from git, current zips, and `.gitignore`, the secret was previously packaged in earlier archive versions. A new client secret should be generated in the Copernicus Data Space Ecosystem (CDSE) portal and the old one revoked. The code now reads `CDSE_CLIENT_ID` and `CDSE_CLIENT_SECRET` environment variables as primary configuration.

---

## 2. Decision on CO2 Definition (Item N3) - RESOLVED
- **Status:** Empirical Evaluation Completed (Retain Total CO2 as Primary).
- **Finding:** In `benchmark_cohort_multipollutant.parquet`, `co2_excl_biomass_tonnes` is missing (`NaN`) for **163 out of 177 rows (92.1%)** in official EEA reporting. Only 14 facility-years report a non-null value.
- **Resolution:** Total `Carbon dioxide (CO2)` is the only viable pan-European reporting series. Retained as primary standard, documented in `DATA_PROVENANCE.md` and `MODEL_CARD.md`.

---

## 3. Tier B UI Expansion Decision
- **Status:** Pending User Decision at Checkpoint 1.
- **Details:** Tier A improvements (honest metrics from CSVs, removal of hardcoded cards, Delegated 2025/2551 nomenclature, scope banners) are completed. Tier B (full multi-page rewrite with `st.navigation` and custom components) is held until approved.

---

## 4. Factual and Regulatory Claims Register

| Claim | Current Code/Doc Status | Authoritative Status / Action Taken |
| :--- | :--- | :--- |
| **Materiality threshold (10% vs 5%)** | Relabeled to *project-defined screening threshold*. | Under Commission Implementing Regulation (EU) 2025/2546 (Article 5), materiality is defined at the **level of goods** (product-level specific embedded emissions). E-PRTR benchmark uses plant-level Scope 1 totals; neither 5% nor 10% is a legal CBAM materiality threshold for this benchmark. Both thresholds evaluated as sensitivity analysis. |
| **Regulation 2025/2551 classification** | Corrected to **Commission Delegated Regulation (EU) 2025/2551**. | Verified on EUR-Lex (`http://data.europa.eu/eli/reg_del/2025/2551/oj`). Relates to accreditation, control, and oversight of CBAM verifiers. |
| **"~403 verification bodies globally hold accreditation"** | Softened to unsourced estimate of EU ETS verifiers. | Estimate of historical EU ETS verifiers under Accreditation and Verification Regulation (EU) 2018/2067. CBAM accreditation under Delegated Regulation (EU) 2025/2551 begins in late 2026. Marked as *unsourced estimate*. |
| **"€50,000 to €150,000+ per site visit"** | Marked as unsourced industry estimate. | Frequently cited in trade publications for complex integrated overseas audits; no single authoritative academic citation exists. Marked explicitly as *unsourced estimate*. |
| **"~12,000 EU import entities"** | Marked as estimated declarants. | Estimated scope of CBAM declarants under Commission transition reports. Marked as *estimate*. |
| **"Physical on-site audits are mandatory"** | Softened to *regulatory default*. | Under Implementing Regulation (EU) 2025/2546, physical on-site audits are the default for initial verifications, subject to strict conditions under which site visits may be waived. |

---

## 5. Offline Data and Environment Constraints
- **EEA Raw Tables:** The 2.2 GB raw EEA database zip is excluded from distribution archives. Cohort processing is verified reproducible offline from `benchmark_cohort_multipollutant.parquet`.
- **Sentinel-5P Satellite Ingestion:** No live API calls to CDSE or Planetary Computer are permitted during offline tests. Uses static offline cache in `data/03_satellite_cache/`.
## 6. Steel Installation Floor & Boundary Diagnosis (RESOLVED)
- **Problem:** Initial implementation observed 34 authentic negative facility-years violating the conservative steel stoichiometric floor.
- **Root Cause 1 (Transferred Process Gases):** In 5 major steelworks (ArcelorMittal Bremen, Eisenhüttenstadt, Acciaierie d'Italia Taranto, HKM, Tata Steel IJmuiden), blast furnace gas is transferred to adjacent power stations outside the E-PRTR boundary. Scope 1 direct emissions reflect only internal plant combustion.
- **Root Cause 2 (Conservative Floor Logic):** Conservative floor was previously calculated against maximum capacity ($0.95 \times \text{cap}$), making it non-conservative.
- **Fix Implemented:** Evaluated against minimum plausible utilization ($0.50 \times \text{cap}$) and flagged transferred-gas plants as non-applicable (`stoich_applicable = False`), reducing authentic floor breaches to **0**!
