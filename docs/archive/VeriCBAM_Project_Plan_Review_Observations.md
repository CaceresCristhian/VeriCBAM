> ARCHIVED: Historical document, superseded by README.md and current project codebase.

# VeriCBAM Project Plan — Review Observations

## Overall assessment

The plan is ambitious, technically interesting, and well structured, with a strong combination of chemical engineering, remote sensing, geospatial data science, ML/LLM orchestration, and software engineering.

The main issue is **scope and scientific defensibility rather than lack of ideas**. The current plan presents several components as if they can directly verify or quantify CBAM emissions, while the proposed satellite data and validation design may only support weaker claims such as **activity indication, anomaly detection, consistency checking, and risk prioritisation**.

For a Data Science Capstone, the strongest version of VeriCBAM would therefore be framed as:

> **An evidence-fusion decision-support system for CBAM declaration consistency and risk assessment, combining stoichiometric plausibility checks with satellite-derived industrial activity indicators and structured document analysis.**

That framing is more defensible than claiming that the system can independently certify or directly measure a facility's legally reportable embedded emissions.

---

## 1. Executive Summary & Problem Statement

### Observation 1 — Avoid presenting supplier fraud as an established general fact

The plan states that non-EU producers "frequently submit fraudulent, deflated, or default emissions figures."

This is a strong empirical claim. Unless a specific source is provided, it should be softened.

**Suggested direction:**
- "may submit inaccurate, incomplete, or inconsistent emissions figures"
- distinguish intentional fraud from reporting errors, estimation, use of default values, and methodological differences.

This distinction matters academically and legally.

### Observation 2 — Be careful with the legal-liability statement

The plan says EU importers "bear full legal liability" and may face "severe regulatory fines and customs blockades."

This should be tied explicitly to the applicable CBAM legislation and implementing rules. The project should distinguish:
- reporting obligations,
- certificate obligations,
- penalties,
- customs procedures,
- verification requirements,
- and responsibility between declarants, producers, and other actors.

**Recommendation:** create a dedicated `regulatory_assumptions.md` document containing the exact legal provisions used by the project.

### Observation 3 — The solution currently overclaims "verification"

The word **verification** is used throughout the project, including "certified verification dossiers."

The proposed system cannot automatically establish legal certification merely because it combines stoichiometry and satellite data.

A safer terminology is:
- "independent consistency assessment"
- "risk screening"
- "evidence-based verification support"
- "audit decision support"

The final report should clearly state that the prototype is **not a legal CBAM verifier or certification authority**.

---

# 2. Objectives

## Observation 4 — Objective 1 is one of the strongest components

The stoichiometric bound engine is well aligned with the author's chemical engineering background and gives the project a genuinely interpretable component.

However, the plan should distinguish:

1. **theoretical stoichiometric minimum**
2. **engineering lower bound**
3. **typical operational emissions**
4. **legally reportable CBAM embedded emissions**

These are not automatically equivalent.

For example, a theoretical reaction minimum does not necessarily establish the minimum value that can appear in a CBAM calculation because system boundaries, precursor emissions, electricity, process configuration, allocation rules, and accounting methodology matter.

### Recommendation

For each production route, define:

`Theoretical bound -> Engineering assumptions -> Accounting boundary -> Comparable CBAM metric`

This would make the model substantially more rigorous.

---

## Observation 5 — Objective 2 is currently too ambitious

The plan proposes to:

> "compute an independent empirical activity index"

This is realistic.

However, the plan also moves toward estimating emissions from satellite observations. That is considerably harder.

TROPOMI observations can provide useful atmospheric information, but turning column concentrations into facility-level CO2 mass emissions requires assumptions about:
- wind fields,
- atmospheric transport,
- plume lifetime,
- background concentration,
- source separation,
- chemical transformation,
- boundary-layer structure,
- satellite overpass timing,
- retrieval uncertainty,
- and spatial resolution.

**Recommendation:** make the primary satellite target an **activity/emission-consistency indicator**, not an absolute facility CO2 measurement.

---

# 3. Stoichiometric Model

## Observation 6 — The term "thermodynamic lower bound" needs tightening

