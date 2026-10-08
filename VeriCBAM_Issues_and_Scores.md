# VeriCBAM — Issues and Area Scores

## Issues

### RED — High Priority

1. **Remove the incorrect 10% regulatory materiality claim**
   - The project currently states that a 10% threshold represents CBAM materiality.
   - This should not be presented as a legal CBAM materiality rule.
   - The benchmark uses plant-level E-PRTR CO2 data, not product-level specific embedded emissions, so it cannot directly establish legal CBAM materiality.
   - If retained, 5% should be described only as a reference/sensitivity point, not as a legal CBAM materiality determination.

2. **Correct Regulation 2025/2551 classification**
   - The project currently refers to Regulation 2025/2551 as an Implementing Regulation.
   - It should be identified as **Commission Delegated Regulation (EU) 2025/2551**.

3. **Remove the steel 2 Mt/year fallback**
   - The benchmark generator currently falls back to `cap_mtpa = 2.0` when crude-steel capacity is missing or zero.
   - This invents capacity and can distort the stoichiometric bounds.
   - Missing or unsuitable capacity should instead lead to **Insufficient Evidence** or exclusion from the relevant benchmark.

4. **Separate the 326-case primary evaluation from the legacy 101-case benchmark**
   - The current primary evaluation contains 326 cases.
   - The older 101-case benchmark should be explicitly labelled as a legacy/regression/calibration benchmark.
   - Documentation should not imply that results from the 101-case benchmark are the main current generalization results.

5. **Resolve the test-suite status**
   - The project contains 19 tests.
   - In the reviewed environment, **13 passed and 6 failed**, with the failures caused by missing `pyarrow` when reading Parquet.
   - A clean environment using the declared requirements should be used to verify the full suite before claiming 19/19 tests pass.

6. **Avoid “fraud detection” / real CBAM violation validation claims**
   - The benchmark combines real facility data with controlled synthetic perturbations.
   - It therefore supports **controlled emissions inconsistency detection/screening**, not validation against real CBAM fraud or legal violations.

---

### ORANGE — Important Improvements

7. **Use “heterogeneous evidence” instead of “independent evidence”**
   - The evidence streams can be correlated.
   - The project should avoid implying statistical independence between the evidence sources.

8. **Fix the evidence-weight documentation**
   - Documentation currently describes weights as `w_i ∈ [0,1]`.
   - The implementation uses weights greater than 1 in some cases.
   - The documentation should reflect the actual implementation, e.g. `w_i > 0`, if that is the intended formulation.

9. **Implement or remove the bootstrap-CI claim**
   - `run_graded_evaluation.py` states that plant-level bootstrap confidence intervals are reported.
   - The reviewed implementation does not actually calculate/save those bootstrap confidence intervals.
   - Either implement them or remove the claim from the documentation/docstring.

10. **Correct the route-mismatch count**
    - Current benchmark data contain **9 usable route-mismatch cases**.
    - Some comments/documentation still state 11.
    - Align the comments and documentation with the actual benchmark.

11. **Clarify the CO2 variable choice**
    - `build_cohort.py` comments indicate a preference for `Carbon dioxide (CO2) excluding biomass`.
    - The implementation currently uses `Carbon dioxide (CO2)` as the primary `co2_tonnes` variable and stores excluding-biomass CO2 separately.
    - The project should explicitly document and justify the selected definition.

12. **Explain pooled historical normalization**
    - Historical z-scores/sigma are computed using pooled information across facilities/years.
    - This is not necessarily invalid, but the methodology should explain this choice.
    - For stricter generalization claims, normalization parameters could be recomputed within training folds.

13. **Replace “thermodynamic minimum” terminology**
    - Current documentation/code uses terms such as “thermodynamic minimum” and “absolute physical minimum”.
    - Prefer:
      - “stoichiometric lower bound”
      - “engineering/BAT reference”
      - “route-specific engineering lower bound”

14. **Moderate physical site-visit wording**
    - Avoid wording that implies the model can definitively replace or determine the need for a physical site visit.
    - Present the output as decision support for verification prioritization.

15. **Keep Sentinel-5P NO2 positioned as auxiliary evidence**
    - The current results show weak standalone discrimination.
    - The satellite component should remain an auxiliary/experimental evidence source rather than being presented as a strong plant-level emissions verifier.

16. **Avoid calling the Bayesian model “calibrated” without qualification**
    - The expert Bayesian model is an expert-parameterized evidence-fusion model.
    - Calibration should be discussed separately using appropriate calibration metrics or calibration methods.

17. **Clarify the role of the learned model**
    - The learned logistic model is currently the strongest empirical model in the benchmark.
    - Its results should be presented as learned predictive/evidence-fusion performance, not as evidence that the system has learned real-world CBAM fraud detection.

18. **Moderate reproducibility/checksum claims**
    - Reproducibility depends on access to the required source datasets and credentials.
    - Claims such as complete deterministic reproduction or validated API checksums should only be made where the implementation actually demonstrates them.

---

## Area Scores

| Area | Score |
|---|---:|
| Proposal alignment | 4.7 / 5 |
| Research idea | 5.0 / 5 |
| Data foundation | 4.2 / 5 |
| Benchmark | 4.5 / 5 |
| Physical modelling | 3.7 / 5 |
| Historical | 4.7 / 5 |
| Satellite implementation | 4.3 / 5 |
| Satellite interpretation | 5.0 / 5 |
| Bayesian fusion | 3.5 / 5 |
| Learned fusion | 5.0 / 5 |
| UQ / calibration | 3.5 / 5 |
| Statistical validation | 3.7 / 5 |
| Reproducibility | 3.5 / 5 |
| Testing | 3.0 / 5 |
| Documentation | 3.5 / 5 |
| Regulatory accuracy | 3.0 / 5 |
| Security | 4.5 / 5 |
| UI | 4.5 / 5 |
| **Overall** | **8.8 / 10** |

## Priority Summary

### RED
- Incorrect 10% CBAM materiality claim
- Incorrect classification of Regulation 2025/2551
- Steel 2 Mt/year fallback
- 326 vs. 101 evaluation distinction
- Test-suite verification
- Avoid real-world fraud/legal-violation claims

### ORANGE
- Heterogeneous vs. independent evidence
- Evidence-weight documentation
- Bootstrap confidence intervals
- Route-mismatch count
- CO2 definition
- Historical normalization methodology
- Thermodynamic terminology
- Site-visit wording
- Satellite positioning
- Bayesian calibration wording
- Learned-model interpretation
- Reproducibility/checksum claims
