> ARCHIVED: Historical document, superseded by README.md and current project codebase.

# VeriCBAM — Advanced & Competitive Project Architecture

## Purpose of this document

This document consolidates the proposed extensions for making **VeriCBAM** more complete, complex, academically competitive, and commercially relevant while keeping the project feasible as a Data Science Capstone.

The main recommendation is to evolve VeriCBAM from a system that simply checks whether a CBAM declaration "looks correct" into:

> **A multimodal industrial intelligence and risk-assessment system that reconstructs the evidence behind a CBAM declaration.**

The emphasis should be on **research depth, evidence quality, uncertainty, explainability, and measurable performance**, rather than simply adding more software infrastructure.

---

# 1. Evidence Fusion Engine

## Concept

Create a formal evidence-fusion layer that combines independent evidence sources rather than producing isolated flags.

### Architecture map

```text
                 CBAM Declaration
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
   Chemical         Satellite        Historical
   Evidence          Evidence         Evidence
        |               |                |
        v               v                v
  Physical          Activity          Facility
  Plausibility      Consistency       Benchmark
        |               |                |
        +---------------+----------------+
                        |
                        v
                Evidence Fusion
                        |
                        v
                Risk / Confidence
                        |
                        v
              Explainable Decision
```

## Evidence examples

| Evidence source | Example result | Confidence |
|---|---|---:|
| Stoichiometric bound | Consistent | 0.96 |
| Declared production | High | 0.88 |
| Satellite activity | Consistent | 0.72 |
| Historical emissions | Inconsistent | 0.81 |
| Facility metadata | Consistent | 0.94 |

## Recommended implementation

Use a deterministic model such as:

```text
Risk = f(
    stoichiometric_violation,
    activity_discrepancy,
    historical_anomaly,
    data_quality,
    source_confidence
)
```

The LLM should explain the result rather than invent or determine the numerical risk score.

---

# 2. Bayesian / Probabilistic Risk Layer

## Concept

Instead of a binary output such as:

```text
Fraud = YES
```

produce:

```text
Probability of material inconsistency = 78%
Confidence = 64%
```

These should be treated as different concepts.

## Conceptual model

```text
P(H | E1, E2, E3, ...)
```

Where:

- `H` = declaration is materially inconsistent
- `E1` = stoichiometric evidence
- `E2` = satellite evidence
- `E3` = historical facility evidence
- `E4` = production metadata
- `E5` = document evidence

## Example risk scale

```text
0.05        0.30          0.65          0.90
 |-----------|-------------|-------------|
 Low       Moderate        High        Critical
```

## Why this improves the project

It turns a collection of rules into an actual **decision-support model** and creates a strong statistical component for the capstone.

---

# 3. Uncertainty Quantification

## Concept

Every major result should carry uncertainty.

Instead of:

```text
Satellite activity discrepancy = 34%
```

the system should be able to communicate:

```text
Activity discrepancy = 34%
Estimated uncertainty = +/- 12%
Evidence quality = Medium
```

## Uncertainty map

```text
Satellite uncertainty
        +
Meteorological uncertainty
        +
Facility attribution uncertainty
        +
Stoichiometric uncertainty
        +
Reporting uncertainty
        |
        v
Overall evidence uncertainty
```

## Recommended outputs

- Point estimate
- Confidence interval or uncertainty interval
- Evidence quality
- Data completeness
- Source confidence

---

# 4. Facility Digital Twin / Industrial Evidence Profile

## Concept

Construct a simplified digital representation of each industrial facility.

## Facility profile map

```text
Facility
|
+-- Location
+-- Production route
+-- Installed capacity
+-- Production history
+-- Process configuration
+-- Energy inputs
+-- Reported emissions
+-- Satellite observations
+-- Atmospheric observations
+-- Historical regulatory data
+-- CBAM declarations
```

## Main research question

Instead of asking:

> Is this reported number plausible?

ask:

> Given everything known about this facility, what should its emissions and industrial activity approximately look like?

## Suggested name

**Facility Digital Twin** or **Industrial Evidence Profile**

This can become one of the distinctive features of VeriCBAM.

---

# 5. Temporal Anomaly Detection

## Concept

Move beyond declaration-versus-observation and model facility behavior over time.

## Temporal map

```text
2019 ---------------- 2020 ---------------- 2021 ---------------- 2022
      |                     |                     |
      v                     v                     v
 emissions              activity              emissions
      |                     |                     |
      +---------------------+---------------------+
                            |
                            v
                    Temporal anomaly
```

## Detect

- Unusual emission increases
- Unexpected production changes
- Shutdown periods
- Sudden changes in emissions intensity
- Abnormal divergence between production and emissions

## Candidate methods

- Isolation Forest
- XGBoost
- Change-point detection
- STL decomposition
- Temporal clustering

