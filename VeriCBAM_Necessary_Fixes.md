# VeriCBAM: What Is Truly Necessary to Fix

**Based on:** the latest `Capstone.zip` (with Copernicus multi-year data, graded benchmark, model card, Stitch UI) and `VeriCBAM_Issues_and_Scores.md`.
**How I used the review:** I checked every item against the code, data and (for the legal points) the published EU texts. Items are sorted into *must fix*, *cheap wording fixes*, *optional*, and *already done*. I also added findings the review did not contain.
**Not verified:** I could not run `pytest` (no pyarrow or pytest offline). `requirements.txt` does list `pyarrow`, and the suite has 19 test functions, so the earlier "6 failed" was most likely an environment problem. Confirm it in a clean venv.

---

## 0. The 20-second summary

The project is much more honest than it was two versions ago. The graded benchmark, the model card and the "satellite is auxiliary" framing are real improvements. What is still wrong falls into four groups:

1. **Legal and factual errors** (materiality, regulation type, an invented steel capacity, a verifier count that is probably wrong).
2. **The headline results shown to a reader still come from the old 101-case benchmark** (UI page 7, README section 6.2, and a static cockpit page with numbers that match no result).
3. **One evaluation asymmetry and one weak stream** inflate or blur the results (NOx baseline includes the tested year; satellite z is a per-plant constant).
4. **A live secret was in your earlier zips.** Rotate it.

If you have only one day, do Section 1 and Section 2.

---

## 1. Must fix (before submission or defense)

### M1. The 10% "materiality" claim is wrong (review #1: confirmed)

- **Where:** `src/benchmark/graded_benchmark_generator.py` line ~227 (comment: "delta >= 10% is material ... Implementing Reg 2025/2546"); `docs/MODEL_CARD.md` line 44 ("Material threshold under Reg. 2025/2546").
- **Fact:** Secondary sources on Implementing Regulation (EU) 2025/2546 report a **5%** materiality level, applied to **total specific embedded emissions at goods level**. Your data is plant-level E-PRTR CO₂, so neither 5% nor 10% is a legal CBAM materiality for your benchmark.
- **Also note:** your code currently labels 5% perturbations as non-material (label 0) and cites a regulation that, if anything, points to 5%. A reader who checks will catch this.
- **Fix:**
  1. Rename the rule: "project-defined screening threshold", not "material under 2025/2546".
  2. Run the evaluation with **both** thresholds (label = δ ≥ 5% and label = δ ≥ 10%) and report both. This is a label-sensitivity table and takes minutes.
  3. Add one sentence: "The regulation's 5% materiality applies to product-level specific embedded emissions; this benchmark is plant-level and does not test legal materiality."
  4. Before quoting the article number, read the materiality article in the official text: http://data.europa.eu/eli/reg_impl/2025/2546/oj

```python
# in run_graded_evaluation.py: evaluate under both label rules
for thr in (0.05, 0.10):
    y_thr = ((df.understatement_delta_pct/100 >= thr) | (df.evaluation_split=="Route_Mismatch")).astype(int)
    # recompute AUC/PR-AUC for every model with y_thr, save to graded_label_sensitivity.csv
```

### M2. Regulation 2025/2551 is a Delegated Regulation (review #2: confirmed)

- **Fact (EUR-Lex):** Commission **Delegated** Regulation (EU) 2025/2551 of 20 Nov 2025 (accreditation of verifiers). Commission **Implementing** Regulations (EU) 2025/2546 (verification principles) and 2025/2547 (calculation of embedded emissions) are correctly "Implementing".
- **Where to change** (search for `2025/2551`):
  - `README.md` lines 19, 21
  - `Capstone_Proposal_Document.md` lines 24, 31, 324
  - `src/ui/app.py` lines ~286-287, 293, 307
  - `admin/generate_official_application_pdf.py` lines 19-20 (then regenerate the PDF)
  - `docs/MODEL_CARD.md` line 12
- **Fix:** replace with "Commission Delegated Regulation (EU) 2025/2551". Add the ELI link http://data.europa.eu/eli/reg_del/2025/2551/oj once in the references.

### M3. Remove the invented steel capacity (review #3: confirmed, and larger than described)

