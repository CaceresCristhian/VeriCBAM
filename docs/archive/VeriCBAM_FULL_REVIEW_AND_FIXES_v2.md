> ARCHIVED: Historical document, superseded by README.md and current project codebase.

# VeriCBAM — Full Project Review and Fixes v2

**Review version:** v2  
**Review date:** 7 October 2026  
**Project:** VeriCBAM — Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment  
**Reviewed package:** Updated `Capstone(1).zip`  
**Purpose:** Detailed technical, methodological, scientific, regulatory, reproducibility, and documentation review of the updated VeriCBAM capstone.

---

# 1. Executive Summary

The updated VeriCBAM package is **substantially stronger than the previous version**.

Several of the most important weaknesses identified in the previous review have been addressed:

- the silent synthetic Sentinel-5P fallback has been removed;
- real Sentinel-5P processing is now explicitly distinguished from unavailable data;
- the evidence-fusion engine now actually uses evidence weights;
- risk and evidence confidence are separated;
- an explicit `Insufficient Evidence` outcome exists;
- the historical anomaly calculation now uses an actual z-score;
- the benchmark label has been renamed away from `ground_truth_inconsistent_label`;
- the benchmark now explicitly distinguishes 177 available facility-year observations from 180 theoretical combinations;
- a controlled 101-case benchmark and five-model ablation are present;
- post-hoc calibration experiments using Brier score, ECE, Platt scaling, and isotonic regression have been added;
- the application form is substantially more complete;
- the repository now has stronger documentation, requirements, tests, experiments, and results.

The project is therefore no longer merely a promising architecture. It has become a **credible capstone prototype with a coherent experimental story**.

However, the updated version still has important problems.

The most important remaining issues are:

1. **The documentation claims a broader satellite system than the code actually implements.**
   - Sentinel-5P NO₂ is implemented.
   - Sentinel-5P CO is not implemented.
   - Sentinel-2 SWIR processing is not implemented.
2. **The benchmark's production variable is not fully independent of emissions**, despite documentation describing it as independent.
3. **The 101 benchmark cases are controlled/synthetic cases, not real CBAM violation labels.**
4. **The reported calibration is calibration against the controlled benchmark, not real-world CBAM probability calibration.**
5. **The excellent Model E results are likely partly explained by the controlled structure of the benchmark and must not be generalized to real-world CBAM performance.**
6. **The current ZIP does not reproduce the documented 17/17 test result. Running the supplied package produced 13 passing and 4 failing tests.**
7. **Required processed data files are not included in the ZIP, which prevents clean reproduction of the benchmark and ablation experiments.**
8. **Some regulatory references need correction, particularly the distinction among EU Implementing Regulations 2025/2546, 2025/2547, and 2025/2551.**
9. **Cement and steel terminology still sometimes describes engineering assumptions as thermodynamic minima.**
10. **Route-mismatch cases should not be called “verified misclassifications”; they are controlled route-mismatch cases based on facilities with documented technology.**
11. **Facility-grouped validation should be added to address dependence among multiple cases generated from the same facilities.**
12. **Expert-defined likelihood ratios need sensitivity analysis and should not be described as empirically learned Bayesian likelihoods.**

### Current overall assessment

**Approximate score: 8.2/10**

With the high-priority issues fixed, the project could realistically reach approximately **9/10 capstone quality**.

The main recommendation is now **not to expand the project horizontally**. Instead, tighten the scientific claims, align documentation with implementation, strengthen benchmark independence and validation, and make the package genuinely reproducible.

---

# 2. Overall Assessment

| Area | Previous version | Updated version | Assessment |
|---|---:|---:|---|
| Research question | Strong | Very strong | Keep |
| Project positioning | Good | Very strong | Keep |
| Repository structure | Weak/partial | Stronger | Continue cleanup |
| Satellite architecture | Major concern | Much better | Scope still overstated |
| Synthetic satellite fallback | Critical issue | Fixed | Strong improvement |
| Evidence fusion | Prototype | Much stronger | Strong |
| Risk/confidence separation | Partial | Fixed | Strong |
| Insufficient Evidence | Missing/weak | Implemented | Strong |
| Benchmark design | Major issues | Improved | Independence still problematic |
| Calibration | Not implemented | Implemented | Must qualify interpretation |
| Testing | Incomplete | Improved | ZIP currently fails 4 tests |
| Application form | Incomplete | Mostly fixed | Signature/date remain |
| Scientific terminology | Several problems | Improved | Still needs correction |
| Reproducibility | Weak | Improved | Data/package gap remains |
| Regulatory framing | Some errors | Better | Regulation references need correction |

---

# 3. Critical Finding #1 — Sentinel-5P Synthetic Fallback Has Been Fixed

## Previous problem

The previous version of `src/satellite/copernicus_client.py` could silently generate synthetic atmospheric observations when real data were unavailable.

That created a major scientific provenance problem because downstream results could appear to be based on Sentinel-5P observations when they were actually generated by software.

## Updated situation

The updated client explicitly states that there is deliberately **no synthetic or simulated fallback**.

The implementation now records provenance information including:

- `data_source`
- `real_sentinel5p`
- granule ID
- orbit information
- processor version
- source URL
- extraction parameters
- QA threshold
- observation date
- cloud fraction

This is a major improvement.

## Assessment

**Status: FIXED**

The satellite pipeline can now distinguish unavailable real observations from simulated data rather than silently substituting synthetic observations.

## Recommended wording

Use:

> “A real Sentinel-5P processing pipeline is implemented. When valid real observations are unavailable, the system reports insufficient evidence rather than silently generating synthetic observations.”

Do not claim that every reported experiment necessarily used real Sentinel-5P observations unless the experiment provenance confirms this.

