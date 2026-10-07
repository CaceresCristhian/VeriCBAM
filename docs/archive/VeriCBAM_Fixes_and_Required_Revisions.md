> ARCHIVED: Historical document, superseded by README.md and current project codebase.

# VeriCBAM — Required Fixes and Recommended Revisions

**Project:** VeriCBAM  
**Working title:** VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment  
**Review basis:** Capstone Proposal Document, VeriCBAM Project Plan, and VeriCBAM Status Summary & Resources  
**Review date:** 2026-10-04

## 1. Executive Summary

The VeriCBAM project is already technically strong. The main corrections concern scientific claims, evaluation design, terminology, and consistency between the proposal, project plan, and current implementation status.

### Priority fixes

1. Do not treat E-PRTR/IED data as CBAM ground truth.
2. Define the prediction target as inconsistency/risk assessment, not verified CBAM non-compliance.
3. Resolve the contradiction between “100% non-synthetic” data and planned injected inconsistencies.
4. Make the Bayesian evidence-fusion formulation explicitly Bayesian.
5. Explain the 177 vs. 180 facility-year observation count.
6. Reframe Sentinel-5P and Sentinel-2 as independent operational/activity evidence rather than direct emissions measurement.
7. Correct Sentinel-2 terminology: B11/B12 are SWIR, not thermal infrared.
8. Synchronize the project plan with the current implementation status.
9. Distinguish implemented, operational, validated, and calibrated components.
10. Keep multimodal evidence fusion and its evaluation as the academic core.

---

## 2. E-PRTR Is Not CBAM Ground Truth

### Issue

The EEA Industrial Reporting Database / E-PRTR provides facility-level historical emissions data, but an E-PRTR record is not equivalent to a verified CBAM embedded-emissions declaration.

### Replace

Avoid:

- ground truth
- verified CBAM truth
- confirmed CBAM non-compliance
- true CBAM violation

Prefer:

- independent reference dataset
- historical regulatory reporting reference
- facility-level emissions reference
- independent historical emissions evidence
- reference observations

### Recommended wording

> “The EEA Industrial Reporting Database is used as an independent facility-level reference dataset for historical emissions and operational consistency analysis. It is not treated as ground truth for CBAM declaration non-compliance.”

Apply this consistently in the proposal, methodology, evaluation, and project plan.

---

## 3. Define the Actual Prediction Target

VeriCBAM should not claim that it independently determines whether a CBAM declaration is legally correct.

### Recommended target

> **Probability or risk of material inconsistency in a CBAM emissions declaration based on independent physical, observational, historical, and documentary evidence.**

Position the system as **decision support and risk assessment**, not autonomous legal verification.

Prefer:

- emissions consistency assessment
- inconsistency risk
- evidence-based risk assessment
- material inconsistency
- verification priority
- decision support

Avoid:

- automatically verifies CBAM compliance
- certifies emissions
- proves fraud
- legally determines non-compliance
- replaces accredited verification bodies

### Recommended system statement

> “VeriCBAM does not replace accredited verification. It provides an explainable, evidence-based assessment of whether a reported emissions value is physically, operationally, historically, and documentarily consistent with independent evidence.”

---

## 4. Resolve the Synthetic vs. Real Data Contradiction

### Issue

The Status Summary describes the reference datasets as authentic and non-synthetic, while the Project Plan proposes injected reporting inconsistencies and classification metrics.

These statements need to be separated.

### Recommended evaluation design

#### Layer A — Real-world reference analysis

Use authentic EEA observations for:

- historical trends
- facility fingerprints
- anomaly detection
- satellite alignment
- descriptive validation
- evidence consistency analysis

Call this:

> **Real-world reference evaluation**

#### Layer B — Controlled perturbation benchmark

Create controlled perturbations of real observations to test whether the system detects known inconsistencies.

Examples:

- unrealistically low emissions relative to production assumptions
- emissions below physical feasibility
- abrupt unexplained historical changes
- operational signals inconsistent with reported activity
- deliberately altered declaration values

Call these:

> **Synthetic perturbations applied to real observations**

### Recommended wording