This adds a genuine **time-series data science component**.

---

# 6. Sector-Aware Modeling

## Concept

Instead of one generic model, create sector-specific process and evidence models.

## Architecture map

```text
                    CBAM Engine
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Cement          Steel        Fertiliser
          |              |              |
     Calcination     BF/BOF          Haber-Bosch
     Kiln activity   DRI/EAF         SMR
          |              |              |
          +--------------+--------------+
                         |
                         v
              Sector-specific models
```

## Recommended implementation

### Tier 1 — Full implementation

- Cement
- Steel

### Tier 2 — Prototype / architecture demonstration

- Fertilisers

Avoid implementing all six CBAM sectors unless the core system is already complete.

---

# 7. Counterfactual Analysis

## Concept

The system should not only identify a suspicious value.

It should investigate what process configuration could make the reported value plausible.

## Example

```text
Declared emissions
       |
       v
0.80 tCO2/t steel
       |
       v
What scenarios could explain it?
       |
       +-- BF-BOF ------> Implausible
       |
       +-- DRI-EAF -----> Possible
       |
       +-- Renewable electricity -> Possible
       |
       +-- CCUS ---------> Requires evidence
```

## Example output

```text
Declaration: 0.80 tCO2/t steel

BF-BOF:
    Physical plausibility -> Very Low

DRI-EAF:
    Physical plausibility -> Medium/High

CCUS scenario:
    Potentially plausible
    Additional evidence required
```

This turns the system into an **investigative assistant** rather than a simple red-flag generator.

---

# 8. Evidence-Resolution Recommendation

## Concept

When the system lacks enough evidence, it should identify what information would reduce uncertainty.

## Example

```text
Assessment:
HIGH RISK

Confidence:
LOW

Missing evidence:
- Installation production records
- Energy consumption data
- Verification documentation
```

## Recommended output

> The current evidence is insufficient to establish a material inconsistency. Additional production and energy records would most reduce uncertainty.

This creates a practical **audit-support workflow**.

---

# 9. LLM as Auditor / Orchestrator

## Principle

The LLM should orchestrate evidence retrieval and explain results.

It should NOT be responsible for numerical truth.

## Recommended architecture

```text
Declaration
    |
    v
Structured extraction
    |
    v
Deterministic validation
    |
    +--> Stoichiometric engine
    |
    +--> Satellite engine
    |
    +--> Facility database
    |
    +--> Historical evidence
    |
    v
Risk scoring
    |
    v
Evidence collection
    |
    v
LLM explanation
```

## Core principle

```text
LLM:
    Extract -> Call tools -> Collect outputs -> Explain

NOT:

    Invent -> Estimate -> Decide
```

This improves reproducibility, safety, and academic defensibility.

---

# 10. Explainability Evidence Graph

## Concept

Every final risk assessment should be traceable to evidence.

## Example

```text
                 DECLARATION
                     |
           +---------+---------+
           |                   |
           v                   v
      0.72 tCO2/t         400 kt production
           |                   |
           v                   v
    Stoichiometric         Facility model
       check                   |
           |                   |
           v                   v
       FAIL                 CONSISTENT
           |                   |
           +---------+---------+
                     |
                     v
                 RISK SCORE
                   82/100
                     |
          +----------+----------+
          |          |          |
          v          v          v
       Chemical   Satellite   Historical
       evidence   evidence    evidence
```

## Each evidence node should contain

- Source
- Timestamp
- Calculation
- Input data
- Model version
- Confidence
- Explanation

This creates an **auditable reasoning chain**.

---

# 11. Adversarial / Red-Team Benchmark

The existing plan already proposes synthetic fraud testing. This can be expanded into a more systematic benchmark.

## Level 1 — Obvious inconsistencies

Example:

```text
BF-BOF
0.4 tCO2/t
```

## Level 2 — Subtle inconsistencies

```text
BF-BOF
1.25 tCO2/t
```

## Level 3 — Accounting manipulation

Correct total emissions but incorrect allocation.

## Level 4 — Temporal manipulation

Production reported during periods of apparent inactivity.

## Level 5 — Multimodal deception

The declaration is individually plausible, but becomes inconsistent when:

- satellite evidence
- historical evidence
- process evidence
- facility metadata

are combined.

## Benchmark objective

Test whether the multimodal system detects inconsistencies that individual evidence sources cannot detect.

---

# 12. Model Comparison / Ablation Study

## This should be one of the central experiments

Do not simply demonstrate that VeriCBAM works.

Test whether adding each evidence source improves performance.

## Experimental models

### Model A — Declaration only

Uses reported CBAM values.

### Model B — Declaration + Stoichiometry

Adds physical/process constraints.

### Model C — Declaration + Satellite

Adds remote-sensing activity indicators.