---

# 4. Critical Finding #2 — Satellite Scope Is Still Broader in the Documentation Than in the Code

This is currently one of the most important remaining issues.

## Documentation claims

The project documentation describes a satellite component involving:

- Sentinel-5P TROPOMI NO₂
- Sentinel-5P CO
- Sentinel-2 SWIR
- B11/B12
- related operational indicators

## Actual implementation

The source code currently demonstrates:

### Implemented

- Sentinel-5P
- TROPOMI
- tropospheric NO₂
- real observation extraction
- QA filtering
- facility/background comparison
- anomaly/activity scoring

### Not demonstrated as implemented

- Sentinel-5P CO processing
- Sentinel-2 processing
- Sentinel-2 B11/B12 processing
- Sentinel-2 NHI calculation
- integrated NO₂ + CO + SWIR satellite fusion

## Recommendation

Unless these components are actually implemented and tested, remove them from the list of implemented capabilities.

Use:

> “Sentinel-5P TROPOMI tropospheric NO₂ is implemented as the primary satellite-derived operational activity indicator.”

Move CO and Sentinel-2 SWIR to:

> “Planned/future extensions.”

## Status

**Priority: RED — must fix documentation or implement the missing modalities.**

---

# 5. Critical Finding #3 — The Satellite Indicator Must Not Be Presented as Direct CO₂ Measurement

The implemented satellite logic compares:

- facility-region NO₂
- regional background NO₂
- robust variability

and derives an enhancement/anomaly measure.

This is useful as an **operational activity indicator**, but it is not a direct measurement of facility CO₂ emissions.

## Correct interpretation

The satellite component can provide evidence such as:

> “Observed atmospheric NO₂ activity is inconsistent with the expected operational pattern.”

It should not be described as:

> “Satellite-measured facility CO₂ emissions.”

## Recommended terminology

Use:

- operational activity indicator
- NO₂ activity anomaly
- atmospheric activity consistency
- facility-background NO₂ contrast
- satellite-derived operational evidence

Avoid:

- direct CO₂ measurement
- satellite verification of declared CO₂
- direct emissions quantification

unless a physically justified emissions inversion is actually implemented and validated.

---

# 6. Critical Finding #4 — Benchmark Production Is Still Partly Circular

This is one of the most important remaining methodological problems.

The benchmark documentation describes production/activity as independent evidence.

However, the generator contains logic equivalent to:

```python
annual_production = max(
    100000.0,
    min(max_cap_prod, round(hist_mean / exp_intensity, -3))
)
```

The important component is:

```python
hist_mean / exp_intensity
```

Thus historical emissions are used to derive estimated production.

## Why this is a problem

The scientific argument is supposed to be:

```text
Independent activity evidence
        +
Declared emissions
        ↓
Consistency assessment
```

But if activity is partly derived from historical emissions, the benchmark is closer to:

```text
Historical emissions
        ↓
Estimated production
        ↓
Synthetic declaration
        ↓
Consistency assessment
```

That weakens the claimed independence between evidence sources.

## Recommended solution

Prefer:

```text
Independent nameplate capacity
        +
independent utilization assumption
        ↓
Activity estimate
```

or use actual independent production/activity data.

If real production data are unavailable, explicitly define the activity variable as a controlled synthetic assumption:

> “Production activity is synthetically specified using independent facility capacity and controlled utilization assumptions.”

Do not call it empirically independent if it is calculated from historical emissions.

## Status

**Priority: RED**

---

# 7. Critical Finding #5 — Route Mismatch Cases Are Controlled, Not Verified Real Misclassifications

The benchmark constructs route mismatch cases by assigning a false/declared route different from the facility's documented route.

For example, a facility may have a documented BF-BOF route while the controlled case assigns a different declared route.

This is useful for testing.

However, the mismatch itself is synthetic.

## Incorrect wording

> “11 verified route misclassifications”

## Better wording

> “11 controlled route-mismatch cases constructed from facilities with independently documented production routes.”

Or simply:

> “11 controlled route-mismatch cases.”

## Why this matters

The facility technology may be supported by external evidence, but the actual declaration error is created by the benchmark.

Therefore:

```text
Real facility technology
+
Synthetic declaration perturbation
=
Controlled route-mismatch case
```

## Status

**Priority: RED — terminology correction.**

---

# 8. Critical Finding #6 — Historical Anomaly Calculation Has Been Improved

The previous version claimed historical anomalies such as “>3 sigma” without actually calculating the z-score.

The updated version calculates a historical z-score using:

```python
actual_drop_z = (
    declared_drop_co2 - hist_mean
) / hist_std
```

This is a genuine improvement.

## Assessment

**Status: FIXED**

The benchmark now contains an actual statistical anomaly measure rather than merely applying a fixed reduction factor and labeling it as a sigma event.

## Remaining issue

The project uses 2018–2023 data while the fusion model refers to a five-year historical window.

Make the temporal definition explicit.

A strong setup would be:

```text
2018–2022
    ↓
historical profile
    ↓
predict/evaluate
2023
```

This avoids accidentally using the evaluation year as part of its own historical baseline.

---

# 9. Critical Finding #7 — Bayesian Evidence Fusion Is Now Better Implemented

The previous version had a `weight` field that was not actually used in the posterior calculation.

The updated engine incorporates evidence weights into the evidence aggregation.

The conceptual structure is approximately:

```text
logit(P(H|E))
=
logit(P(H))
+
Σ weight × confidence × log(LR)
```

This is much more coherent.

## Positive changes

The project now distinguishes:

### Risk

> estimated inconsistency probability/risk

from:

### Evidence confidence

> confidence in the quality/availability of the evidence supporting that risk.

This separation is conceptually important.

## Assessment

