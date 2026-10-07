> ARCHIVED: Historical document, superseded by README.md and current project codebase.

# VeriCBAM — Full Review and Required Fixes

**Project:** VeriCBAM  
**Working title:** VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment  
**Review basis:** Uploaded `Capstone.zip`, including the filled capstone application form, `VeriCBAM_Project_Plan.md`, and the supplied Python source code.  
**Review date:** 2026-10-07

---

# 1. Executive Summary

The VeriCBAM project has a strong research concept and a promising technical architecture. The central idea — combining physical/chemical constraints, satellite-derived operational evidence, historical facility behavior, and documentary/reference evidence into an explainable evidence-fusion system — is appropriate for a Data Science Master's capstone.

The main issue is **not the overall concept**.

The main issue is the difference between:

1. what the project plan describes,
2. what the application form claims,
3. what the current repository actually implements, and
4. what has already been scientifically validated.

The current project should therefore be described as:

> **A strong, well-designed capstone prototype with a promising multimodal evidence-fusion research contribution, but with several components still at prototype/simulation stage rather than experimentally validated.**

The project does **not** need a fundamental redesign.

The priority is to make the documentation scientifically precise, make the implementation status transparent, and then bring the most important experimental components up to the level claimed by the project plan.

---

# 2. Overall Assessment

| Area | Assessment |
|---|---|
| Research idea | 🟢 Very strong |
| Research question | 🟢 Strong |
| Architecture | 🟢 Strong |
| Project plan | 🟢 Strong, but several claims need correction |
| Application form | 🔴 Incomplete |
| Chemical models | 🟡 Good prototype; assumptions need tightening |
| Bayesian fusion | 🟡 Strong prototype architecture; not yet genuinely calibrated |
| Sentinel-5P pipeline | 🔴 Major issue: synthetic fallback currently exists |
| Evaluation benchmark | 🟡 Good structure, but labels and evidence generation need refinement |
| Dashboard | 🟢 Good prototype |
| Reproducibility/package | 🔴 Important supporting files are missing from the ZIP |
| Scientific defensibility | 🟡 Good potential; terminology must be corrected |
| Current overall maturity | **~7.5/10** |
| Potential after fixes | **~9/10** |

---

# 3. Critical Finding #1 — Sentinel-5P Is Currently Synthetic in the Fallback Path

## Problem

The project documentation presents the Sentinel-5P component as an operational Copernicus pipeline.

However, the supplied `copernicus_client.py` contains a fallback path that generates synthetic atmospheric observations when real cached observations are unavailable.

The implementation uses random generation and empirical parameters to construct observations such as:

- monthly observations,
- cloud fractions,
- background concentrations,
- plume enhancements,
- QA values.

This means the current system should **not** be described as having a fully validated real-data Sentinel-5P emissions/activity pipeline.

## Current conceptual flow

```text
CDSE catalogue query
        ↓
data available?
        ↓
   ┌────┴────┐
   │         │
  yes        no
   │         │
   ↓         ↓
metadata    synthetic fallback
```

The critical problem is the second branch.

## Correct claim at the current stage

Use:

> “A Sentinel-5P processing architecture and analysis prototype has been implemented, with synthetic fallback observations used for software development and testing.”

Do not use:

> “VeriCBAM has an operational Sentinel-5P emissions verification pipeline using real observations.”

## Required implementation change

Separate the satellite pipeline into two explicit modes:

```text
REAL DATA MODE
    ↓
CDSE catalogue
    ↓
actual Level-2 product
    ↓
NetCDF/HDF extraction
    ↓
quality filtering
    ↓
spatial extraction
    ↓
background estimation
    ↓
plume/activity metric
```

and:

```text
TEST MODE
    ↓
synthetic observations
    ↓
unit/integration testing
```

Synthetic data should only be enabled explicitly.

For example, conceptually:

```python
mode = "real"
```

and synthetic mode should require an explicit choice such as:

```python
mode = "synthetic"
```

The application/dashboard should never silently substitute synthetic satellite data for missing real data.

---

# 4. Critical Finding #2 — Project Plan Is Ahead of the Repository

The project plan describes a much larger repository than the uploaded ZIP currently contains.

The plan describes or anticipates components such as:

```text
config/
data/
docs/
experiments/
tests/
src/remote_sensing/
src/fingerprinting/
src/fusion/
src/document_ai/
src/agent/
src/report/
web/
requirements.txt
Dockerfile
README.md
```

The supplied ZIP contains primarily:

```text
src/
    benchmark/
    core/
    data_loaders/
    satellite/
    ui/
VeriCBAM_Project_Plan.md
VeriCBAM_Capstone_Application_Form_Filled_v2.pdf
```

The ZIP does not currently demonstrate complete implementations of all planned components, including:

- full `data/` package/data artifacts,
- `tests/`,
- `requirements.txt`,
- `README.md`,
- document parser,
- facility fingerprinting,
- LLM auditor/agent,
- PDF report generator,
- Sentinel-2 implementation,
- GEM integration,
- complete experiment scripts,
- complete calibration workflow.

## Required fix

The project plan must clearly distinguish:

### Implemented