> “The primary reference dataset consists entirely of authentic facility observations. For controlled predictive evaluation, a separate benchmark introduces explicitly documented perturbations to real observations. These perturbations are used only to test detection sensitivity under known conditions and are not presented as real CBAM violations.”

This is stronger than claiming that all evaluation data are completely non-synthetic.

---

## 5. Make the Bayesian Evidence Fusion Explicitly Bayesian

### Issue

The documents use “Bayesian evidence fusion,” “likelihood ratios,” and weighted evidence scores. The mathematical definition should clearly match the terminology.

Define:

- **H** = material inconsistency
- **Eᵢ** = evidence source *i*
- **P(H)** = prior probability
- **LRᵢ** = likelihood ratio from evidence source *i*
- **Cᵢ** = confidence/reliability factor

Recommended formulation:

```text
logit P(H | E)
=
logit P(H)
+
Σ Cᵢ × log(LRᵢ)
```

where:

```text
logit(p) = log(p / (1-p))
```

and:

```text
P(H | E) = sigmoid(
    logit(P(H))
    + Σ Cᵢ log(LRᵢ)
)
```

Document:

1. how the prior is selected,
2. how likelihood ratios are estimated or specified,
3. how confidence weights are defined,
4. how evidence dependencies are handled,
5. how uncertainty is propagated,
6. how probabilities are calibrated.

### Important dependency issue

Historical emissions, satellite activity, and production may reflect the same underlying operational state. Do not assume unconditional independence without justification.

If the implementation uses an approximation, say so explicitly:

> “The fusion model approximates conditional independence between evidence channels while applying confidence factors and dependency-aware adjustments.”

If formal Bayesian likelihoods are not actually implemented, rename the component to:

> **Probabilistic Evidence-Fusion Risk Engine**

rather than overstating the Bayesian formulation.

---

## 6. Clarify the 95% Credible Interval

If the Bayesian engine reports 95% credible intervals, document:

- parameter being estimated,
- prior,
- likelihood,
- posterior distribution,
- interval calculation.

If the interval is not derived from a formal posterior distribution, use the statistically appropriate term instead, such as:

- uncertainty interval
- confidence interval
- prediction interval

Do not call it a Bayesian credible interval unless it is actually derived from a posterior distribution.

---

## 7. Explain the 177 vs. 180 Observation Count

The cohort contains:

- 30 facilities
- 6 years: 2018–2023
- 180 possible facility-year observations

The Status Summary reports **177 annual records**, implying three missing observations.

### Required action

Identify the missing:

- facility
- year
- reason for missingness, if known
- analytical impact

### Recommended wording

> “The benchmark cohort contains 30 facilities across 2018–2023, yielding 180 possible facility-year observations. Three observations are missing, resulting in 177 available facility-year records.”

Do not call this a complete six-year panel.

---

## 8. Reframe Sentinel-5P Evidence

Do not imply:

> Sentinel-5P NO₂/CO → direct facility CO₂ measurement.

NO₂ and CO are influenced by:

- meteorology
- atmospheric transport
- background concentrations
- neighboring sources
- source composition
- spatial resolution
- temporal sampling
- cloud/quality conditions

### Recommended output name

> **Operational Activity Consistency Score**

### Recommended wording

> “Sentinel-5P observations are used as independent atmospheric indicators of industrial operational activity and are not interpreted as direct measurements of facility-level CO₂ emissions.”

The current background normalization and confidence scoring support this framing.

---

## 9. Correct Sentinel-2 Terminology

Sentinel-2 B11 and B12 are **Short-Wave Infrared (SWIR)** bands.

Do not call them:

- thermal infrared
- thermal bands
- direct temperature measurement

Prefer:

> “Sentinel-2 SWIR-based industrial activity indicators”

or:

> “Sentinel-2 SWIR observations used as an industrial activity/anomaly proxy.”

If actual thermal data from another mission are later added, describe those separately.

---

## 10. Clarify What Satellite Evidence Can Prove

Satellite evidence can provide independent information about:

- surface conditions
- industrial activity patterns
- site-level spectral changes
- spatial anomalies
- operational proxies