The plan repeatedly connects the minimum emission value to both stoichiometry and thermodynamics.

For several processes, the relevant lower bound is primarily determined by **mass balance and process chemistry**, while enthalpy/free-energy calculations do not automatically produce a minimum CO2 intensity.

Therefore, avoid implying:

`Delta H / Delta G -> minimum CO2`

unless the thermodynamic derivation is actually performed.

### Better structure

For each process:

- reaction stoichiometry
- elemental mass balance
- carbon balance
- process boundary
- energy requirements
- fuel assumptions
- electricity assumptions
- carbon capture assumptions
- resulting lower/upper bounds

This also makes the code easier to test.

---

## Observation 7 — The BF-BOF numerical threshold should not be hard-coded as universal

The plan gives:

> approximately 1.60 tCO2/t crude steel

and uses 0.80 tCO2/t as an example of a physically falsified declaration.

This is useful as an illustrative case, but the project should not treat one number as universally applicable to every BF-BOF plant.

The result depends on the defined boundary and assumptions.

### Recommendation

Implement:

`minimum_emissions(route, assumptions)`

rather than:

`minimum_emissions(route) = constant`

The assumptions should include at least:
- product definition,
- process route,
- raw-material composition,
- reductant,
- fuel,
- electricity,
- precursor treatment,
- carbon capture,
- and accounting boundary.

---

## Observation 8 — Cement is a particularly good first use case

The calcination reaction provides a very clear chemical relationship.

This makes cement an excellent demonstration case for the project because part of the emissions can be constrained from material chemistry before any satellite analysis is performed.

The plan could use cement as the **reference validation case**, then add steel as the more complex second case.

---

# 4. Remote Sensing

## Observation 9 — The biggest scientific risk is the NO2 -> CO2 relationship

The plan proposes:

`CO2 Mass Flow proportional to integrated NO2 VCD`

with an empirical/stoichiometric coefficient.

This is not generally a direct physical conversion.

NOx emissions depend strongly on:
- combustion conditions,
- temperature,
- fuel composition,
- burner design,
- process technology,
- abatement systems,
- operating conditions,
- and atmospheric chemistry.

Therefore, the model should be described as a **proxy relationship** rather than a direct conversion.

### Recommendation

Instead of predicting:

`CO2 mass flow`

initially predict:

`industrial activity / emission anomaly score`

and test whether that score correlates with independently available facility-level emissions.

---

## Observation 10 — Sentinel-5P spatial resolution is a major limitation

The plan correctly identifies coarse spatial resolution as a risk.

This should be elevated from a risk-management item to a **central methodological limitation**.

A single TROPOMI pixel can contain:
- multiple industrial sources,
- roads,
- power generation,
- urban emissions,
- surrounding facilities,
- and meteorological effects.

Consequently, facility attribution must be treated probabilistically rather than as a simple spatial lookup.

### Recommendation

Include source attribution uncertainty in the output:

`Facility attribution confidence = high / medium / low`

---

## Observation 11 — Sentinel-2 SWIR should not be described as direct thermal infrared

The plan calls Sentinel-2 SWIR imagery "thermal infrared signatures."

Sentinel-2 MSI is a multispectral optical/SWIR instrument rather than a conventional thermal infrared sensor.

The proposed SWIR activity indicator may still be useful, but the terminology should be corrected.

More importantly, the proposed NHI should be treated as a **research hypothesis requiring validation**, not as an established operational-temperature detector.

### Recommendation

Use language such as:

> "SWIR-based industrial activity/anomaly indicator"

rather than:

> "thermal infrared temperature detection"

unless a proper thermal product is introduced.

---

## Observation 12 — Sentinel-2 operational detection is vulnerable to cloud and revisit constraints

The plan acknowledges cloud cover, but the impact should be reflected in the evaluation design.

A facility may appear inactive because:
- the scene is cloudy,
- haze affects retrieval,
- acquisition timing is unfavorable,
- the relevant area is contaminated by other surfaces,
- or the plant genuinely stopped.

Therefore:

`no detected hotspot != plant inactive`

The system needs an **insufficient-observation state** rather than forcing a binary active/inactive decision.

---

# 5. Data Sources