**Status: SUBSTANTIALLY FIXED**

---

# 10. Critical Finding #8 — The Model Is Still Expert-Parameterized, Not Fully Empirically Bayesian

The model uses manually specified likelihood ratios such as:

- stoichiometry LRs
- satellite LRs
- historical LRs
- registry LRs
- route LRs

These are expert-defined model parameters.

They are not directly estimated from large empirical distributions of:

```text
P(E | H)
P(E | not H)
```

Therefore, the safest terminology is:

> **Expert-parameterized probabilistic evidence-fusion model**

or:

> **Probabilistic evidence-fusion prototype**

rather than:

> Fully empirically calibrated Bayesian model.

## Important distinction

The mathematical structure is Bayesian-inspired and probabilistic.

The parameter estimation is not fully data-driven.

That is acceptable for a capstone if clearly disclosed.

---

# 11. Critical Finding #9 — The 8% Prior Must Be Treated as an Assumption/Sensitivity Parameter

The project uses a prior near:

```text
P(H) = 0.08
```

This should not be presented as an empirically established prevalence unless a defensible source exists.

## Recommended approach

Treat it as a model assumption and run sensitivity analysis:

```text
2%
5%
8%
12%
15%
```

Then report whether:

- ranking remains stable;
- high-risk cases remain high-risk;
- threshold decisions change;
- calibration changes.

This makes the model more robust.

---

# 12. Critical Finding #10 — Calibration Is Valuable but Must Be Described Correctly

The updated project now reports:

### Raw

- Brier score ≈ 0.0414
- ECE ≈ 0.0625

### Platt scaling

- Brier score ≈ 0.0284
- ECE ≈ 0.0523

### Isotonic regression

- Brier score ≈ 0.0281
- ECE ≈ 0.0459

This is a useful addition.

The five-fold out-of-fold approach is also preferable to fitting and evaluating calibration on the same cases.

## But the labels are controlled benchmark labels

Therefore the correct conclusion is:

> “Calibration was evaluated against controlled benchmark labels.”

Not:

> “The model is calibrated for real-world CBAM inconsistency probabilities.”

## Important limitation

There are no publicly available large-scale labels representing real CBAM declaration inconsistencies with which to establish real-world calibration.

Therefore real-world calibration remains a limitation.

---

# 13. Critical Finding #11 — Do Not Interpret 80% Risk as an 80% Real-World Probability

Avoid statements such as:

> “An 80% risk rating means that 80% of such declarations are actually inconsistent.”

The current evidence does not support that interpretation.

A more defensible statement is:

> “The reported probability is calibrated relative to the controlled benchmark under the specified model assumptions.”

That distinction should appear in:

- thesis
- README
- dashboard
- methodology
- limitations
- conclusion

---

# 14. Critical Finding #12 — The Benchmark Contains Multiple Cases per Facility

The benchmark contains approximately:

- 30 baseline cases
- 30 physical violations
- 30 historical anomalies
- 11 route mismatch cases

for a total of 101 controlled cases.

But many cases originate from the same 30 facilities.

Therefore:

```text
101 cases
≠
101 independent facilities
```

This matters for:

- ROC-AUC
- PR-AUC
- F1
- calibration
- cross-validation
- generalization claims

## Recommended solution

Add grouped evaluation using:

```text
GroupKFold
group = facility_id
```

or:

```text
Leave-One-Facility-Out
```

Then evaluate whether the model generalizes to facilities not used in benchmark construction.

## Priority

**HIGH**

This is one of the most valuable remaining experiments.

---

# 15. Critical Finding #13 — Model E Results Are Excellent but Need Careful Interpretation

Current Model E results are approximately:

- Precision = 1.000
- Recall = 0.901
- F1 = 0.948
- ROC-AUC = 0.9948
- PR-AUC = 0.9979
- FPR = 0

These are extremely strong.

They are also likely influenced by the structure of the controlled benchmark.

## The correct interpretation

Do not say:

> “VeriCBAM achieves 99.48% real-world CBAM inconsistency detection.”

Instead say:

> “The multimodal model achieved very strong discrimination on the controlled benchmark.”

Then explicitly explain:

- cases were deliberately constructed;
- some evidence streams are directly associated with the perturbation type;
- the benchmark does not represent the prevalence or complexity of real CBAM violations;
- facilities are repeated across cases.

This is still a valuable result.

---

# 16. Critical Finding #14 — Model D Is Scientifically Interesting

The historical model reports approximately:

- ROC-AUC ≈ 0.986
- but thresholded F1 = 0
- precision = 0
- recall = 0

This is useful rather than embarrassing.

It demonstrates that:

> ranking performance and threshold performance are not the same.

The model can rank cases strongly while its probability scale is poorly aligned with a 0.5 classification threshold.

This supports the need for:

- calibration
- threshold selection
- decision analysis
- confidence-aware triage

This should be discussed in the thesis.

---

# 17. Critical Finding #15 — Model C Provides a Useful Negative Result

The satellite-only model has weak discrimination, approximately:

- ROC-AUC ≈ 0.517
- F1 = 0

This does not mean:

> “Satellite remote sensing does not work.”

The scientifically appropriate interpretation is:

> “The tested Sentinel-5P NO₂ operational indicator alone provides weak discrimination of the controlled inconsistency categories.”

This can actually strengthen the multimodal-fusion argument:

```text
Individual evidence
       ↓
limited
       ↓
Evidence fusion
       ↓
stronger
```

The result supports the thesis question rather than necessarily undermining the project.

---

# 18. Critical Finding #16 — Satellite Spatial Methodology Can Be Improved

The current method uses:

- a facility-centered near-field region;
- a regional background annulus;
- facility/background contrast;
- robust variability;
- anomaly z-score.