### Model D — Declaration + Historical Data

Adds facility history.

### Model E — Multimodal VeriCBAM

Combines all major evidence sources.

## Evaluation table

| Model | Precision | Recall | F1 | FPR |
|---|---:|---:|---:|---:|
| Declaration | | | | |
| + Stoichiometry | | | | |
| + Satellite | | | | |
| + Historical | | | | |
| **Multimodal** | | | | |

## Central research question

> Does multimodal evidence fusion improve the detection of inconsistent CBAM emissions declarations compared with individual evidence sources?

This gives the project a strong Data Science research contribution.

---

# 13. Probability Calibration

If VeriCBAM outputs:

```text
Probability of inconsistency = 80%
```

then the probability should have statistical meaning.

## Metrics

- Reliability diagrams
- Brier score
- Expected Calibration Error
- ROC-AUC
- Precision-Recall curves
- F1
- False-positive rate

## Why this matters

A calibrated 80% risk score is much more useful to a human auditor than an arbitrary score of 80/100.

---

# 14. Human-in-the-Loop Verification

## Concept

Do not attempt to replace the human verifier.

Instead, create an automated screening and prioritisation system.

## Workflow

```text
                    VeriCBAM
                       |
              Automated screening
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Low risk     Medium risk   High risk
          |            |            |
       Archive       Review       Human audit
```

## Recommended role of the system

> AI-assisted pre-verification / audit prioritisation

rather than:

> AI replacing accredited verification.

This makes the system more realistic and commercially defensible.

---

# 15. CBAM Audit Trail

## Concept

Every assessment should be reproducible.

## Example

```text
Audit ID:
VC-2027-00041

Declaration:
supplier_041.xlsx

Analysis timestamp:
2027-01-07 14:32 UTC

Facility:
FAC-00921

Data versions:
TROPOMI: [version]
ERA5: [version]
E-PRTR: [version]
GEM: [version]

Calculations:
stoichiometry_v1.3
satellite_model_v0.8

Risk:
78/100

Evidence:
E01 -> Stoichiometric inconsistency
E02 -> Activity discrepancy
E03 -> Historical anomaly

Decision:
HIGH RISK / HUMAN REVIEW
```

## Required characteristics

- Reproducibility
- Versioned inputs
- Versioned models
- Timestamping
- Evidence references
- Calculation traceability

---

# 16. Regulatory Knowledge Graph

## Concept

Represent the CBAM regulatory structure as a structured knowledge base.

## Knowledge graph

```text
CBAM Regulation
       |
       +-- Sector
       |
       +-- CN code
       |
       +-- Production route
       |
       +-- Calculation method
       |
       +-- Embedded emissions
       |
       +-- Precursor
       |
       +-- Default value
       |
       +-- Verification requirement
       |
       +-- Evidence requirement
```

## AI architecture

```text
User / Declaration
        |
        v
       LLM
        |
        +------> Regulatory Knowledge Graph
        |
        +------> Deterministic Calculation Engine
        |
        +------> Data / Satellite Tools
        |
        v
  Explainable Audit Result
```

This moves the project toward:

> **RAG + Knowledge Graph + Deterministic Scientific Computation**

rather than a generic LLM agent.

---

# 17. Facility Fingerprinting

## Concept

Build a characteristic historical fingerprint for every facility.

## Example

```text
              FACILITY FINGERPRINT

Production route       BF-BOF
Capacity               4.2 Mt/year

NO2 pattern            ████████░░
SO2 pattern            ███░░░░░░░
CO pattern             █████░░░░░
SWIR activity          ███████░░░
Historical CO2         ████████░░
Production             ███████░░░
```

## Possible methods

- PCA
- Clustering
- Mahalanobis distance
- Isolation Forest
- Autoencoder

## Main objective

Detect unusual behavior relative to the facility's own historical pattern rather than only comparing it against a global population.

This is a natural and valuable Data Science extension.

---

# 18. Recommended Overall Architecture

The following architecture combines the strongest ideas while avoiding unnecessary infrastructure expansion.

```text
                    +-------------------------+
                    |     CBAM Declaration    |
                    |       PDF / Excel       |
                    +------------+------------+
                                 |
                                 v
                    +-------------------------+
                    | Document Intelligence   |
                    | OCR / Parser / RAG      |
                    +------------+------------+
                                 |
              +------------------+------------------+
              |                  |                  |
              v                  v                  v
       +-------------+    +-------------+    +-------------+
       | Chemical    |    | Satellite   |    | Historical  |
       | Engine      |    | Engine      |    | Facility DB |
       +------+------+    +------+------+    +------+------+
              |                  |                  |
              v                  v                  v
       Physical bounds    Activity signal    Facility fingerprint
              |                  |                  |
              +------------------+------------------+
                                 |
                                 v
                    +-------------------------+
                    | Evidence Fusion Engine  |
                    | Bayesian / ML / Rules   |
                    +------------+------------+
                                 |
                                 v
                    +-------------------------+
                    | Uncertainty Quantifier  |
                    +------------+------------+
                                 |
                                 v
                    +-------------------------+
                    | Risk + Confidence Score |
                    +------------+------------+
                                 |
                                 v
                    +-------------------------+
                    | Explainable AI Auditor  |
                    +------------+------------+
                                 |
              +------------------+------------------+
              |                  |                  |
              v                  v                  v
       Audit Dashboard     Evidence Graph       PDF Dossier
              |
              v
        Human Verifier
```