- cohort manager,
- cement engine,
- steel engine,
- controlled benchmark generator,
- evidence-fusion prototype,
- Sentinel-5P prototype,
- Streamlit cockpit.

### Planned / in progress

- real Sentinel-5P ingestion,
- Sentinel-2,
- document parser,
- GEM integration,
- facility fingerprinting,
- full ablation experiment,
- calibration,
- report generation.

This does not weaken the project. It makes the project plan credible and reproducible.

---

# 5. Critical Finding #3 — Filled Application Form Is Not Complete

The rendered application form still contains blank fields.

## Fields that need completion

- First Name
- Matriculation No.
- Study Program
- Title of Project
- Place / Date
- Signature

The project description itself is populated.

The checkbox confirming awareness of workload requirements is checked.

The university/internal approval area should remain blank if it is reserved for institutional use.

## Recommended values

### First Name

```text
Cristhian
```

### Study Program

```text
M.Sc. Data Science
```

### Project title

Preferred:

```text
VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment
```

### Remaining

- Insert the correct matriculation number.
- Insert the correct place/date.
- Sign the form according to the university's submission requirements.

---

# 6. Critical Finding #4 — Application Description Slightly Overstates Current Implementation

The application form describes the system in a way that can be interpreted as if all three evidence pillars are already operational on real data.

The conceptual description is good, but it should distinguish:

> system being developed

from:

> components already validated on real data.

## Recommended wording

Instead of implying that the satellite component is already fully operational, use:

> “a Copernicus Earth Observation processing pipeline designed to ingest Sentinel-5P TROPOMI tropospheric columns and Sentinel-2 SWIR indicators…”

This accurately describes the research system without claiming that every component is already complete.

---

# 7. Critical Finding #5 — Bayesian Engine Is Not Yet Calibrated

The mathematical structure is promising:

```text
logit P(H | E)
=
logit P(H)
+
Σ Cᵢ log(LRᵢ)
```

However, the implementation currently uses hard-coded likelihood ratios such as:

```python
lr_stoich = 2.2
lr_sat = 6.5
lr_temp = 5.2
lr_reg = 4.5
```

and a hard-coded prior:

```python
prior_inconsistency_prob = 0.08
```

These are currently expert-defined parameters rather than empirically estimated/calibrated likelihood ratios.

## Correct current terminology

Use:

> **Bayesian/probabilistic evidence-fusion prototype**

or:

> **Probabilistic evidence-fusion risk engine**

Avoid:

> “calibrated Bayesian evidence-fusion engine”

until the probability calibration experiment has actually been completed.

## Required future experiment

Use the controlled benchmark to evaluate:

- Brier score,
- Expected Calibration Error (ECE),
- reliability/calibration curves,
- ROC-AUC,
- PR-AUC,
- precision,
- recall,
- F1.

Then, if appropriate, apply a calibration method such as:

- Platt scaling,
- isotonic regression,
- another justified calibration approach.

Only after that should the final output be described as a calibrated inconsistency probability.

---

# 8. Critical Finding #6 — The 8% Prior Needs Better Support

The project uses:

```text
P(H) ≈ 0.08
```

and associates it with an audit/discrepancy baseline.

The supplied project package does not sufficiently establish the exact source and methodological justification for this precise 8% value.

## Two valid solutions

### Option A — Empirical prior

Find and document a defensible source with:

- exact statistic,
- population,
- definition of discrepancy,
- context,
- applicability to VeriCBAM.

### Option B — Sensitivity prior

Treat the prior as a modelling assumption and test:

```text
P(H) = 0.02
P(H) = 0.05
P(H) = 0.08
P(H) = 0.15
```

Then demonstrate whether the risk ranking is robust.

For a capstone, Option B may be especially useful because it creates a clear robustness experiment.

---

# 9. Critical Finding #7 — `weight` Exists but Is Not Used

The evidence stream structure contains a weight field.

However, the actual posterior calculation uses the confidence factor and likelihood ratio but does not incorporate the `weight` value.

This creates a mismatch between the data model and the actual fusion equation.

## Required fix

Choose one:

### Option A — Remove `weight`

If confidence is the only intended reliability modifier, simplify the data model.

### Option B — Use `weight`

If scientifically justified, implement something conceptually like:

```text
Σ wᵢ Cᵢ log(LRᵢ)
```

and define exactly what `wᵢ` represents.

For the current capstone, removing the unused weight may be preferable unless a strong methodological justification exists.

---

# 10. Critical Finding #8 — The 95% Uncertainty Interval Needs a Statistical Definition

The uncertainty mechanism currently perturbs likelihood ratios using a noise scale based on confidence.

This is useful as a prototype sensitivity analysis, but it is not automatically a statistically justified 95% credible interval.

## Current appropriate description

> “Monte Carlo sensitivity interval under assumed likelihood-ratio uncertainty.”

## If a Bayesian credible interval is desired

Define probability distributions for uncertain quantities such as:

- likelihood ratios,
- prior probability,
- confidence/reliability,
- measurement uncertainty.

Then propagate those distributions through the Bayesian model.