This is reasonable for a prototype.

However, atmospheric transport means the highest concentration may not occur directly around the facility.

The project already extracts wind information such as:

- `wind_u`
- `wind_v`

but does not appear to use wind direction to rotate or shift the analysis region.

## Future improvement

A stronger method would use:

```text
Facility
   ↓
Wind direction
   ↓
Downwind sector
   ↓
Plume/activity region
   ↓
Upwind/background comparison
```

This does not have to be implemented for the capstone if time is limited.

Document it as a limitation/future extension.

---

# 19. Critical Finding #17 — Cement Terminology Still Needs Correction

The cement model contains language around:

> thermodynamic minimum

and:

> thermodynamic limits

This is too strong for the current implementation.

The model combines:

1. a stoichiometric calcination relationship;
2. an assumed energy-consumption benchmark;
3. fuel emissions.

The stoichiometric component can be framed as a lower bound under assumptions.

The energy benchmark is an engineering/BAT-style benchmark, not a fundamental thermodynamic minimum.

## Recommended terminology

Use:

> **Stoichiometric process-emissions lower bound**

and:

> **Engineering/BAT energy benchmark**

and:

> **Model-based lower bound under specified assumptions**

Avoid:

> Thermodynamic minimum

unless the value is actually derived from a formal thermodynamic minimum calculation.

---

# 20. Critical Finding #18 — Steel Route Values Are Engineering Assumptions

Values for:

- BF-BOF
- DRI-NG
- DRI-H₂
- Scrap-EAF

are useful for route-aware screening.

But they should not automatically be described as absolute thermodynamic minima.

## Better terminology

Use:

> route-specific engineering lower bound

or:

> route-specific reference emissions intensity

depending on how the value is constructed.

Also document:

- source;
- year;
- system boundary;
- assumed energy source;
- assumed feedstock;
- whether Scope 1 only or broader emissions are represented.

---

# 21. Critical Finding #19 — Physical Overrule Is Still Too Absolute

The fusion engine can strongly override the probability when stoichiometric violation is detected.

Even a posterior near 1.0 should not be interpreted as literal physical impossibility unless all assumptions are certain.

Physical feasibility depends on:

- composition;
- production quantity;
- production route;
- system boundary;
- carbon capture;
- fuel;
- scrap ratio;
- measurement uncertainty;
- accounting conventions.

## Recommended UI language

Instead of:

> Physical Impossibility Detected

use:

> **Physical feasibility violation under model assumptions**

Instead of:

> Physically Verified

use:

> **Physically feasible under specified assumptions**

---

# 22. Critical Finding #20 — E-PRTR Is Correctly No Longer Treated as Ground Truth

The updated project explicitly states that E-PRTR is not ground truth for CBAM non-compliance.

This is correct.

Use terminology such as:

> historical regulatory reference data

or:

> independent historical emissions reference

rather than:

> verified CBAM truth

unless the underlying data have the relevant assurance status.

---

# 23. Critical Finding #21 — 177 vs 180 Is Correctly Explained

The project now distinguishes:

```text
30 facilities × 6 years = 180 theoretical facility-year combinations
```

from:

```text
177 available observations
```

with three missing facility-year combinations.

This is much better than implying a complete panel.

Keep this explanation.

Also document exactly which three combinations are missing.

---

# 24. Critical Finding #22 — Application Form Is Mostly Fixed

The updated application form now contains:

- first name;
- surname;
- matriculation number;
- M.Sc. Data Science;
- project title;
- project description;
- Berlin/date.

This addresses the major incompleteness identified previously.

## Remaining actions

### Signature

The signature field remains blank.

That is acceptable during drafting but should be completed before formal submission if required.

### Date

The form currently contains:

> Berlin, 12.10.2026

The review date is 7 October 2026.

If the form is submitted before 12 October, use the actual signing/submission date.

---

# 25. Critical Finding #23 — Application Description Still Overstates Satellite Implementation

The application currently describes the satellite component using:

- Sentinel-5P NO₂/CO
- Sentinel-2 SWIR

but the implementation reviewed demonstrates Sentinel-5P NO₂.

## Recommended application wording

Use:

> “A Copernicus Earth Observation processing pipeline is implemented for Sentinel-5P TROPOMI tropospheric NO₂ observations, providing a satellite-derived operational activity indicator. Additional Sentinel-2/CO modalities are planned extensions rather than current implemented components.”

If you later implement them, update the statement accordingly.

---

# 26. Regulatory Review

The regulatory motivation of the project is broadly sound.

The European Commission currently describes the definitive CBAM regime as applying from **1 January 2026**.

The verification framework is also now operationally relevant:

- accreditation began during 2026;
- accredited verifiers can register;
- first verification reports can be issued from January 2027;
- first annual declaration for 2026 emissions is due in 2027.

These facts support the timing and relevance of VeriCBAM.

---

# 27. Critical Regulatory Correction — Regulation Numbers

The project currently risks conflating several Commission Implementing Regulations.

The current Commission framework distinguishes:

### Commission Implementing Regulation (EU) 2025/2546

Relevant to:

> verification principles / verification rules.

### Commission Implementing Regulation (EU) 2025/2551

Relevant to:

> accreditation and verification.

### Commission Implementing Regulation (EU) 2025/2547

Relevant to:

> methods for calculation of embedded emissions.

Therefore:

**Do not cite 2025/2547 as the verification regulation.**

This should be corrected throughout:

- README;
- project plan;
- proposal;
- application;
- thesis;
- dashboard;
- references.

---

# 28. CBAM Default-Value Markups

The project's discussion of the temporary/default-value markups is broadly consistent with the current framework for relevant sectors:

- 2026: 10%
- 2027: 20%
- 2028 onward: 30%