It should not be presented as directly measuring:

- facility CO₂ emissions
- exact combustion emissions
- exact embedded emissions
- legally reportable CBAM emissions

Satellite evidence should be one component of the multimodal evidence system.

---

## 11. Use an Evidence Hierarchy

Structure the methodology as four levels.

### Level 1 — Physical consistency

**Question:** Is the declaration physically plausible?

Examples:

- stoichiometric minimum
- route-specific bounds
- material balance
- process constraints

### Level 2 — Operational consistency

**Question:** Is the declaration consistent with observed operational activity?

Examples:

- Sentinel-5P
- Sentinel-2
- production/activity proxies

### Level 3 — Historical consistency

**Question:** Is the declaration consistent with the facility's historical behavior?

Examples:

- historical emissions
- temporal anomaly detection
- facility fingerprint

### Level 4 — Multimodal consistency

**Question:** Does the declaration remain plausible when all independent evidence is considered together?

This is where the evidence-fusion model operates.

This hierarchy makes the research contribution clearer.

---

## 12. Preserve the Five-Model Ablation Study

The five-model ablation is one of the strongest parts of the project.

### Model A — Declaration-only baseline

Uses only declaration information.

### Model B — Stoichiometric evidence

Declaration + physical/chemical constraints.

### Model C — Satellite evidence

Declaration + remote-sensing operational indicators.

### Model D — Historical evidence

Declaration + facility historical behavior.

### Model E — Multimodal evidence

Declaration + stoichiometry + satellite + historical evidence.

### Main experimental question

> Does multimodal evidence fusion improve the detection and calibration of known inconsistencies compared with individual evidence sources?

---

## 13. Use Metrics Only Where Labels Exist

Where controlled perturbations provide labels, metrics can include:

- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC
- Brier score
- Expected Calibration Error (ECE)
- calibration curve
- false-positive rate
- false-negative rate
- detection latency, where relevant

For a 30-facility cohort, avoid broad population-level generalization.

Prefer:

> “The evaluation tests the methodological hypothesis within the available facility cohort.”

Avoid:

> “The experiment proves the model works across European industry.”

---

## 14. Add “Insufficient Evidence” as a Formal Outcome

Make this a first-class system output.

Recommended categories:

1. **Consistent**
2. **Potential inconsistency**
3. **High inconsistency risk**
4. **Insufficient evidence**

This is important because satellite coverage, atmospheric conditions, historical records, and documentation quality can be insufficient.

The system should not force a binary conclusion when evidence is weak.

---

## 15. Separate Risk from Confidence

Display two separate concepts.

### Risk

How strongly the evidence suggests material inconsistency.

### Confidence

How reliable and complete the evidence is.

For example:

> **High inconsistency risk + low confidence**

means:

> “The available evidence raises a substantial concern, but evidence quality is insufficient for a strong conclusion.”

Do not collapse these into one score.

---

## 16. Distinguish Implementation Status

Use the following terminology consistently.

### Implemented

The component exists and has been technically tested.

### Operational

The component successfully processes real input data end-to-end.

### Validated

The component has been quantitatively evaluated against an independent reference or controlled benchmark.

### Calibrated

Predicted probabilities have been quantitatively assessed and, where appropriate, adjusted for calibration.

### Suggested status terminology

| Component | Appropriate status |
|---|---|
| Stoichiometric engine | Implemented / unit-tested |
| EEA benchmark cohort | Acquired / processed |
| Sentinel-5P client | Implemented |
| Sentinel-5P real-data pipeline | Operational only after successful real end-to-end processing |
| Bayesian evidence fusion | Implemented |
| Probability calibration | Validated only after calibration experiment |
| Streamlit dashboard | Implemented |
| Full multimodal model | Validated only after ablation study |

Do not use “validated” simply because code runs.

---

## 17. Synchronize the Project Plan and Status Summary

The Status Summary says that Sentinel-5P, Bayesian fusion, and the Streamlit cockpit are already built, while the Project Plan schedules related work in later sprints.

Update the schedule so completed work is marked as completed.

Remaining sprints can then focus on:

- integration
- validation
- Sentinel-2 extension
- document parser
- GEM linking
- ablation
- calibration
- robustness
- final reporting

This removes the apparent contradiction between documents.

---

## 18. Reduce Scope if Necessary

The current scope includes:

- CBAM document parsing
- chemistry
- cement
- steel
- fertilisers
- Sentinel-5P
- Sentinel-2
- ERA5
- facility fingerprinting
- temporal anomaly detection
- Bayesian fusion
- uncertainty
- counterfactual analysis
- LLM auditor
- Streamlit
- PDF dossier
- five-model ablation
- calibration

This is ambitious for a capstone.

### Must-have

1. Cement + steel
2. Stoichiometric engine
3. Historical facility evidence
4. One robust satellite methodology
5. Evidence-fusion model
6. Uncertainty/confidence
7. Five-model ablation
8. Quantitative evaluation

### Should-have

9. Document parser
10. Sentinel-2 extension
11. Facility fingerprint
12. Counterfactual analysis
13. Explainable evidence graph

### Nice-to-have

14. LLM auditor
15. PDF dossier
16. Full multi-sector expansion
17. Full AWS/Terraform deployment
18. Highly autonomous agent loops

If time becomes constrained, cut the nice-to-have features before cutting the evaluation.

---

## 19. Keep the LLM in the Correct Role

The LLM should **not** be responsible for:

- calculating stoichiometric limits
- generating scientific measurements
- assigning the core risk probability
- overriding deterministic constraints
- deciding legal CBAM compliance

The LLM should instead:

- interpret structured evidence
- summarize findings
- generate explanations
- identify missing evidence
- produce an audit-oriented narrative
- support the human verifier

### Recommended principle

> “Deterministic and statistical components generate the evidence and risk assessment; the LLM explains and organizes the evidence.”

---

## 20. Strengthen the Human-in-the-Loop Design

The final system should explicitly show:

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

Avoid presenting the system as:

```text
AI → CBAM compliance decision
```

---

## 21. Recommended Final Architecture

Use one consistent architecture across the documents:

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

## 22. Recommended Central Research Statement

Use a formulation close to:

> **Can independent physical, observational, historical, and documentary evidence be fused into a calibrated risk model that identifies inconsistent CBAM emissions declarations more effectively than any individual evidence source?**

This is stronger and more defensible than framing the project as direct satellite-based emissions verification.

---

## 23. Recommended Project Positioning

Preferred title:

> **VeriCBAM: Multimodal Evidence Fusion & Decision Support for CBAM Emissions Consistency Assessment**

Alternative:

> **VeriCBAM: An Explainable Multimodal Decision-Support System for CBAM Verification**

The first title is preferable because it avoids implying that VeriCBAM replaces accredited verification.

---

## 24. Global Terminology Replacements

Search the documents and replace where appropriate:

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
| Validated | Implemented, operational, or validated — depending on evidence |
| Complete 2018–2023 panel | 177 available facility-year observations across 2018–2023 |
| No synthetic data | Authentic reference data + controlled synthetic perturbations, if used |
| Legal decision | Human verification support |

---

## 25. Add a Reference-Data Limitations Section

Recommended section:

### Limitations of the Reference Data

> The EEA Industrial Reporting Database provides independent facility-level historical emissions observations but does not constitute a labelled dataset of verified CBAM declaration violations. Consequently, it is used primarily for reference analysis, facility fingerprinting, historical consistency assessment, and alignment with observational evidence. Controlled perturbations of real observations may be introduced in a separate benchmark to evaluate the ability of the proposed evidence-fusion framework to identify known inconsistencies. These perturbations are explicitly distinguished from real regulatory violations.

---

## 26. Add a Controlled Inconsistency Benchmark

Recommended perturbation categories:

1. Physical-bound violation
2. Route inconsistency
3. Historical anomaly
4. Satellite/activity inconsistency
5. Combined multimodal inconsistency

For each perturbation, store:

- original observation
- perturbed observation
- perturbation type
- perturbation magnitude
- expected label
- evidence sources affected
- detectability

This creates a reproducible evaluation protocol.

---