---

# 19. Recommended Final Scope for the Capstone

Do **not** implement every possible extension.

The strongest practical scope is:

## Core components

1. **CBAM document intelligence**
2. **Chemical / stoichiometric engine**
3. **Satellite activity engine**
4. **Facility digital fingerprint**
5. **Historical anomaly detection**
6. **Multimodal evidence-fusion model**
7. **Uncertainty + confidence estimation**
8. **Explainable human-in-the-loop audit dashboard**

## Sector scope

### Full implementation

- Cement
- Steel

### Architecture / prototype extension

- Fertilisers

## What should remain optional

- React / Next.js
- Complex microservices
- Terraform
- Full AWS infrastructure
- Large autonomous agent loops
- CNN/U-Net satellite segmentation
- All six CBAM sectors

The research contribution should receive priority over infrastructure.

---

# 20. Recommended Central Research Question

A strong final research question is:

> **Can independent physical, observational, historical, and documentary evidence be fused into a calibrated risk model that identifies inconsistent CBAM emissions declarations more effectively than any individual evidence source?**

## Sub-questions

### RQ1 — Physical plausibility

How accurately can process-specific stoichiometric constraints identify physically implausible emissions declarations?

### RQ2 — Remote sensing

Can satellite-derived activity indicators provide useful independent evidence about declared industrial activity?

### RQ3 — Historical behavior

Can facility-specific historical fingerprints identify abnormal emissions or activity patterns?

### RQ4 — Evidence fusion

Does combining independent evidence sources improve precision, recall, F1, and false-positive rate?

### RQ5 — Uncertainty

How does uncertainty in satellite observations, facility attribution, and process assumptions affect risk-score reliability?

### RQ6 — Explainability

Can the system provide a reproducible evidence chain that allows a human reviewer to understand and challenge each risk assessment?

---

# 21. Suggested Final Product Positioning

## Current positioning

> Autonomous CBAM verification platform.

## Recommended positioning

> **VeriCBAM — Multimodal AI-Assisted Evidence and Risk Assessment for CBAM Emissions Declarations**

Alternative:

> **VeriCBAM — An Explainable Multimodal Decision-Support System for CBAM Verification**

The second is particularly suitable for an academic project.

---

# 22. Recommended Research Contribution

The project should not claim that its main contribution is simply:

> "We built a dashboard."

Instead, the contribution should be:

```text
Independent evidence sources
          |
          v
Evidence fusion
          |
          v
Calibrated risk assessment
          |
          v
Explainable human decision support
```

The key experimental claim becomes:

> **Multimodal evidence fusion can identify inconsistent industrial emissions declarations more reliably than isolated evidence sources.**

This is much stronger as a Data Science contribution.

---

# 23. Competitive Differentiation

The project can distinguish itself through five dimensions:

## 1. Physical intelligence

Chemical engineering constraints rather than purely statistical anomaly detection.

## 2. Earth observation

Independent satellite evidence rather than relying exclusively on supplier declarations.

## 3. Historical intelligence

Facility-specific temporal fingerprints rather than only cross-sectional comparison.

## 4. Explainable AI

Every risk flag can be traced to a calculation, observation, dataset, or regulatory rule.

## 5. Human-in-the-loop design

The system prioritises and explains evidence rather than pretending to replace professional verification.

---

# 24. Final Recommended VeriCBAM Concept

The strongest version of the project is:

```text
                 VERICBAM
                    |
                    v
       "What does the evidence say?"
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
     Physical    Observed    Historical
     reality      activity    behavior
        |           |           |
        +-----------+-----------+
                    |
                    v
              Evidence Fusion
                    |
                    v
             Uncertainty Model
                    |
                    v
            Risk + Confidence
                    |
                    v
          Explainable AI Auditor
                    |
                    v
              Human Reviewer
```

The fundamental philosophy should be:

> **Do not ask the AI to decide whether a declaration is true. Ask the system to assemble, quantify, and explain the independent evidence that supports or contradicts the declaration.**

That is the direction most likely to make VeriCBAM simultaneously **more complete, more complex, more scientifically defensible, and more competitive**.