Fertiliser has separate treatment.

Keep the values, but make sure the exact regulatory source and applicable goods/sectors are clearly stated.

---

# 29. Verifier Bottleneck Numbers Need Careful Interpretation

The project uses figures around:

- 12,000 economic operators/applications;
- 4,100 authorised declarants;
- approximately 403 accredited verifiers.

These figures can illustrate the emerging verification-capacity issue.

However:

```text
12,000 applications
≠
12,000 installations
```

One declarant can have multiple suppliers/facilities.

Therefore do not construct a simplistic:

> 12,000 installations / 403 verifiers

ratio.

Use the numbers only as contextual evidence of the scale of the emerging verification workload.

---

# 30. Audit Cost Claims Need Stronger Sources

The project contains cost ranges such as:

- €50,000–€150,000+
- €75,000–€210,000+

These exact figures require precise source tracing.

The general concept of verification cost and workload is reasonable, but the project currently risks overstating the evidentiary basis for these exact ranges.

## Recommendation

Either:

1. provide an exact source/page/table for every cost range; or
2. remove the exact figures from the central academic argument.

The project does not depend on those numbers.

---

# 31. Technology Registry — Add Provenance Metadata

The technology registry currently contains useful information such as:

- facility;
- sector;
- country;
- technology;
- capacity;
- source;
- source URL;
- notes.

Add, where possible:

```text
facility_id
technology_route
capacity
source
source_type
source_publication_date
access_date
confidence
mapping_method
```

Especially document:

> How was the facility ID mapped to the technology source?

That mapping is itself an evidence-processing step and should be reproducible.

---

# 32. Critical Finding #24 — The ZIP Does Not Currently Reproduce the Claimed 17/17 Tests

The updated documentation states that:

> 17/17 tests pass.

However, executing the supplied ZIP currently produced:

> **13 passing, 4 failing**

The four failures were:

1. `test_technology_registry_completeness`
2. `test_controlled_benchmark_structure`
3. `test_ablation_study_execution`
4. `test_probability_calibration_execution`

The first three failures are caused by required processed data files not being included in the ZIP.

The fourth is associated with the `pyarrow` dependency in the execution environment, although `requirements.txt` does declare `pyarrow>=14.0.0`.

## Important distinction

This does not necessarily mean the code is broken.

It means the **distributed project package is not yet self-contained/reproducible**.

Do not claim:

> 17/17 tests pass in the submitted package

until this is demonstrated in a clean environment.

---

# 33. Reproducibility Problem — Missing Processed Data

The README expects processed files such as:

```text
data/02_processed/benchmark_cohort.parquet
data/02_processed/facility_technology_registry.csv
data/02_processed/controlled_perturbation_benchmark.parquet
```

and satellite cache data.

These files are not present in the uploaded ZIP.

Therefore the benchmark and ablation cannot be reproduced directly from the package.

## Solution A — Include processed data

Include the required processed datasets if licensing and size allow.

## Solution B — Provide deterministic generation scripts

If raw data cannot be redistributed, provide scripts that rebuild the processed files from the permitted sources.

For example:

```text
python scripts/build_reference_cohort.py
python scripts/build_satellite_cache.py
python scripts/build_technology_registry.py
python scripts/build_controlled_benchmark.py
```

Then document:

- source;
- version;
- access date;
- filtering;
- transformations;
- output schema;
- dataset hash.

---

# 34. Documentation Is Still Slightly Ahead of the Repository

The README and project plan describe a repository structure that is broader than the actual distributed package.

This was a problem in the previous version and is improved but not fully eliminated.

## Recommended documentation rule

Every component in the documentation should be labeled as exactly one of:

```text
IMPLEMENTED
GENERATED RESULT
EXTERNAL DATA
PLANNED
```

Avoid presenting planned components inside an “implemented repository” tree.

---

# 35. Recommended Repository Structure

A strong final structure would be:

```text
VeriCBAM/
│
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── docs/
│   ├── VeriCBAM_Project_Plan.md
│   ├── DATA_PROVENANCE.md
│   ├── METHODOLOGY.md
│   ├── LIMITATIONS.md
│   ├── EXPERIMENTS.md
│   └── REGULATORY_REFERENCES.md
│
├── config/
│   ├── model_config.yaml
│   ├── satellite_config.yaml
│   └── benchmark_config.yaml
│
├── data/
│   ├── 01_raw/
│   ├── 02_processed/
│   └── 03_satellite_cache/
│
├── experiments/
│   ├── run_ablation.py
│   ├── run_calibration.py
│   ├── run_grouped_validation.py
│   └── run_sensitivity.py
│
├── tests/
│
├── src/
│   ├── core/
│   ├── satellite/
│   ├── benchmark/
│   ├── data_loaders/
│   └── ui/
│
└── results/
    ├── tables/
    ├── figures/
    └── reports/
```

---

# 36. Evidence Hierarchy

The project should clearly communicate the following evidence hierarchy:

## Level 1 — Physical consistency

Question:

> Is the declaration physically feasible under explicit assumptions?

Examples:

- stoichiometric bounds;
- route-specific engineering bounds;
- production/emissions relationship.

## Level 2 — Operational consistency

Question:

> Is observed activity consistent with the declared production/emissions pattern?

Example:

- Sentinel-5P NO₂ operational indicator.

## Level 3 — Historical consistency

Question:

> Is the declaration consistent with the facility's historical behavior?

Examples:

- z-score;
- historical trajectory;
- abnormal year-over-year changes.

## Level 4 — Multimodal consistency

Question:

> Do independent evidence streams jointly support or contradict the declaration?

This is where VeriCBAM's main contribution lies.

---

# 37. Final Architecture

The recommended final architecture is:

```text
CBAM Declaration
      │
      ▼
Document / Structured Data Extraction
      │
      ├─────────────────────┐
      ▼                     ▼
Physical Model         Operational Evidence
      │                     │
      │                Sentinel-5P NO₂
      │                     │
      └──────────┬──────────┘
                 ▼
       Historical Facility Profile
                 │
                 ▼
        Technology / Registry Evidence
                 │
                 ▼
        Evidence Fusion Engine
                 │
          ┌──────┴──────┐
          ▼             ▼
       Risk        Evidence Confidence
          │             │
          └──────┬──────┘
                 ▼
        Uncertainty Analysis
                 │
                 ▼
       Explainable Evidence Graph
                 │
                 ▼
       Human Verification Triage
```

The central principle should remain:

> **The system assembles, quantifies, and explains evidence; it does not independently certify legal compliance.**

---

# 38. LLM Role

Do not add an LLM merely for complexity.

If an LLM is used, it should:

### Do

- interpret declaration documents;
- summarize evidence;
- explain why a case was flagged;
- retrieve supporting evidence;
- generate human-readable audit narratives;
- identify missing information;
- organize evidence into an evidence graph.

### Do not

- calculate stoichiometry;
- generate satellite measurements;
- invent observations;
- assign the core probability;
- override physical constraints;
- decide legal compliance;
- replace an accredited verifier.

The deterministic/scientific components should remain responsible for quantitative calculations.

---

# 39. Human-in-the-Loop Design

The final system should be framed as:

```text
Machine
  ↓
Evidence collection
  ↓
Quantification
  ↓
Risk prioritization
  ↓
Explanation
  ↓
Human verifier
```

not:

```text
Machine
  ↓
Legal compliance decision
```

This distinction is central to the project's credibility.

---

# 40. Dashboard Terminology

Recommended replacements:

| Current/Problematic | Recommended |
|---|---|
| Physically Verified | Physically feasible under specified assumptions |
| Physical Impossibility Detected | Physical feasibility violation under model assumptions |
| Route Verified | No route inconsistency detected under current evidence |
| Verified Emissions | Reference emissions / reported emissions |
| Satellite Emissions Measurement | Satellite-derived operational activity indicator |
| CBAM Violation | Potential inconsistency / verification priority |
| Compliance Decision | Decision-support assessment |
| Ground Truth | Benchmark label / controlled benchmark label |
| Real Violation | Controlled inconsistency case |
| Certified Verification Dossier | Evidence assessment dossier |

---

# 41. Risk and Confidence Must Remain Separate

A key design principle:

```text
Risk ≠ Confidence
```

Example:

> Risk = 0.85  
> Evidence confidence = 0.42

This should mean:

> The model sees substantial inconsistency risk, but the evidence supporting that estimate is incomplete or uncertain.

This is much better than producing a single opaque number.

---

# 42. Insufficient Evidence Must Remain a First-Class Outcome

The system should explicitly return:

> **Insufficient Evidence**

when:

- satellite observations are unavailable;
- document extraction is incomplete;
- historical coverage is insufficient;
- registry mapping is uncertain;
- evidence streams conflict without enough information;
- uncertainty becomes too large.

Do not force every case into:

```text
low risk
high risk
```

---

# 43. Recommended Experimental Program

## Experiment 1 — Baseline

Declaration-only model.

## Experiment 2 — Physical evidence

Stoichiometric/engineering evidence.

## Experiment 3 — Satellite evidence

Sentinel-5P NO₂ activity indicator.

## Experiment 4 — Historical evidence

Historical facility trajectory.

## Experiment 5 — Multimodal fusion

Combined evidence.

## Experiment 6 — Calibration

Compare:

- raw;
- Platt;
- isotonic.

Metrics:

- Brier;
- ECE;
- reliability curve.

## Experiment 7 — Prior sensitivity

Test:

```text
2%
5%
8%
12%
15%
```

## Experiment 8 — LR sensitivity

Test:

```text
0.5 × LR
0.75 × LR
1.0 × LR
1.25 × LR
1.5 × LR
```

## Experiment 9 — Facility-grouped validation

Use:

```text
GroupKFold
```

or:

```text
Leave-One-Facility-Out
```

This should be the next major experiment.

---

# 44. Recommended Benchmark Structure

A common benchmark table should contain:

```text
case_id
facility_id
sector
year
original_emissions
declared_emissions
production
production_route
declared_route
benchmark_label
stoich_margin
stoich_violation
satellite_zscore
satellite_confidence
satellite_available
historical_zscore
historical_confidence
capacity_ratio
registry_confidence
perturbation_type
perturbation_magnitude
```

All five ablation models should consume the same benchmark cases.

This makes the comparison much stronger.

---

# 45. Recommended Controlled Case Types

Keep:

### Baseline

No perturbation.

### Physical violation

Declaration exceeds model-based physical/engineering feasibility.

### Historical anomaly

Declaration deviates abnormally from the historical trajectory.

### Route mismatch

Declared route differs from independently documented facility route.

Potential future cases:

### Satellite inconsistency

Controlled operational activity signal inconsistent with declared production.

### Multi-source contradiction

Two or more independent evidence streams disagree.

### Missing evidence

One or more critical streams unavailable.

The latter two would be particularly useful for testing the `Insufficient Evidence` logic.

---

# 46. Limitations Section Required for the Thesis

The final thesis should explicitly acknowledge:

## 46.1 Controlled benchmark

The 101 cases are synthetic/controlled perturbations, not observed regulatory violations.

## 46.2 No real CBAM violation labels

The model cannot currently be validated against a large public dataset of confirmed CBAM inconsistencies.

## 46.3 Satellite limitations

Sentinel-5P NO₂:

- is not direct CO₂;
- is affected by atmospheric transport;
- depends on observation availability;
- has spatial-resolution limitations;
- can be influenced by nearby sources and weather.

## 46.4 Physical model assumptions

Bounds depend on:

- composition;
- route;
- system boundary;
- production;
- energy source;
- carbon capture;
- process assumptions.

## 46.5 Expert-defined LRs

Likelihood ratios are not yet learned from a large labeled dataset.

## 46.6 Calibration limitation

Calibration is evaluated on the controlled benchmark rather than real-world CBAM cases.

## 46.7 Historical missingness

The 177 observations are not a complete 180-observation panel.

## 46.8 Generalization

30 facilities are sufficient for a capstone prototype but not for broad industrial generalization.

---

# 47. Recommended Data Provenance Document

Create:

```text
docs/DATA_PROVENANCE.md
```

For every dataset, document:

```text
Dataset:
Source:
URL:
Version:
Access date:
License:
Variables used:
Filtering:
Transformations:
Missing-data handling:
Spatial processing:
Temporal processing:
Known limitations:
Hash:
```

For satellite data additionally document:

```text
Satellite:
Instrument:
Product:
Collection:
Processor:
QA threshold:
Spatial filter:
Background method:
Wind data:
Observation count:
```

---

# 48. Recommended Status Terminology

The project should distinguish four maturity states.

## Implemented

Code exists and has been tested.

## Operational

The component processes real inputs end-to-end.

## Validated

The component has quantitative evaluation against an appropriate benchmark.

## Calibrated

The probability outputs have been evaluated for calibration on an appropriate labeled dataset.

A component may be:

> implemented but not operational

or:

> operational but not validated

or:

> validated on controlled data but not externally validated.

This language will make the thesis much more rigorous.

---

# 49. Final Recommended Research Question

The strongest current version is:

> **To what extent can independent physical, observational, historical, and documentary evidence be fused into a calibrated decision-support model that identifies inconsistent CBAM emissions declarations more reliably than isolated evidence sources?**

If you want to be even more conservative because the calibration is benchmark-specific:

> **To what extent can independent physical, observational, historical, and documentary evidence be fused into an explainable decision-support model that identifies controlled CBAM emissions inconsistencies more reliably than isolated evidence sources?**

The second wording is safest for the current evidence.

---

# 50. Recommended Contribution Statement

Use:

> **VeriCBAM proposes a multimodal, explainable evidence-fusion framework that combines deterministic physical constraints, satellite-derived operational indicators, historical facility behavior, and technology/declaration information to produce inconsistency risk and evidence-confidence estimates for CBAM-related emissions assessment.**

Do not claim:

> autonomous CBAM certification.

Do not claim:

> replacement of accredited verification.

Do not claim:

> direct measurement of declared CO₂ from Sentinel-5P.

---

# 51. Recommended Final Thesis Story

The complete academic narrative should be:

```text
CBAM declarations
        ↓
Difficult to independently assess
        ↓
Evidence is heterogeneous
        ↓
Physical evidence
+
Satellite operational evidence
+
Historical evidence
+
Technology/document evidence
        ↓
Evidence Fusion
        ↓
Risk + Confidence
        ↓
Uncertainty
        ↓
Explainable prioritization
        ↓
Human verification
```

The central scientific question then becomes:

> Does multimodal evidence improve inconsistency detection compared with isolated evidence?

This is a strong and manageable capstone research question.

---

# 52. What NOT to Add Now

Do not expand the project unnecessarily with:

- all six CBAM sectors;
- a large LLM agent;
- LangChain;
- RAG;
- vector databases;
- CNN/U-Net;
- Vision Transformers;
- Sentinel-2;
- CO processing;
- microservices;
- Kubernetes;
- Terraform;
- large AWS infrastructure.

These are not required to make the project academically strong.

The best use of remaining time is:

```text
Correctness
    ↓
Reproducibility
    ↓
Evaluation
    ↓
Calibration
    ↓
Documentation
```

not feature count.

---

# 53. Priority Fix List

## RED — Must Fix Before Submission

### R1 — Correct regulatory references

Especially distinguish:

- 2025/2546
- 2025/2547
- 2025/2551

### R2 — Correct satellite scope

Either implement CO/Sentinel-2 or remove them from implemented claims.

### R3 — Fix benchmark production independence

Do not derive “independent” production from historical emissions.

### R4 — Correct route-mismatch terminology

Use controlled route-mismatch cases.

### R5 — Fix reproducibility package

Include processed data or provide deterministic generation scripts.

### R6 — Fix the 17/17 test claim

Only report test results reproduced from the actual final package.

---

# 54. ORANGE — Strongly Recommended

### O1

Add facility-grouped validation.

### O2

Add LR sensitivity.

### O3

Make the five-year/six-year historical window explicit.

### O4

Correct thermodynamic terminology.

### O5

Document technology-registry mapping.

### O6

Separate controlled benchmark calibration from real-world calibration.

### O7

Add a complete data provenance document.

### O8

Document the exact three missing facility-year combinations.

---

# 55. GREEN — Optional Improvements

### G1

Wind-aware satellite plume analysis.

### G2

Improved operational activity scoring.

### G3

Additional controlled satellite inconsistency cases.

### G4

Missing-evidence stress tests.

### G5

Counterfactual explanations.

### G6

Evidence graph visualization.

### G7

LLM-generated evidence summaries.

These should only be implemented after the RED and ORANGE items.

---

# 56. Recommended Development Order

## Phase 1 — Correctness

1. Fix regulatory references.
2. Fix documentation claims.
3. Fix physical-model terminology.
4. Fix route-mismatch wording.
5. Fix benchmark production construction.

## Phase 2 — Reproducibility