## Observation 13 — The data-source table is strong, but each dataset needs a formal data dictionary

For every source, document:
- spatial resolution,
- temporal resolution,
- units,
- coordinate reference system,
- uncertainty/quality flags,
- licensing,
- missing-data behavior,
- version/date,
- and exact variables used.

This is especially important for Sentinel-5P and E-PRTR.

### Recommendation

Create:

`docs/data_dictionary.md`

and:

`docs/data_provenance.md`

---

## Observation 14 — E-PRTR should not automatically be treated as exact facility ground truth

E-PRTR is valuable for benchmarking, but annual reported emissions are not equivalent to the satellite's instantaneous or overpass-time signal.

Potential differences include:
- reporting period,
- methodology,
- source aggregation,
- facility boundaries,
- temporal aggregation,
- pollutant definitions,
- and satellite observation timing.

Therefore, describe E-PRTR as:

> "independent regulatory/reference data"

rather than perfect ground truth.

---

# 6. Architecture

## Observation 15 — The architecture is technically impressive but too large for a capstone

The current plan contains:

- FastAPI
- Streamlit
- React/Next.js
- PostgreSQL/PostGIS
- Docker
- Terraform
- AWS
- CI/CD
- LLM agent
- document parser
- TROPOMI pipeline
- Sentinel-2 pipeline
- stoichiometric engine
- flux model
- PDF generation
- maps
- benchmark database

This is effectively a small production platform.

For a capstone, the danger is that infrastructure consumes the time needed to produce scientifically meaningful results.

### Recommendation: define a strict MVP

**Must have**
1. Cement + steel stoichiometric engine
2. One satellite activity indicator
3. Facility registry matching
4. Synthetic CBAM declaration parser
5. Evidence-fusion risk score
6. Quantitative evaluation
7. Streamlit demo

**Should have**
- second satellite modality
- LLM tool calling
- PDF report

**Could have**
- FastAPI
- PostgreSQL/PostGIS
- React
- AWS deployment
- Terraform
- advanced agent autonomy

---

# 7. LLM Agent

## Observation 16 — The LLM should orchestrate, not decide scientific truth

This is one of the most important architectural principles for the project.

The LLM should:

`extract -> call tools -> collect outputs -> explain evidence`

It should NOT:

`invent -> estimate -> decide`

The plan already moves in this direction with Pydantic and tool calling, which is good.

### Recommended architecture

`Declaration`

-> `Structured extraction`

-> `Deterministic validation`

-> `Stoichiometric engine`

-> `Satellite engine`

-> `Registry/database evidence`

-> `Risk scoring`

-> `LLM explanation`

This makes the final result reproducible.

---

## Observation 17 — Separate the deterministic score from the LLM explanation

The "Discrepancy & Fraud Risk Index" should be calculated by deterministic code.

For example:

`Risk = f(stoichiometric_violation, activity_discrepancy, data_quality, source_confidence)`

The LLM can then explain why the score is high.

This is much easier to evaluate academically than allowing an LLM to directly produce the score.

---

# 8. Validation and Metrics

## Observation 18 — The validation protocol is currently the weakest section

The plan proposes correlations between satellite indices and E-PRTR emissions.

The central problem is that annual E-PRTR emissions and satellite-derived observations operate at very different temporal and spatial scales.

A correlation may be interesting but does not automatically validate facility-level emission estimation.

### Recommendation

Use multiple evaluation questions:

### A. Stoichiometric engine
- numerical correctness
- conservation checks
- unit tests
- sensitivity analysis

### B. Satellite activity model
- precision/recall for known operational states
- temporal consistency
- false alarm rate
- missing-observation rate

### C. Facility attribution
- correct facility/source association
- confidence calibration

### D. Risk engine
- fraud detection precision
- recall
- F1
- false-positive rate
- calibration

### E. End-to-end system
- correct evidence retrieval
- reproducibility
- audit trace completeness

---

## Observation 19 — 25 steelworks + 25 kilns may be difficult to validate properly

The plan proposes 50 facilities.

This sounds rigorous, but the true sample size may be much smaller after filtering for:
- cloud-free observations,
- suitable satellite passes,
- reliable facility coordinates,
- identifiable production route,
- usable emissions data,
- and sufficient temporal overlap.