The resulting posterior interval can legitimately be described as a Bayesian credible interval if the statistical assumptions support that terminology.

---

# 11. Critical Finding #9 — Physical Overrule Is Too Absolute

The evidence-fusion implementation can set:

```text
posterior = 1.0
confidence = 1.0
```

when a stoichiometric violation occurs.

The intention is understandable: a physical impossibility should dominate the evidence.

However, the physical bound itself may depend on uncertain inputs and assumptions, including:

- production,
- composition,
- process route,
- system boundary,
- capture assumptions,
- measurement error.

## Better interpretation

Use:

> **Physical feasibility violation under specified model assumptions**

rather than implying:

> 100% certain real-world non-compliance.

The deterministic rule can remain, but its assumptions should be visible.

---

# 12. Critical Finding #10 — Cement Model Terminology

The cement engine includes a stoichiometric calcination relationship and a thermal-energy/BAT-type lower bound.

The chemical stoichiometric component can be described as a physical constraint.

The energy benchmark should not automatically be described as a fundamental thermodynamic minimum.

## Recommended terminology

Instead of:

> thermodynamic minimum

use:

> **engineering/BAT lower bound**

where the value comes from process/BAT assumptions.

A clearer structure is:

```text
Chemical stoichiometric minimum
+
Engineering/BAT process constraint
=
Model-based feasibility bound
```

This is more scientifically defensible.

---

# 13. Critical Finding #11 — Steel Route Bounds Need Similar Terminology

The steel engine uses route-specific values such as:

- BF-BOF,
- DRI-NG,
- DRI-H₂,
- Scrap-EAF.

The hematite reduction calculation can be presented as a stoichiometric physical relationship.

The route-specific values incorporate engineering/process assumptions.

## Recommended terminology

Use:

> **route-specific engineering lower bound**

rather than:

> absolute thermodynamic minimum

unless the value is actually derived from a formal thermodynamic analysis.

---

# 14. Critical Finding #12 — Benchmark Production Is Derived from Emissions

The benchmark generator creates production/activity assumptions using emissions-derived relationships.

This creates a circular dependency:

```text
CO₂
 ↓
derived production
 ↓
CO₂ evaluated against production
```

This can make the benchmark artificially easy because the activity variable is not independent.

## Better approach

Use independently sourced activity/capacity information where possible, such as:

- GEM,
- facility capacity,
- production data,
- independently documented facility metadata.

If that is not possible, explicitly label the value as:

> synthetic benchmark production assumption.

Do not present emissions-derived production as independent empirical activity data.

---

# 15. Critical Finding #13 — Rename `ground_truth_inconsistent_label`

The benchmark code uses a variable named similar to:

```text
ground_truth_inconsistent_label
```

This is problematic because the benchmark labels are generated by the experiment rather than independently observed CBAM truth.

## Recommended names

Use:

```text
benchmark_label
```

or:

```text
expected_inconsistency_label
```

or:

```text
controlled_case_label
```

This small terminology change is important for academic clarity.

---

# 16. Critical Finding #14 — Historical “>3 Sigma” Claim Is Not Actually Calculated

The benchmark description refers to a historical drop greater than three standard deviations.

However, the supplied generator uses a fixed reduction factor rather than calculating the resulting historical z-score.

## Required fix

Actually calculate:

```text
z = (perturbed_value - historical_mean) / historical_std
```

Then either:

- generate perturbations until the desired z-score is achieved, or
- record the resulting z-score.

The benchmark should store the actual value.

This makes the experiment reproducible.

---

# 17. Critical Finding #15 — Steel Route Misclassification Is Currently Assumed

The benchmark describes route misclassification cases, but the actual “true” route must come from a real independent source if the case is to represent a real facility technology mismatch.

If all facilities are simply assumed to be BF-BOF, the route label is an assumption.

## Required improvement

Where possible, store:

```text
actual_route
actual_route_source
declared_route
route_mismatch
```

For example:

```text
actual_route = BF-BOF
actual_route_source = independent facility source
declared_route = Scrap-EAF
```

Then the benchmark is genuinely testing route misclassification.

If this cannot be sourced, call it:

> controlled synthetic route-mismatch scenario

rather than real route ground truth.

---

# 18. Critical Finding #16 — Current Benchmark Does Not Fully Support Model C

The planned ablation contains:

```text
A — Declaration
B — Stoichiometry
C — Satellite
D — Historical
E — Multimodal
```

But the controlled benchmark currently contains mostly declaration/emissions/activity/route information, while the satellite evidence is separately simulated.

Therefore the five models are not yet consuming a fully unified evidence dataset.

## Required improvement

Create one common benchmark table such as:

```text
controlled_benchmark.parquet
```

with fields such as:

```text
case_id
facility_id
sector
year

original_emissions
declared_emissions

production
production_route

label

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

Then Models A–E can consume exactly the same cases and differ only in evidence availability.

This will make the ablation scientifically much stronger.

---

# 19. Recommended Experimental Dataset Structure

A strong experiment dataset should contain:

| Field | Purpose |
|---|---|
| `case_id` | Unique evaluation case |
| `facility_id` | Facility |
| `sector` | Cement/steel |
| `year` | Observation year |
| `original_emissions` | Original reference value |
| `declared_emissions` | Value assessed by model |
| `production` | Activity information |
| `production_route` | Process route |
| `benchmark_label` | Controlled expected label |
| `stoich_margin` | Physical margin |
| `stoich_violation` | Physical feasibility flag |
| `satellite_zscore` | Activity/plume evidence |
| `satellite_confidence` | Satellite evidence quality |
| `satellite_available` | Data availability |
| `historical_zscore` | Historical anomaly |
| `historical_confidence` | Historical evidence quality |
| `capacity_ratio` | Capacity/activity relationship |
| `registry_confidence` | Reference-data confidence |
| `perturbation_type` | Case type |
| `perturbation_magnitude` | Severity |

---

# 20. Satellite Evidence Should Be an Activity Proxy

Sentinel-5P should not be described as directly measuring facility-level CO₂.

Satellite observations are affected by:

- meteorology,
- atmospheric transport,
- background concentrations,
- neighboring sources,
- source composition,
- spatial resolution,
- temporal sampling,
- cloud/quality conditions.

## Recommended output

> **Operational Activity Consistency Score**

## Recommended wording

> “Sentinel-5P observations are used as independent atmospheric indicators of industrial operational activity and are not interpreted as direct measurements of facility-level CO₂ emissions.”

---

# 21. Sentinel-2 Terminology Must Be Corrected

Sentinel-2 B11 and B12 are **SWIR (Short-Wave Infrared)** bands.

Do not describe them as:

- thermal infrared,
- thermal bands,
- direct temperature measurements.

Prefer:

> “Sentinel-2 SWIR-based industrial activity indicators.”

or:

> “Sentinel-2 SWIR observations used as an industrial activity/anomaly proxy.”

---

# 22. E-PRTR Should Not Be Called Ground Truth Anywhere

This terminology must be corrected in:

- project plan,
- application,
- code comments,
- benchmark variables,
- dashboard labels,
- final thesis,
- presentation.

Use:

> independent reference data

or:

> historical regulatory reporting reference.

The distinction is fundamental:

```text
E-PRTR historical emissions
        ≠
verified CBAM embedded-emissions declaration
```

---

# 23. Explain the 177 vs. 180 Observation Count

The cohort contains:

- 30 facilities,
- 6 years (2018–2023),
- 180 possible facility-year observations.

The reported dataset contains 177 observations.

Therefore, three facility-year observations are missing.

## Recommended wording

> “The benchmark cohort contains 30 facilities across 2018–2023, yielding 180 possible facility-year observations. Three observations are missing, resulting in 177 available facility-year records.”

Document:

- facility,
- year,
- reason for missingness if known,
- analytical impact.

Do not describe this as a complete panel.

---

# 24. Risk and Confidence Must Be Separate

The dashboard should display:

## Risk

How strongly the evidence indicates potential material inconsistency.

## Confidence

How reliable and complete the available evidence is.

Example:

> **High inconsistency risk + low confidence**

means:

> “The evidence raises a substantial concern, but evidence quality is insufficient for a strong conclusion.”

This is better than collapsing both into one number.

---

# 25. Add “Insufficient Evidence” as a Formal Outcome

Recommended outputs:

1. **Consistent**
2. **Potential inconsistency**
3. **High inconsistency risk**
4. **Insufficient evidence**

The fourth category is particularly important when:

- satellite coverage is poor,
- atmospheric quality is insufficient,
- historical records are missing,
- declaration information is incomplete,
- facility metadata are uncertain.

---

# 26. Recommended Evidence Hierarchy

Use this as the central scientific structure.

## Level 1 — Physical consistency

Question:

> Is the declaration physically plausible?

Evidence:

- stoichiometry,
- process constraints,
- route-specific feasibility,
- material balance.

## Level 2 — Operational consistency

Question:

> Is the declaration consistent with observed operational activity?

Evidence:

- Sentinel-5P,
- Sentinel-2,
- production/activity proxies.

## Level 3 — Historical consistency

Question:

> Is the declaration consistent with the facility's historical behavior?

Evidence:

- historical emissions,
- temporal anomaly,
- facility fingerprint.

## Level 4 — Multimodal consistency

Question:

> Does the declaration remain plausible after combining independent evidence?

Evidence:

- physical,
- satellite,
- historical,
- documentary/reference evidence.

This makes the multimodal contribution easy to explain.

---

# 27. Recommended Final Architecture

Use one consistent architecture across the project:

```text
CBAM Declaration
       ↓
Document Extraction / Validation
       ↓
 ┌───────────────┬────────────────┬────────────────┐
 ↓               ↓                ↓                ↓
Chemical       Satellite       Historical      Documentary
Evidence       Evidence        Evidence        Evidence
 ↓               ↓                ↓                ↓
Physical       Activity        Facility        Declaration
Bounds         Indicators      Fingerprint     Consistency
 └───────────────┴────────────────┴────────────────┘
                       ↓
             Evidence Fusion Engine
                       ↓
             Risk + Confidence
                       ↓
            Uncertainty Assessment
                       ↓
          Explainable Evidence Graph
                       ↓
                Human Verifier
                       ↓
          Verification Decision Support