- **Where:** `graded_benchmark_generator.py` lines ~148-150 and ~248-250 (`cap_mtpa = 2.0`), and line ~336 (route-mismatch branch, which has **no** guard at all).
- **Extra finding:** in your registry, **3 of 15 steel plants have `crude_steel_capacity_mtpa = 0.00`**: thyssenkrupp Hamborn, thyssenkrupp Beeckerwerth and DK Recycling und Roheisen. They all silently get 2.0 Mt, and the floors derived from it feed Models B and E and the logistic regression. Beeckerwerth is labelled "Downstream Rolling & Surface Coating" and DK Recycling "Foundry Pig Iron", so a crude-steel floor is questionable for both.
- **Fix:**
  1. Remove the fallback. If capacity is missing or ≤ 0, set the stoichiometry fields to `NaN`, set `stoich_available = False`, and exclude the plant from Model B and from the stoichiometry feature (or let the engine return *Insufficient Evidence*).
  2. Add a guard in the route-mismatch branch and skip plants without capacity.
  3. Report how many cases lose the stoichiometry stream (about 3 of 30 plants).
  4. Add a unit test: a plant with capacity 0 must not produce a numeric floor.

```python
cap = r_info.get("crude_steel_capacity_mtpa")
if pd.isna(cap) or cap <= 0:
    floor_central = floor_max = np.nan; stoich_available = False
```

### M4. The reader-facing headline still shows the legacy 101-case results (review #4: confirmed, and wider)

- **UI page 7** (`src/ui/app.py` ~line 764) reads `ablation_study_summary.csv` / `calibrated_predictions_101.parquet`. It shows "Model E F1", **"Zero False Positives"** and **"Lowest Error"** as hard-coded captions. The graded 326-case results appear nowhere in the UI.
- **`src/ui/stitch_cockpit.html`** (embedded on page 1) hard-codes "Fused Model ROC-AUC **0.9984**", "+0.0984 over single-modality baseline" and "Audit Confidence & Calibrated Discrimination **99.2%**". None of these match any result in the repo (legacy fused AUC is 0.9991; graded expert fusion is 0.7693).
- **README section 6.2** still presents "VeriCBAM Fused" F1 0.964 / AUC 0.9991 as a results table, followed by "Key Result: ... generalizes cleanly ... without facility data leakage".
- **Fix:**
  1. Make the graded benchmark (326 cases) the primary results page, loaded from `graded_model_comparison_summary.csv`.
  2. Move the 101-case results under a labelled expander or section: "Legacy controlled benchmark (regression and calibration tests only)".
  3. Delete or regenerate the static cockpit numbers from result files; do not hard-code metrics in HTML.
  4. Delete "Zero False Positives", "Lowest Error" and the "Key Result ... without facility data leakage" sentence.

### M5. Be straight about what the results say (new; not in the review)

The graded results in your own model card say:

| Model | ROC-AUC | FPR on real years |
|---|---|---|
| Historical alone (D) | 0.966 | 0.00% |
| **Expert Bayesian fusion (E1)** | **0.769** | **25.4%** |
| Learned logistic regression (E2) | 0.965 | 5.65% |

So the headline architecture (expert fusion) is **worse than its own historical stream** and flags about a quarter of genuine plant-years. That is an honest and useful finding, but the Proposal, the UI and the cockpit still tell the "fusion is best" story.

- **Fix the narrative** in README, Proposal, UI: "On the graded benchmark, a learned fusion matches the best single stream; the hand-parameterized expert fusion does not."
- **Diagnose before you explain.** One verified cause candidate: `run_graded_evaluation.py` passes `abs(historical_z_robust)` to the engine, so genuine *increases* in emissions are treated like suspicious *decreases*, although understatement can only produce decreases. Try a one-sided score (`max(0, -z)`) and re-run; I have not tested whether this explains the gap.
- Also run triage (precision@k) for the **learned** model; `run_graded_evaluation.py` currently computes it only for the expert model, the weaker of the two.

### M6. NOx baseline includes the year being tested (new)

- **Where:** `src/data_loaders/build_cohort.py`: the NOx/CO₂ fingerprint uses all years < 2023. Negatives from 2018-2022 are therefore scored against a baseline that contains their own value. Positives are all 2023 and out-of-sample.
- **Evidence (computed):** among 139 in-baseline negatives, **0** have |NOx z| > 2 (std 0.68); among 26 out-of-sample 2023 negatives, **3.6%** do (std 0.77). The stream looks cleaner on negatives than it would on new data, which biases AUC and FPR in your favour.
- **Fix:** compute the NOx baseline **leave-one-year-out**, exactly as you did for the CO₂ history. Re-run the evaluation.

### M7. Weights in the docs do not match the code (review #8: confirmed, and worse than described)

- **README lines 84-85** say `w_i ∈ [0,1]` with stoichiometry 1.0, satellite 0.35, historical 0.80, …
- **Code** uses stoichiometry 1.5, satellite 1.0, historical 1.0, NOx 1.2, registry 0.8, route 2.0 (`evidence_fusion.py`).
- **Fix:** state `w_i > 0` and copy the real values into the README, Proposal and Model Card from one table. The MODEL_CARD claim "w_sat ≤ 1.0" is true, but the README's 0.35 is not.