A smaller but carefully documented sample is better than a large nominal sample with weak observations.

### Recommendation

Define:

`candidate facilities -> quality filtering -> final evaluation cohort`

and report how many facilities survive each stage.

---

## Observation 20 — Synthetic fraud cases are useful but cannot substitute for real fraud labels

The 100-case synthetic benchmark is a good idea for testing the system.

However, because the labels are created by the project itself, it mainly demonstrates whether the system can detect **known injected inconsistencies**.

It does not establish real-world fraud detection performance.

The final report should explicitly distinguish:

- synthetic benchmark performance
- real-world external validation

---

# 9. Risk Management

## Observation 21 — Add uncertainty propagation

The risk matrix focuses mainly on engineering risks.

The scientific model also needs uncertainty estimates.

For example:

`Satellite measurement uncertainty`

+

`wind uncertainty`

+

`background uncertainty`

+

`facility attribution uncertainty`

=

`overall evidence uncertainty`

A risk score without uncertainty could look more precise than the evidence warrants.

---

## Observation 22 — Add a "cannot determine" state

The system should be allowed to return:

> **Insufficient evidence for reliable assessment**

rather than forcing:

> Compliant / Fraudulent

This is especially important because satellite observations are incomplete.

A useful classification could be:

- Low risk
- Medium risk
- High risk
- Insufficient evidence

---

# 10. Timeline

## Observation 23 — The timeline is aggressive

The plan goes from data ingestion to:
- remote sensing,
- stoichiometry,
- benchmarking,
- LLM agent,
- web application,
- deployment,
- PDF generation,
- and final validation in approximately 12–14 weeks.

This is possible only if the MVP is tightly controlled.

### Recommended priority order

**Weeks 1–3**
- regulatory scope
- data access
- facility selection
- stoichiometric baseline

**Weeks 4–6**
- satellite pipeline
- quality filtering
- activity indicator

**Weeks 7–8**
- validation
- uncertainty analysis

**Weeks 9–10**
- declaration parser
- deterministic risk engine
- LLM explanation layer

**Weeks 11–12**
- dashboard
- end-to-end testing

**Final period**
- scientific analysis
- report
- presentation

---

# 11. Repository Structure

## Observation 24 — The repository structure is good, but add explicit research artifacts

The current structure is software-engineering oriented.

Add:

```text
docs/
├── methodology/
│   ├── regulatory_scope.md
│   ├── stoichiometric_assumptions.md
│   ├── remote_sensing_methodology.md
│   └── validation_protocol.md
├── data/
│   ├── data_dictionary.md
│   └── data_provenance.md
└── decisions/
    └── architecture_decisions.md
```

Also add experiment tracking:

```text
experiments/
├── configs/
├── runs/
└── results/
```

This will make the project much easier to defend academically.

---

# 12. Research Question

## Observation 25 — The project needs one explicit central research question

The current plan has many objectives but no single dominant research question.

A stronger capstone formulation would be:

> **To what extent can chemical stoichiometric constraints and satellite-derived industrial activity indicators improve the identification of inconsistent CBAM emissions declarations?**

Possible subquestions:

1. How accurately can process-specific stoichiometric constraints identify physically implausible declarations?
2. Can satellite-derived indicators distinguish declared industrial activity levels?
3. Does combining independent evidence sources improve fraud/inconsistency detection compared with either source alone?
4. How does uncertainty affect the reliability of the resulting risk score?

This gives the project a clear scientific contribution.

---

# 13. Recommended Experimental Design

A particularly strong experiment would compare four models:

### Model A — Declaration only
Uses reported CBAM values.

### Model B — Stoichiometry only
Uses physical/process constraints.

### Model C — Satellite only
Uses remote-sensing activity indicators.

### Model D — Multimodal evidence fusion
Combines A + B + C.

Then compare:

- Precision
- Recall
- F1
- False-positive rate
- Calibration
- Explainability

The central research result becomes:

> **Does multimodal evidence fusion outperform individual evidence sources?**

That is a much stronger Data Science contribution than simply building a dashboard.

---

# 14. Important Terminology Changes