```

---

# 28. LLM Role Must Remain Limited

The LLM should not:

- calculate stoichiometric limits,
- generate scientific measurements,
- assign the core probability,
- override physical constraints,
- decide legal compliance.

The LLM should:

- interpret structured evidence,
- summarize findings,
- explain the evidence,
- identify missing information,
- generate audit-oriented narratives,
- support the human verifier.

## Recommended principle

> “Deterministic and statistical components generate the evidence and risk assessment; the LLM explains and organizes the evidence.”

---

# 29. Human-in-the-Loop Must Be Explicit

The system should end with:

```text
Evidence
   ↓
Risk Assessment
   ↓
Confidence / Uncertainty
   ↓
Explainable Evidence Graph
   ↓
Human Verifier
   ↓
Verification Priority / Decision Support
```

Avoid:

```text
Evidence
   ↓
AI
   ↓
CBAM compliance decision
```

This is one of the strongest positioning choices for the project.

---

# 30. Dashboard Terminology Needs Softening

Some dashboard labels are currently stronger than the actual evidence supports.

## Replace

### Current

> STOICHIOMETRICALLY COMPLIANT

### Prefer

> Physically feasible under specified assumptions

---

### Current

> ROUTE VERIFIED

### Prefer

> No route inconsistency detected under current evidence

---

### Current

> Physical Impossibility Detected

### Prefer

> Physical feasibility violation under model assumptions

---

### Current

> instantly clearing physically verified claims

### Prefer

> prioritizing declarations for further verification

The dashboard should never imply that VeriCBAM legally clears or certifies declarations.

---

# 31. Scope: What Must Be Protected

The current scope is ambitious:

- CBAM document parsing,
- chemistry,
- cement,
- steel,
- fertilisers,
- Sentinel-5P,
- Sentinel-2,
- ERA5,
- facility fingerprinting,
- temporal anomaly detection,
- Bayesian fusion,
- uncertainty,
- counterfactual analysis,
- LLM auditor,
- Streamlit,
- PDF dossier,
- five-model ablation,
- calibration.

For a capstone, this is a lot.

## Must-have

1. Cement + steel
2. Stoichiometric engine
3. Historical facility evidence
4. One robust satellite methodology
5. Evidence-fusion model
6. Uncertainty/confidence
7. Five-model ablation
8. Quantitative evaluation

## Should-have

9. Document parser
10. Sentinel-2 extension
11. Facility fingerprint
12. Counterfactual analysis
13. Explainable evidence graph

## Nice-to-have

14. LLM auditor
15. PDF dossier
16. Full multi-sector expansion
17. Full AWS/Terraform deployment
18. Highly autonomous agent loops

If time becomes constrained, sacrifice the nice-to-have features before sacrificing evaluation.

---

# 32. Recommended Research Question

The strongest formulation is:

> **To what extent can independent physical, observational, historical, and documentary evidence be fused into a calibrated decision-support model that identifies inconsistent CBAM emissions declarations more reliably than isolated evidence sources?**

This should remain the central research question.

Avoid overly strong language such as:

> “prove”

or:

> “legally verify”

where the data do not support those claims.

---

# 33. Recommended Evaluation Structure

The five-model ablation should remain central.

## Model A — Declaration-only baseline

Uses declaration information only.

## Model B — Stoichiometric evidence

Declaration + physical/chemical constraints.

## Model C — Satellite evidence

Declaration + remote-sensing operational indicators.

## Model D — Historical evidence

Declaration + facility historical behavior.

## Model E — Multimodal evidence

Declaration + stoichiometry + satellite + historical evidence.

## Main experimental question

> Does multimodal evidence fusion improve the detection and calibration of known inconsistencies compared with individual evidence sources?

---

# 34. Metrics

Where controlled labels exist, evaluate:

- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC
- Brier score
- Expected Calibration Error
- calibration/reliability curve
- false-positive rate
- false-negative rate
- detection latency where relevant

Do not claim population-level generalization from the 30-facility cohort.

Prefer:

> “The evaluation tests the methodological hypothesis within the available facility cohort.”

---

# 35. Recommended Controlled Inconsistency Benchmark

Use controlled categories:

1. Physical-bound violation
2. Route inconsistency
3. Historical anomaly
4. Satellite/activity inconsistency
5. Combined multimodal inconsistency

For each case store:

- original observation,
- perturbed observation,
- perturbation type,
- perturbation magnitude,
- expected label,
- affected evidence sources,
- detectability.

These cases should be explicitly identified as synthetic/controlled evaluation cases.

They should never be presented as real regulatory violations.

---

# 36. Recommended Robustness Tests

Add at least a small sensitivity/robustness experiment involving:

- different prior probabilities,
- different confidence weights,
- satellite missingness,
- noisy satellite observations,
- missing historical years,
- uncertain production assumptions,
- alternative stoichiometric bounds,
- different perturbation magnitudes.

Report whether the risk ranking remains stable.

This can become a valuable Master's-level contribution.

---

# 37. Scientific Interpretation of the Ablation

Do not simply produce a leaderboard.

Explain what each evidence source contributes.

### Stoichiometry

Detects:

> physically impossible or implausible declarations.

### Satellite

Detects:

> operational/activity inconsistencies.

### Historical evidence

Detects:

> unusual facility behavior.

### Multimodal fusion

Detects:

> complementary inconsistencies that may not be visible from one evidence source.

This makes the ablation scientifically meaningful.

---

# 38. Recommended Contribution Statement

Use:

> **A multimodal, explainable evidence-fusion framework that combines deterministic physical constraints, satellite-derived operational indicators, historical facility behavior, and declaration-level information to produce calibrated inconsistency risk and confidence estimates for CBAM-related emissions assessment.**

This is a much stronger and more defensible contribution than:

> autonomous CBAM emissions verification.

---

# 39. File-by-File Action Plan

## 39.1 `VeriCBAM_Capstone_Application_Form_Filled_v2.pdf`

### Required

- [ ] Fill First Name.
- [ ] Fill Matriculation No.
- [ ] Fill Study Program.
- [ ] Insert final project title.
- [ ] Fill Place/Date.
- [ ] Sign.
- [ ] Leave institutional approval section for the university if applicable.

### Recommended title

```text
VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment
```

### Recommended program

```text
M.Sc. Data Science
```

---

## 39.2 `VeriCBAM_Project_Plan.md`

### Required

- [ ] Replace “ground truth” with “independent reference data.”
- [ ] Clarify that E-PRTR is not CBAM violation truth.
- [ ] Explain real data vs. controlled synthetic perturbations.
- [ ] Explain 177 available observations vs. 180 possible.
- [ ] Change “calibrated Bayesian” to prototype/probabilistic until calibration is completed.
- [ ] Clarify the 8% prior.
- [ ] Correct Sentinel-2 B11/B12 terminology to SWIR.
- [ ] Reframe Sentinel-5P as operational/activity evidence.
- [ ] Replace “thermodynamic minimum” where the value is actually an engineering/BAT bound.
- [ ] Distinguish implemented, operational, validated, and calibrated.
- [ ] Synchronize the sprint plan with actual implementation.
- [ ] Reduce claims of broad generalization.
- [ ] Protect the five-model ablation as the core experiment.

---

## 39.3 `src/satellite/copernicus_client.py`

### Highest-priority code change

- [ ] Separate real-data and synthetic-data modes.
- [ ] Do not silently fall back to synthetic observations.
- [ ] Add an explicit `synthetic`/test mode.
- [ ] Log clearly when synthetic data are used.
- [ ] Ensure dashboard/demo can identify data provenance.
- [ ] Implement actual Level-2 measurement extraction before claiming real satellite operation.
- [ ] Preserve quality filtering and background normalization.

### Recommended data provenance field

```text
data_source = "real_sentinel5p"
```

or:

```text
data_source = "synthetic_test"
```

This should propagate into the analysis output.

---

## 39.4 `src/satellite/plume_analyzer.py`

### Review/fix

- [ ] Treat output as operational/activity evidence.
- [ ] Avoid naming output as direct CO₂ emissions.
- [ ] Preserve cloud/quality filtering.
- [ ] Document background-estimation assumptions.
- [ ] Document spatial/temporal limitations.
- [ ] Return evidence quality/confidence separately from the score.
- [ ] Explicitly report insufficient evidence when observations are unavailable or low quality.

---

## 39.5 `src/core/bayesian/evidence_fusion.py`

### Required

- [ ] Clarify Bayesian formulation.
- [ ] Decide whether `weight` is needed.
- [ ] If retained, include it consistently in the mathematical formulation.
- [ ] Document prior selection.
- [ ] Document LR selection.
- [ ] Document confidence factors.
- [ ] Document evidence dependency assumptions.
- [ ] Separate risk from confidence.
- [ ] Replace absolute `posterior=1.0` behavior with a clearly documented physical-overrule assumption or high-evidence rule.
- [ ] Rename “calibrated” until calibration is completed.
- [ ] Implement proper calibration experiment later.

---

## 39.6 `src/core/stoichiometry/cement_engine.py`

### Required

- [ ] Keep true stoichiometric constraints.
- [ ] Rename engineering/BAT values appropriately.
- [ ] Distinguish physical chemistry from engineering benchmark.
- [ ] Document assumptions and units.
- [ ] Make uncertainty in input quantities explicit where possible.

---

## 39.7 `src/core/stoichiometry/steel_engine.py`

### Required

- [ ] Keep stoichiometric reduction relationship.
- [ ] Rename route-specific “thermodynamic/absolute” bounds as engineering/process lower bounds unless formally derived.
- [ ] Document route assumptions.
- [ ] Make route uncertainty explicit.
- [ ] Avoid claiming actual facility route unless independently sourced.

---

## 39.8 `src/benchmark/cohort_manager.py`

### Required

- [ ] Document 177 available facility-year observations.
- [ ] Identify the three missing observations.
- [ ] Document missingness.
- [ ] Avoid “complete panel” terminology.
- [ ] Keep E-PRTR as independent reference data.

---

## 39.9 Benchmark generator

### Required

- [ ] Rename `ground_truth_inconsistent_label`.
- [ ] Explicitly distinguish controlled labels from real-world truth.
- [ ] Calculate historical z-scores rather than only fixed percentage drops.
- [ ] Store perturbation magnitude.
- [ ] Store actual z-score.
- [ ] Make production/activity assumptions explicit.
- [ ] Avoid deriving an “independent” production variable directly from emissions.
- [ ] Use independent route information where possible.

---

## 39.10 `src/ui/app.py`

### Required

- [ ] Replace “verified/compliant” wording.
- [ ] Show risk and confidence separately.
- [ ] Display data provenance.
- [ ] Display “Insufficient Evidence” when appropriate.
- [ ] Make synthetic satellite mode visibly identifiable.
- [ ] Use “decision support” terminology.
- [ ] Avoid implying legal CBAM certification.

---

# 40. Recommended Repository Improvements

The project would benefit from adding:

```text
README.md
requirements.txt
tests/
experiments/
docs/
config/
```

A recommended structure:

```text
VeriCBAM/
│
├── README.md
├── requirements.txt
├── LICENSE
│
├── docs/
│   ├── methodology.md
│   ├── assumptions.md
│   ├── evaluation.md
│   └── data_dictionary.md
│
├── config/
│   └── default.yaml
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── experiments/
│   ├── benchmark_generation.py
│   ├── ablation.py
│   ├── calibration.py
│   └── robustness.py
│
├── tests/
│   ├── test_cement.py
│   ├── test_steel.py
│   ├── test_fusion.py
│   └── test_satellite.py
│
├── src/
│   ├── benchmark/
│   ├── core/
│   ├── data_loaders/
│   ├── satellite/
│   └── ui/
│
└── results/
    ├── figures/
    ├── tables/
    └── metrics/