### M8. Bootstrap CIs are claimed but not computed (review #9: confirmed)

- `run_graded_evaluation.py` docstring promises plant-level bootstrap CIs and imports `bootstrap`, but never uses it.
- **Preferred fix (about 30 lines):** resample **facilities** with replacement, 1000 times, on the out-of-fold predictions, and report 95% CIs for AUC, PR-AUC, Brier and FPR. With only 30 independent facilities, these intervals matter.
- **Minimum fix:** delete the claim.

```python
rng = np.random.default_rng(0); fac = df.facility_id.unique(); aucs = []
for _ in range(1000):
    s = rng.choice(fac, len(fac), replace=True)
    b = pd.concat([df[df.facility_id == f] for f in s])
    if b.benchmark_label.nunique() == 2: aucs.append(roc_auc_score(b.benchmark_label, b[col]))
lo, hi = np.percentile(aucs, [2.5, 97.5])
```

### M9. Rotate the Copernicus secret (new; urgent)

`Copernicus.txt` with a live client ID and secret was inside the earlier zips. It is gone from the latest zip, and the zip builder, `.gitignore` and `build_reproducible_zip.py` now exclude it, which is good. But the secret was shared in those archives.

- **Fix:** generate a new client secret in your Copernicus Data Space account and revoke the old one.
- **Going forward:** read credentials from environment variables (`CDSE_CLIENT_ID`, `CDSE_CLIENT_SECRET`) with the file only as a local fallback. `copernicus_multiyear_client.py` currently parses any line containing "id" or "secret", which is fragile.

### M10. Unverified or probably wrong factual claims (new)