6. Package processed datasets or generation scripts.
7. Confirm dependencies.
8. Re-run all tests in a clean environment.
9. Record exact test results.

## Phase 3 — Evaluation

10. Run baseline A–E.
11. Run facility-grouped validation.
12. Run calibration.
13. Run prior sensitivity.
14. Run LR sensitivity.

## Phase 4 — Satellite

15. Confirm real Sentinel-5P provenance.
16. Document observation counts.
17. Document missing observations.
18. Add wind-aware analysis only if time allows.

## Phase 5 — Presentation

19. Update dashboard terminology.
20. Update README.
21. Update project plan.
22. Update application.
23. Produce final figures/tables.
24. Freeze final dataset/version.

---

# 57. Final Pre-Submission Checklist

## Scientific

- [ ] Research question finalized.
- [ ] Hypotheses finalized.
- [ ] Controlled benchmark explicitly described.
- [ ] No synthetic case is called real ground truth.
- [ ] No real-world generalization is inferred from controlled data.
- [ ] Model E improvement is supported by ablation.
- [ ] Facility-grouped validation completed.
- [ ] Calibration limitations documented.
- [ ] Prior sensitivity completed.
- [ ] LR sensitivity completed.

## Satellite

- [ ] Only actually implemented modalities are claimed.
- [ ] Sentinel-5P provenance recorded.
- [ ] No silent synthetic fallback.
- [ ] NO₂ is described as an operational indicator, not direct CO₂.
- [ ] Missing observations produce insufficient evidence.
- [ ] Spatial method documented.
- [ ] Atmospheric transport limitations documented.

## Physical models

- [ ] Stoichiometric bounds documented.
- [ ] Engineering/BAT benchmarks clearly separated from thermodynamic minima.
- [ ] Assumptions documented.
- [ ] System boundaries documented.
- [ ] Physical violations described as model-assumption violations.

## Benchmark

- [ ] Production is independent of historical emissions, or explicitly described as synthetic.
- [ ] `benchmark_label` terminology used.
- [ ] Route mismatch is called controlled.
- [ ] Historical z-score calculated.
- [ ] 177 vs 180 documented.
- [ ] Missing facility-years documented.
- [ ] Grouped validation completed.

## Bayesian model

- [ ] Prior documented.
- [ ] Prior sensitivity documented.
- [ ] Likelihood ratios documented.
- [ ] LR sensitivity documented.
- [ ] Weight is actually used.
- [ ] Risk and confidence remain separate.
- [ ] Uncertainty assumptions documented.
- [ ] Calibration is not overclaimed.

## Reproducibility

- [ ] `requirements.txt` complete.
- [ ] Clean environment tested.
- [ ] All required processed data included or reproducibly generated.
- [ ] Dataset versions documented.
- [ ] Dataset hashes documented where possible.
- [ ] Exact experiment commands documented.
- [ ] Test count verified.
- [ ] Reported results regenerated from the final package.

## Application

- [ ] Name complete.
- [ ] Matriculation number correct.
- [ ] Study program correct.
- [ ] Project title correct.
- [ ] Description matches actual implementation.
- [ ] Regulation references correct.
- [ ] Date correct.
- [ ] Signature completed.

---

# 58. Final Verdict

The updated VeriCBAM project is **meaningfully better than the previous version**.

The architecture is now strong enough for a serious Data Science capstone:

```text
Physical evidence
        +
Satellite operational evidence
        +
Historical evidence
        +
Technology/document evidence
        ↓
Multimodal Evidence Fusion
        ↓
Risk + Confidence
        ↓
Uncertainty
        ↓
Explainable Human Decision Support
```

The main remaining weakness is not the core idea.

It is **claim-to-implementation consistency and experimental independence**.

The project is currently best characterized as:

> **A multimodal, explainable evidence-fusion prototype using deterministic physical constraints, Sentinel-5P NO₂ operational evidence, historical facility behavior, and technology metadata to prioritize controlled emissions inconsistencies for further verification.**

That description is strongly supported by the current implementation.

The project should not yet be described as:

> a fully operational multimodal satellite system using Sentinel-5P NO₂/CO and Sentinel-2;

or:

> a real-world calibrated CBAM violation detector;

or:

> a legally valid CBAM verification system.

---

# 59. Recommended Final Positioning

The strongest final title remains:

> **VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment**

A strong subtitle/description is:

> **An explainable evidence-fusion framework combining physical constraints, satellite-derived operational indicators, historical facility behavior, and documentary/technology evidence to prioritize CBAM emissions declarations for further verification.**

This positioning is technically ambitious while remaining scientifically defensible.

---

# 60. Bottom Line

### Current status

**Strong capstone prototype — approximately 8.2/10.**

### After the RED fixes

Potentially:

**~9/10 capstone quality.**

### The six things that matter most now

1. **Correct the EU regulation references.**
2. **Align satellite claims with actual implemented code.**
3. **Remove benchmark production circularity.**
4. **Fix the reproducibility/data package.**
5. **Add facility-grouped validation.**
6. **Stop overclaiming calibration/generalization.**

If these are addressed, the project will have a much stronger defense against the most likely questions from a supervisor or examiner:

- “Is the satellite evidence real?”
- “Where did your benchmark labels come from?”
- “Are your evidence sources really independent?”
- “How do you know your probabilities are calibrated?”
- “Can the experiment be reproduced?”
- “Does the model generalize to unseen facilities?”
- “Are these legal verification decisions?”
- “What exactly does the satellite measure?”
- “Are your physical bounds actually thermodynamic limits?”

The project already has good answers to many of these questions. The remaining work is to make those answers explicit, reproducible, and consistent across the code, documentation, benchmark, dashboard, application form, and thesis.