```

Do not create empty folders merely for appearance. Add them when they correspond to real reproducible work.

---

# 41. Recommended Development Order

## Phase 1 — Clean the scientific foundation

```text
E-PRTR
   +
facility metadata
   +
stoichiometry
   ↓
clean benchmark
```

## Phase 2 — Real remote sensing

```text
Actual Sentinel-5P
       ↓
quality filtering
       ↓
facility/background extraction
       ↓
operational activity indicator
```

## Phase 3 — Evidence fusion

```text
Stoichiometry
Satellite
Historical
Registry
      ↓
probabilistic fusion
      ↓
risk + confidence
```

## Phase 4 — Calibration

```text
raw probability
      ↓
calibration experiment
      ↓
calibrated probability
```

## Phase 5 — Ablation

```text
A vs B vs C vs D vs E
```

## Phase 6 — Robustness

```text
prior
weights
missing data
measurement noise
perturbation severity
```

## Phase 7 — Dashboard refinement

The dashboard should present the scientifically validated outputs rather than drive the research methodology.

---

# 42. Current Status Terminology

Use these definitions throughout the project.

### Implemented

Code exists and has been technically tested.

### Operational

Real input can be processed end-to-end successfully.

### Validated

Quantitative evaluation has been performed against an independent reference or controlled benchmark.

### Calibrated

Predicted probabilities have been evaluated for calibration and, if appropriate, calibrated.

### Recommended status table

| Component | Current appropriate wording |
|---|---|
| Stoichiometric engine | Implemented / unit-tested |
| EEA cohort | Acquired / processed |
| Sentinel-5P client | Implemented prototype |
| Sentinel-5P real-data pipeline | Not yet fully validated; real operational status depends on end-to-end data extraction |
| Bayesian fusion | Implemented prototype |
| Probability calibration | Pending |
| Streamlit cockpit | Implemented prototype |
| Multimodal ablation | Pending |
| Robustness analysis | Pending |

---

# 43. Recommended Global Terminology

| Avoid | Prefer |
|---|---|
| Ground truth | Independent reference data |
| CBAM compliance verification | CBAM consistency assessment |
| Automatically verifies | Assesses / flags / prioritizes |
| Certified verification | Decision support |
| Proves non-compliance | Identifies potential inconsistency |
| Direct emissions measurement | Operational/activity indicator |
| Sentinel-2 thermal infrared | Sentinel-2 SWIR |
| Satellite emissions measurement | Satellite-derived operational evidence |
| Deterministic Bayesian | Probabilistic Bayesian / evidence fusion |
| Calibrated | Calibrated only after calibration experiment |
| Validated | Validated only after quantitative evaluation |
| Complete panel | 177 available facility-year observations |
| No synthetic data | Authentic reference data + controlled synthetic perturbations |
| Legal decision | Human verification support |
| Route verified | No route inconsistency detected under current evidence |
| Stoichiometrically compliant | Physically feasible under specified assumptions |

---

# 44. Recommended Limitations Section

Add a section to the project plan/thesis:

## Limitations of the Reference Data

> The EEA Industrial Reporting Database provides independent facility-level historical emissions observations but does not constitute a labelled dataset of verified CBAM declaration violations. Consequently, it is used primarily for reference analysis, facility fingerprinting, historical consistency assessment, and alignment with observational evidence. Controlled perturbations of real observations may be introduced in a separate benchmark to evaluate the ability of the proposed evidence-fusion framework to identify known inconsistencies. These perturbations are explicitly distinguished from real regulatory violations.

---

# 45. Recommended Evaluation Limitations

State explicitly:

- the 30-facility cohort is a methodological benchmark,
- it is not representative of all European industry,
- controlled perturbations do not constitute real CBAM violations,
- satellite evidence has resolution and atmospheric limitations,
- physical bounds depend on assumptions and system boundaries,
- Bayesian priors and likelihood ratios may require calibration,
- historical reporting can contain missing observations.

This will make the project appear more academically mature.

---

# 46. Recommended Final Thesis Story

The strongest narrative is:

```text
CBAM declarations are difficult to assess independently
                    ↓