## 27. Add Robustness Tests

At minimum, test some combination of:

- different priors
- different evidence confidence weights
- satellite missingness
- noisy satellite measurements
- missing historical years
- uncertain production assumptions
- alternative stoichiometric bounds
- different perturbation magnitudes

Report whether the risk ranking changes substantially.

This strengthens the academic contribution significantly.

---

## 28. Interpret the Ablation Scientifically

Do not only report which model has the highest metric.

Explain what information each evidence source contributes:

- **Stoichiometry** → physically impossible declarations
- **Satellite** → operational inconsistencies
- **Historical data** → unusual facility behavior
- **Multimodal fusion** → complementary evidence integration

This turns the ablation study into a scientific analysis rather than a leaderboard.

---

## 29. Recommended Final Contribution Statement

Use a formulation such as:

> **A multimodal, explainable evidence-fusion framework that combines deterministic physical constraints, satellite-derived operational indicators, historical facility behavior, and declaration-level information to produce calibrated inconsistency risk and confidence estimates for CBAM-related emissions assessment.**

This is more defensible than claiming autonomous CBAM emissions verification.

---

# 30. Final Pre-Submission Checklist

## Scientific validity

- [ ] E-PRTR is not called ground truth.
- [ ] CBAM inconsistency is clearly defined.
- [ ] Bayesian formulation is mathematically explicit.
- [ ] Credible intervals have a defined statistical basis.
- [ ] Satellite data are treated as observational/activity evidence.
- [ ] Sentinel-2 B11/B12 are described as SWIR.
- [ ] Physical bounds are distinguished from regulatory thresholds.
- [ ] Uncertainty and insufficient evidence are explicitly represented.

## Dataset

- [ ] 177 vs. 180 observations explained.
- [ ] Missing facility-years documented.
- [ ] Real observations and synthetic perturbations are clearly separated.
- [ ] No artificial perturbation is presented as a real CBAM violation.
- [ ] Cohort-size limitations are acknowledged.

## Evaluation

- [ ] Five-model ablation retained.
- [ ] Controlled inconsistency benchmark defined.
- [ ] Precision/Recall/F1 calculated only where labels exist.
- [ ] Calibration evaluated only after probabilities are properly defined.
- [ ] Robustness tests included.
- [ ] Generalization claims limited to the available evidence.

## Architecture

- [ ] Evidence fusion is the core.
- [ ] LLM is explanation/orchestration, not scientific truth.
- [ ] Human verifier remains in the loop.
- [ ] Risk and confidence are separate.
- [ ] “Insufficient Evidence” is a valid output.

## Documentation

- [ ] Proposal and project plan use the same terminology.
- [ ] Status summary matches actual implementation.
- [ ] Completed components are removed from future-work descriptions.
- [ ] Remaining sprints focus on validation/integration where appropriate.
- [ ] Implemented vs. operational vs. validated vs. calibrated is explicit.

## Scope

- [ ] Cement + steel remain the primary sectors.
- [ ] Fertiliser expansion is optional.
- [ ] One robust satellite pipeline is sufficient for MVP.
- [ ] UI/LLM/PDF features do not take priority over evaluation.
- [ ] The multimodal ablation experiment is protected from scope cuts.

---

# 31. Bottom Line

The VeriCBAM concept does **not** need to be redesigned.

The strongest path is to keep the existing architecture and make the scientific claims more precise:

**Physical constraints + satellite observations + historical facility behavior + declaration information → probabilistic evidence fusion → risk + confidence + uncertainty → explainable human decision support.**

The most important changes are:

1. **E-PRTR ≠ CBAM ground truth**
2. **Real reference data ≠ labelled violations**
3. **Controlled perturbations should be explicitly identified as synthetic evaluation cases**
4. **Bayesian terminology must match the actual mathematics**
5. **Satellite data provide operational/activity evidence, not direct facility CO₂ verification**
6. **177 observations must be explained**
7. **The final system assesses inconsistency risk rather than legally verifying compliance**

With these corrections, the project becomes considerably more defensible as a Data Science Capstone and the multimodal evidence-fusion contribution becomes much clearer.

