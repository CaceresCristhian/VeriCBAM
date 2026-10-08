# VeriCBAM: Open Items & Decision Register

This register records methodological choices, unverified claims, credentials actions, and items pending user decisions.

---

## 1. Urgent Security Action
- [ ] **Rotate Copernicus Client Secret:**  
  *User must rotate the previously exposed Copernicus client secret.*  
  Although `Copernicus.txt` has been purged from git, current zips, and `.gitignore`, the secret was previously packaged in earlier archive versions. A new client secret should be generated in the Copernicus Data Space Ecosystem (CDSE) portal and the old one revoked. The code now reads `CDSE_CLIENT_ID` and `CDSE_CLIENT_SECRET` environment variables as primary configuration.

---

## 2. Decision on CO2 Definition (Item N3)
- **Status:** Pending User Decision at Checkpoint 1 (Default: Keep total CO2).
- **Trade-Off Analysis:**
  - **Option A (Current Default):** Total `Carbon dioxide (CO2)` from E-PRTR F1.4.
    - *Pros:* Maximizes data availability across European historical reporting (all 30 target facilities report total CO2; 177 plant-years complete). Aligns with gross combustion mass balance.
    - *Cons:* Under official CBAM rules (Implementing Regulation (EU) 2025/2547), biomass emissions are subject to specific zero-rating or sustainability criteria under RED II/III.
  - **Option B:** `Carbon dioxide (CO2) excluding biomass`.
    - *Pros:* Closer to CBAM regulatory accounting where sustainable biomass is exempted.
    - *Cons:* In E-PRTR, some facilities omit the excluding-biomass field or report 0, introducing potential missingness or reporting inconsistencies across historical years.
- **Current Position:** The codebase and benchmarks currently use total `Carbon dioxide (CO2)`, documented explicitly in `DATA_PROVENANCE.md` and `README.md`.

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
| **"~403 verification bodies globally hold accreditation"** | Softened to EU ETS accredited verifiers under AVR (EU) 2018/2067. | CBAM-specific verifier accreditation under Delegated Regulation (EU) 2025/2551 has not yet begun rolling out (expected late 2026). The 403 figure reflects existing EU ETS verifiers. Marked as *contextualized estimate*. |
| **"€50,000 to €150,000+ per site visit"** | Marked as industry estimate. | Derived from GMK Center (2024) steel sector studies and EC Impact Assessment SWD(2021) 643 for complex integrated BF-BOF overseas audits. Marked as *industry estimate*. |
| **"~12,000 EU import entities"** | Marked as estimated declarants. | Estimated scope of CBAM declarants under Commission transition reports. Marked as *estimate*. |
| **"Physical on-site audits are mandatory"** | Softened to *regulatory default*. | Under Implementing Regulation (EU) 2025/2546, physical on-site audits are the default for initial verifications, subject to strict conditions under which site visits may be waived. |

---

## 5. Offline Data and Environment Constraints
- **EEA Raw Tables:** The 2.2 GB raw EEA database zip is excluded from distribution archives. Cohort processing is verified reproducible offline from `benchmark_cohort_multipollutant.parquet`.
- **Sentinel-5P Satellite Ingestion:** No live API calls to CDSE or Planetary Computer are permitted during offline tests. Uses static offline cache in `data/03_satellite_cache/`.