No public dataset provides complete verified CBAM violation labels
                    ↓
Use independent evidence instead
                    ↓
Physical / chemical evidence
                    +
Satellite operational evidence
                    +
Historical facility evidence
                    +
Documentary/reference evidence
                    ↓
Evidence fusion
                    ↓
Uncertainty + confidence
                    ↓
Calibrated inconsistency risk
                    ↓
Explainable human decision support
```

This is a coherent Data Science research story.

---

# 47. Final Pre-Submission Checklist

## Application

- [ ] First name completed
- [ ] Matriculation number completed
- [ ] M.Sc. Data Science completed
- [ ] Project title completed
- [ ] Place/date completed
- [ ] Signature completed
- [ ] Institutional approval section left for university if applicable

## Scientific terminology

- [ ] E-PRTR is not called ground truth
- [ ] CBAM inconsistency is defined
- [ ] Satellite data are not presented as direct CO₂ measurement
- [ ] Sentinel-2 B11/B12 are identified as SWIR
- [ ] Engineering/BAT bounds are distinguished from thermodynamic limits
- [ ] Risk and confidence are separate
- [ ] Insufficient Evidence is a valid outcome

## Bayesian model

- [ ] Prior documented
- [ ] Likelihood ratios documented
- [ ] Confidence factors documented
- [ ] Weight field either removed or correctly incorporated
- [ ] Evidence dependency assumptions documented
- [ ] Uncertainty method documented
- [ ] Calibration experiment planned/completed
- [ ] “Calibrated” used only after calibration

## Dataset

- [ ] 177 vs. 180 explained
- [ ] Missing observations documented
- [ ] E-PRTR labelled as independent reference data
- [ ] Synthetic perturbations clearly separated from real observations
- [ ] Benchmark labels renamed
- [ ] Production/activity assumptions documented
- [ ] Route assumptions documented

## Satellite

- [ ] Synthetic fallback explicitly identified
- [ ] Real-data mode separated
- [ ] Actual Level-2 extraction implemented before claiming real operational validation
- [ ] Data provenance visible
- [ ] Quality filtering documented
- [ ] Atmospheric/background limitations documented

## Evaluation

- [ ] Common benchmark dataset created
- [ ] Models A–E use comparable cases
- [ ] Precision/Recall/F1 only used where labels exist
- [ ] Calibration metrics included
- [ ] Robustness analysis included
- [ ] Generalization claims limited

## Documentation

- [ ] Application and project plan agree
- [ ] Project plan and repository agree
- [ ] Current implementation status is accurate
- [ ] Completed and planned components are clearly separated
- [ ] Code comments use scientifically accurate terminology
- [ ] Dashboard terminology matches scientific claims

## Scope

- [ ] Cement and steel remain core
- [ ] Fertiliser is optional
- [ ] One robust satellite methodology is enough for MVP
- [ ] Evaluation has priority over UI/LLM/PDF features
- [ ] Five-model ablation remains protected

---

# 48. Final Verdict

The VeriCBAM concept should **not be redesigned**.

The strongest architecture is already present conceptually:

```text
CBAM declaration
       ↓
Physical evidence
       +
Satellite evidence
       +
Historical evidence
       +
Registry/documentary evidence
       ↓
Evidence fusion
       ↓
Risk + confidence + uncertainty
       ↓
Explainable decision support
       ↓
Human verifier
```

The principal correction is to align the **claims, code, and scientific validation level**.

The most important changes are:

1. **E-PRTR ≠ CBAM ground truth**
2. **Real reference data ≠ labelled real-world violations**
3. **Controlled perturbations must be explicitly identified as synthetic evaluation cases**
4. **Bayesian terminology must match the actual mathematics**
5. **Satellite data provide operational/activity evidence, not direct facility CO₂ verification**
6. **177 observations must be explained**
7. **The 30-facility dataset is a methodological benchmark, not proof of European-wide generalization**
8. **The current Sentinel-5P synthetic fallback must be clearly separated from real-data processing**
9. **The current Bayesian model should be called a prototype until calibration is performed**
10. **The final system should assess inconsistency risk and verification priority, not legally certify CBAM compliance**

With these changes, VeriCBAM becomes substantially more defensible as a Master's Data Science Capstone and its real contribution becomes clearer:

> **multimodal, explainable evidence fusion for CBAM emissions consistency assessment.**