- "**~403 verification bodies globally hold active accreditation under … (EU) 2025/2551**" (README line 21, Proposal line 31, app.py line 293). Sources on the framework say the first CBAM verifier accreditations are expected around **September 2026**, so this number most likely refers to EU ETS verifiers, not CBAM. Re-source it or reword to "EU ETS accredited verifiers".
- "€50,000 to €150,000+ per site visit" and "~12,000 EU import entities": make sure each is tied to a citable source in the references, and word them as estimates.
- "physical on-site audits are mandatory" (Proposal line 24): reports on the rules describe site visits as the default with conditions under which they may be waived. Check the final text and soften if needed (review #14).

### M11. Run the test suite in a clean environment (review #5)

```powershell
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
```

Only keep the "19/19 passed" badge if this passes. Also add tests for the new code (below, P1).

---

## 2. Cheap wording fixes (do these in one pass; about 1 hour)

| Review # | Change | Where |
|---|---|---|
| 6 | "severe fraud" to "severe understatement"; never claim fraud or violation detection; say "screening of controlled inconsistencies" | Proposal line 159; search `fraud` |
| 7 | "independent evidence" to "heterogeneous evidence" | README 25; Proposal 47, 55, 73, 123; `evidence_fusion.py` line 12 |
| 13 | "thermodynamic floor/minimum" to "stoichiometric lower bound" or "route-specific engineering lower bound (BAT reference)". The BF-BOF 1.35 t/t and EAF 0.04 t/t are engineering benchmarks, not thermodynamic limits | `app.py` ~line 510, cement/steel docstrings, README, Proposal line 110 |
| 16 | "calibrated Bayesian" to "expert-parameterized Bayesian fusion" | `evidence_fusion.py` docstrings (lines 3, 42, 56, 69, 240) |
| 17 | Add: "The learned model is trained on labels defined by the same synthetic perturbation generator; it shows learnable structure in the benchmark, not real-world fraud detection" | Model Card section 3, README 6.1 |
| 10 | Route-mismatch count: 9 usable in the graded benchmark (11 only in the legacy suite). Fix the generator comment | `graded_benchmark_generator.py` line ~327 |
| 15 | Satellite "negative result" to "inconclusive / underpowered" (see N1) | README line 165 ("proved"), Model Card section 4 |

---

## 3. New findings the review did not cover

### N1. The satellite "negative result" is under-powered, not proven (change the wording)

- Multi-year file: **25 rows = 5 plants x 5 years**, all German cement plants (the client has `sample_only=True` as default).
- The column `valid_months` is really **valid days** (2 to 13 clear days per summer), and "annual mean" is a **June-August** mean. Both labels are misleading.
- Within-plant Spearman values range from **-0.70 to +0.70** with n = 5 each, so none is informative. The model card's "mean ρ = -0.100" is an average of five unstable numbers.
- No background subtraction, wind or footprint handling is used in this pull; an ~11 km box around a plant like CEMEX Rüdersdorf is dominated by Berlin background NO₂.
- **Fix:** say "inconclusive: the pilot (5 plants, 2-13 clear days per summer, no background correction) could not detect a relationship". Rename the columns (`valid_days`, `summer_mean_no2`). If time allows, run all 30 plants (`sample_only=False`), subtract a ring background, and add monthly means.
- **In the benchmark itself**, `satellite_z` is still a constant per plant (2023 overpass mean) applied to all years and all cases; the new multi-year data is not used there. Keep it auxiliary and say so.

### N2. Effective sample size is 30

All 140 graded positives are derived from the same 30 plants' 2023 rows (4 labelled levels x 30 + 5% sensitivity cases), and the 177 negatives come from the same plants. Group CV prevents leakage, but the *independent* sample is 30 plants. Say so beside every metric, and use the bootstrap in M8.

### N3. CO₂ variable choice: code and comment disagree (review #11: confirmed)

`build_cohort.py` documents a preference for "CO₂ excluding biomass" but uses total `Carbon dioxide (CO2)` as `co2_tonnes`. CBAM generally treats biomass differently, so excl-biomass is the better primary variable.

- **Fix:** choose one, update the comment and `DATA_PROVENANCE.md`, and re-run the pipeline if you switch. Either is defensible if justified.

### N4. Pooled MAD (review #12): document, do not rework

Pooled sigma (0.0911) is computed over all plant-years, including held-out plants. It is unsupervised, so the effect is small. One sentence in the Model Card is enough; fold-wise recomputation is optional.

### N5. No tests for the new code

`tests/` was not touched. Add small tests for: no-fallback capacity (M3), the label rule at both thresholds (M1), leave-one-year-out NOx baseline (M6), `build_cohort` duplicate rule, and one-sided historical score (M5).

---

## 4. Where I differ from the review's scores

| Area | Review | My view |
|---|---|---|
| Benchmark (4.5) | high | 3.5-4.0: negatives are now real (big improvement), but invented steel capacity, NOx self-inclusion, constant satellite z and n = 30 plants remain |
| Learned fusion (5.0) | perfect | 3.5-4.0: it matches the historical stream (AUC 0.965 vs 0.966), is trained on generator-defined labels, and has no CIs |
| Satellite interpretation (5.0) | perfect | 4.0: the framing is honest, but "proved" overstates a 5-plant pilot |
| Regulatory accuracy (3.0) | low | agree; the fixes above are quick |
| Bayesian fusion (3.5) | | agree; it underperforms and needs diagnosis |
| Overall 8.8/10 | | about 8.0 now; 8.5+ after Sections 1-2 |

---

## 5. Suggested order of work

| Step | Task | Time |
|---|---|---|
| 1 | M9: rotate the secret | 10 min |
| 2 | M2 + Section 2 wording pass (find-and-replace) | 1-2 h |
| 3 | M3: remove capacity fallback, rebuild benchmark | 1-2 h |
| 4 | M6: leave-one-year-out NOx baseline; M5: one-sided z; re-run graded evaluation | 2-3 h |
| 5 | M1: both label thresholds; M8: facility bootstrap CIs | 2-3 h |
| 6 | M4: switch UI page 7, cockpit and README 6.2 to graded results | 2-3 h |
| 7 | M7, M10, N3: docs consistency and sources | 1-2 h |
| 8 | M11 + N5: clean-venv test run, add tests | 2 h |
| 9 | N1: reword satellite claims (optional: full 30-plant pull) | 1 h (or 1 day) |

After step 6, regenerate every number in README, Proposal and Model Card from `experiments/results/*.csv`; do not type numbers by hand.

---

## 6. Optional (only if time allows)

- Fold-wise recomputation of pooled sigma (N4).
- Full 30-plant, multi-year Copernicus pull with background ring and monthly means.
- Extend the cohort to about 300 plants for history/NOx evaluation (see earlier plan).
- Compare real E-PRTR vs EU ETS discrepancies as an independent test set.

---

## 7. Already addressed (no action needed)

- Copernicus credentials excluded from the new zip, zip builder and `.gitignore`.
- Weights formula `w_i * C_i * ln(LR_i)` now appears in the engine docstring and Model Card.
- The early return that bypassed fusion with a fixed 0.999 posterior was removed, and the global random seed was replaced with a local generator. Note that a floor breach still uses LR = 1e6 and forces the "High Inconsistency Risk" verdict, so it remains effectively deterministic. That is acceptable if you document it as a hard physical flag rather than a probabilistic estimate.
- Graded benchmark uses real negatives, leave-one-year-out CO₂ history and a pooled robust scale.
- Model Card states the satellite limitation and the proxy-vs-CBAM caveat.
- `README` section 6.1 reports the unflattering graded results honestly (the problem is that 6.2 still sits beside it).
- `requirements.txt` includes `pyarrow`.