The following terminology should be reviewed throughout the document.

| Current wording | Safer / more precise wording |
|---|---|
| "verify emissions" | "assess consistency of reported emissions" |
| "fraud detection" | "fraud/inconsistency risk detection" |
| "certified verification dossier" | "automated audit-support dossier" |
| "ground truth" | "independent reference data" |
| "thermal infrared Sentinel-2" | "SWIR-based activity indicator" |
| "CO2 mass flow from NO2" | "CO2-related activity/emission proxy derived from NO2" |
| "thermodynamic minimum" | "stoichiometric/process lower bound" where appropriate |
| "prove falsification" | "flag physical inconsistency" |

---

# 15. Recommended MVP

If the project must be reduced, I would build this version:

```text
CBAM Declaration
       |
       v
Structured extraction
       |
       +--------------------+
       |                    |
       v                    v
Stoichiometric         Facility Registry
Bound Engine                 |
       |                     |
       |                     v
       |              Satellite Activity
       |                     |
       +----------+----------+
                  |
                  v
        Deterministic Risk Engine
                  |
                  v
         Evidence + Uncertainty
                  |
                  v
           LLM Explanation
                  |
                  v
           Streamlit Dashboard
```

### Initial sectors

**1. Cement**
- strongest chemical/stoichiometric foundation

**2. Steel**
- more complex and therefore valuable as the second case

Avoid implementing all six CBAM sectors during the capstone unless the core system is already complete.

---

# 16. Final Assessment

### Strengths

- Strong interdisciplinary concept.
- Excellent fit with chemical engineering + data science.
- Clear practical relevance.
- Strong use of open/public data.
- Good opportunity for explainable AI.
- Stoichiometric component provides deterministic scientific reasoning.
- Remote sensing provides an independent evidence source.
- Synthetic red-team testing is a useful addition.
- The proposed repository and engineering architecture are unusually mature for a capstone.

### Main weaknesses

1. The project currently claims more regulatory/physical certainty than the proposed evidence can support.
2. Satellite-to-emission conversion is the largest scientific risk.
3. Sentinel-2 terminology and the proposed SWIR "thermal" interpretation need refinement.
4. E-PRTR should not be treated as perfect ground truth.
5. The LLM should not be responsible for numerical truth or the core risk score.
6. The scope is too large for a single capstone unless an MVP is enforced.
7. The validation design needs stronger temporal/spatial alignment.
8. Uncertainty and "insufficient evidence" states need to become first-class components.
9. A single central research question is needed.
10. Regulatory claims need explicit primary-source documentation.

---

# 17. Priority Actions Before Proposal Submission

## Priority 1 — Narrow the claim

Change the core claim from:

> autonomous verification of CBAM emissions

to something closer to:

> multimodal consistency assessment and risk screening for CBAM emissions declarations.

## Priority 2 — Freeze the MVP

Commit to:

- Steel
- Cement
- Stoichiometric engine
- One primary satellite activity methodology
- Registry matching
- Deterministic risk score
- LLM explanation
- Streamlit dashboard

## Priority 3 — Define the research question

Use the multimodal evidence-fusion question as the central scientific contribution.

## Priority 4 — Formalize assumptions

Create explicit methodology documents for:
- CBAM accounting boundaries
- production routes
- stoichiometric assumptions
- satellite preprocessing
- facility attribution
- uncertainty
- evaluation

## Priority 5 — Design the validation before building the full system

Select the facilities and define exactly what constitutes:
- positive evidence,
- negative evidence,
- missing evidence,
- and ground/reference data.

This prevents the project from building a sophisticated pipeline and only afterward discovering that the outputs cannot be scientifically validated.

---

## Bottom line

**The concept is strong enough for a very good capstone, but it should be reframed from an "autonomous CBAM verification/certification platform" into an "evidence-fusion CBAM consistency and risk-assessment system."**

The most valuable scientific contribution is not whether the system can directly measure a factory's CO2 from space. It is whether **independent chemical constraints + remote-sensing activity evidence + structured declaration analysis can identify inconsistent declarations more reliably than any individual evidence source.**

That is ambitious, measurable, explainable, and much easier to defend academically.

