# VeriCBAM Streamlit UI: Design and Order Improvements

**Reviewed:** `src/ui/app.py` (843 lines), `src/ui/stitch_cockpit.html` (332 lines), `docs/STITCH_DESIGN.md`.
**Goal:** a cockpit that follows the user's journey, never shows a number it cannot back up, and is easier to maintain.
**Companion file:** `VeriCBAM_Necessary_Fixes.md` (the content and claim fixes referenced below are listed there as M1-M11).

---

## 1. What works today (keep it)

- A coherent dark "Stitch" palette with clear tokens (canvas `#0f131c`, card `#1c2028`, cyan, emerald, amber, crimson) and a short, readable spec in `STITCH_DESIGN.md`.
- Good contrast. I computed the ratios: secondary text on canvas 7.2:1, on cards 6.4:1, primary text on cards 14.9:1, and all four status badges between 5.7:1 and 5.9:1, so everything clears WCAG AA (4.5:1).
- A dark Plotly theme helper (`apply_stitch_plotly_theme`) used consistently.
- Sensible domain features: facility map with time series, physics calculators, a standalone pre-check, a fusion simulator with prior sensitivity.
- Explicit verdict vocabulary (Consistent, Potential Inconsistency, High Inconsistency Risk, Insufficient Evidence). This is the strongest piece of UX in the app.

---

## 2. Problems found

### 2.1 Content integrity (fix first; these are credibility issues, not styling)

| Where | Problem | Fix |
|---|---|---|
| Page 7 (benchmark) | Reads the legacy 101-case files and shows hard-coded captions "Zero False Positives" and "Lowest Error". The primary 326-case graded results are not in the UI. | Load `graded_model_comparison_summary.csv`; move legacy under an expander (Necessary Fixes M4) |
| `stitch_cockpit.html` (shown on page 1) | Static numbers: "Fused Model ROC-AUC 0.9984", "+0.0984 over single-modality baseline", "Audit Confidence & Calibrated Discrimination 99.2%". None match any result file. | Generate from result files, or delete the metric cards |
| Page 1, 3, 6 text | "Thermodynamic floor", "independent evidence", "calibrated", 2025/2551 called an Implementing Regulation | Wording pass (Necessary Fixes M2, Section 2) |
| Sidebar | Student and supervisor details sit permanently under the navigation | Move to an About page |

### 2.2 Information architecture (order)

The sidebar is a flat list of eight radio items whose order follows the *thesis chapters*, not a user's task:

1. Executive Overview, 2. Cohort, 3. Physics Engine, 4. Standalone Pre-Check, 5. Satellite, 6. Fusion, 7. Ablation Benchmark, 8. Proposal and Roadmap.

Consequences:
- The user's main task ("check one declaration") is split across **three** pages (3, 4, 6) with three different input forms.
- The Standalone Pre-Check, which is your most practical feature, is item 4 of 8.
- A "Capstone Proposal & Roadmap" page sits in the product navigation; it is documentation, not a tool.
- Evidence streams (physics, satellite, history) are pages, but there is no page where you see them **together for one plant**, which is the whole point of fusion.

### 2.3 Visual and interaction issues

- **Dense, uniform "bento" cards.** Page 3 shows four cards per row, repeated for two sectors, and page 7 four more. Everything has equal visual weight, so the eye has no starting point.
- **Verdict is not the hero.** On page 6 the badge is small and sits above two cards; the evidence breakdown follows. The decision should dominate.
- **Raw HTML in dozens of f-strings** (`unsafe_allow_html=True`), repeated card markup, and ~130 lines of CSS inside `app.py`. Hard to change a card once and have it update everywhere.
- **Emoji as icons** in badges ("🚨", "✅", "⚠️") render differently per OS, and color is the only other cue. Add text labels (you already do) and consistent glyphs.
- **External dependencies at runtime:** sidebar icon from `img.icons8.com` and fonts from Google Fonts. The app breaks visually offline (for example at a defense with no Wi-Fi).
- **One 843-line `if/elif` script.** Every interaction re-runs the whole file; there is no shared state, so selecting a plant on page 2 does not carry to page 5.
- **Missing states:** no empty/error state if result files are absent, no loading indicator for the satellite client, and no download buttons.

---

## 3. Proposed information architecture

Group navigation by user task and put the main workflow first. With Streamlit ≥ 1.36 use `st.navigation`:

```
HOME
  Overview                    (what it is, scope banner, 3 honest headline findings)

SCREEN
  Screen a declaration        (the main workflow: one form, one verdict, all evidence)
  Supplier pre-check          (stoichiometry-only, works for any supplier)

EXPLORE EVIDENCE
  Plant explorer              (map + time series + NOx/CO2 + satellite for one plant)
  Physics calculator          (cement / steel floors, route benchmarks)
  Satellite (Sentinel-5P)     (auxiliary evidence, with its limits stated)

EVALUATION
  Benchmark results           (326-case graded evaluation, CIs, triage)
  Legacy benchmark            (101 cases, collapsed, labelled as regression only)

ABOUT
  Method & limitations        (model card)
  References & roadmap        (current page 8)
  Author & project            (student / supervisor details)
```

Why this order:
1. A first-time visitor sees the purpose and the scope, then the tool, then the proof, then the background.
2. The same plant selection (kept in `st.session_state`) carries from Explorer to Screen.
3. Fusion is no longer a separate "simulator": it is the **output** of the Screen page, with sliders moved into an "Advanced / what-if" expander.

---

## 4. Page designs

### 4.1 Overview

```
┌──────────────────────────────────────────────────────────────┐
│  VeriCBAM                       [scope banner, always visible] │
│  Plant-level consistency screening for CBAM declarations.     │
│  Controlled benchmark · not a legal verification              │
├───────────────┬───────────────┬───────────────────────────────┤
│ 30 plants     │ 326 cases     │ Learned fusion AUC 0.965      │
│ 177 plant-yrs │ 177 real neg. │ (95% CI from bootstrap)       │
├───────────────┴───────────────┴───────────────────────────────┤
│ What we learned (3 bullets, from result files, not hard-coded)│
│ • Historical + learned fusion detect ≥20% understatement      │
│ • Expert-weighted fusion over-flags real years (FPR 25%)      │
│ • Satellite NO₂ inconclusive in a 5-plant pilot               │
├───────────────────────────────────────────────────────────────┤
│  [Screen a declaration →]   [See benchmark results →]         │
└───────────────────────────────────────────────────────────────┘
```

- Drop the embedded cockpit iframe, or keep it only after its numbers come from result files.
- Pull all figures from the CSVs with a small helper so they can never drift from the results.

### 4.2 Screen a declaration (the main page; merges current pages 3, 4, 6)

```
┌ Inputs (left, st.form) ───────┐ ┌ Result (right) ─────────────────────────┐
│ Plant:  [select from cohort]  │ │  ┌───────────────────────────────────┐  │
│   or    [manual: sector,      │ │  │  POTENTIAL INCONSISTENCY          │  │
│          route, capacity]     │ │  │  Risk 62%  (CI 48-75%)            │  │
│ Declared CO₂ (t):  [______]   │ │  │  Evidence completeness  ▓▓▓▓░ 4/5 │  │
│ Year: [2023]                  │ │  └───────────────────────────────────┘  │
│ ▸ Advanced (prior, weights)   │ │  Why? (waterfall: prior → posterior)    │
│ [ Run screening ]             │ │   Prior            ▏ 8%                 │
└───────────────────────────────┘ │   Stoichiometry    ▕███ +…              │
                                  │   History          ▕██ +…               │
                                  │   NOx/CO₂          ▕█ +…                │
                                  │   Satellite        ▕ ~0 (auxiliary)     │
                                  │  Missing: registry route (unverified)   │
                                  │  What would change this verdict: …      │
                                  │  [Download dossier PDF]                 │
                                  └─────────────────────────────────────────┘
```

Key behaviors:
- **Verdict is the hero** (large badge, one number, one interval). Show the posterior **and** the evidence confidence separately, as your engine already does.
- **Waterfall chart** of each stream's contribution `w_i · C_i · ln(LR_i)`, from the prior logit to the posterior. This is the most explainable view of your fusion and costs little because the engine already returns per-stream values.
- **Show abstention explicitly:** "Insufficient Evidence: capacity unknown", never a number. This aligns with removing the invented steel capacity (M3).
- **Show what is missing** and what extra evidence would change the verdict.
- Put prior and weights in an expander so a casual user does not move them by accident.
- Download button: a one-page dossier (markdown or PDF) with verdict, evidence and caveats.

### 4.3 Supplier pre-check

Keep it as its own page: it needs no satellite or history, so it works for non-EU suppliers. Add a horizontal "range bar" showing floor, typical range and the declared value as a marker; this reads faster than two cards.

### 4.4 Plant explorer

- Map on the left, details on the right (instead of stacked), with a persistent plant selection.
- Tabs inside the page: **CO₂ history**, **NOx/CO₂ ratio**, **Satellite**, **Registry**.
- Show data-quality flags (duplicate raw rows, rounding, missing years) beside the chart.

### 4.5 Satellite page

- State the finding plainly in a callout: "Pilot (5 plants, 2-13 clear days per summer): inconclusive."
- Replace the "Remote Verdict" card with **coverage** (valid days, cloud fraction) and a scatter of NO₂ vs reported CO₂ with n and the Spearman value.
- Label as "auxiliary evidence" in the page title.

### 4.6 Benchmark results (replaces current page 7)

Order the page from most important to supporting:

1. **Headline table** (326 cases, 30 plants): ROC-AUC, PR-AUC, Brier, ECE, **FPR on real years**, each with a 95% bootstrap interval.
2. **Detection vs understatement size**: line chart, recall by δ (5, 10, 20, 30, 50%) for expert and learned models, plus a toggle for the label threshold (5% or 10%).
3. **Triage curve**: share of true inconsistencies caught vs share of declarations reviewed, for **both** models and a random line.
4. **Calibration**: reliability diagram.
5. Expander: legacy 101-case results, with the banner "controlled regression test, not the main result".

Add a standing caption under every chart: "30 independent plants; synthetic understatements applied to real plant-years."

---

## 5. Design system improvements

Keep the Stitch palette. Tighten how it is applied.

1. **Tokens in one place.** Create `.streamlit/config.toml` for the base theme and `src/ui/assets/theme.css` for the rest; load it once.

```toml
# .streamlit/config.toml
[theme]
base = "dark"
backgroundColor = "#0f131c"
secondaryBackgroundColor = "#1c2028"
textColor = "#f1f5f9"
primaryColor = "#8ed5ff"
font = "sans serif"
```

2. **Component helpers** instead of repeated HTML (`src/ui/components.py`):

```python
import html, streamlit as st

TONES = {"ok": "#4edea3", "warn": "#facc15", "risk": "#ffb4ab", "muted": "#94a3b8"}

def metric_card(label, value, sub="", tone="muted"):
    st.markdown(
        f'<div class="bento-card"><div class="bento-label">{html.escape(label)}</div>'
        f'<div class="bento-value" style="color:{TONES[tone]}">{html.escape(str(value))}</div>'
        f'<div class="bento-sub">{html.escape(sub)}</div></div>', unsafe_allow_html=True)

VERDICT_TONE = {"Consistent": "ok", "Potential Inconsistency": "warn",
                "High Inconsistency Risk": "risk", "Insufficient Evidence": "muted"}

def verdict_badge(verdict):
    tone = VERDICT_TONE[verdict]
    st.markdown(f'<div class="status-badge badge-{tone}">{html.escape(verdict.upper())}</div>',
                unsafe_allow_html=True)

def scope_banner():
    st.info("Plant-level consistency screening on a controlled benchmark. "
            "Not a legal CBAM verification; accredited verifiers decide.")
```

   Using `html.escape` on dynamic values also removes the (small) HTML-injection risk from facility names.
3. **Visual hierarchy:** one large "hero" element per page (the verdict, the headline table, or the map). Reduce secondary cards from four-up to two-up or inline captions.
4. **Status is never color-only:** keep text labels, add a small glyph, and use a pattern or label on charts (do not rely on amber vs red alone).
5. **Typography:** keep Inter for text and JetBrains Mono for numbers; self-host both (or fall back to system fonts) so the app looks the same offline.
6. **Spacing:** use a 4/8/16/24 px scale; set a max content width on text-heavy pages so paragraphs stay readable.
7. **Replace the external sidebar icon** with a local SVG or an emoji in `st.set_page_config(page_icon=...)`.

---

## 6. Honest-UX patterns (specific to this project)

These are as much UI requirements as the styling:

| Pattern | Implementation |
|---|---|
| Scope banner on every page | `scope_banner()` at the top of each page |
| No standalone accuracy claims | Every metric shows the benchmark name, n, and a CI or "n = 30 plants" |
| Label synthetic data | Badge "synthetic perturbation on real plant-years" beside benchmark numbers |
| Show abstention | "Insufficient Evidence" with the reason, never a fabricated number |
| Show evidence completeness | "4 of 5 streams available" meter on every verdict |
| Mark experimental streams | Satellite tagged "auxiliary / experimental" everywhere it appears |
| No hard-coded results | `load_metrics()` helper reading CSVs; fail with a clear message if a file is missing |
| Respect the regulation | Say "Delegated Regulation (EU) 2025/2551" and never state a legal materiality for plant-level data |

---

## 7. Technical improvements

| Area | Change |
|---|---|
| Structure | Split into `src/ui/pages/*.py` plus `src/ui/components.py`; use `st.navigation` and `st.Page`. Target < 200 lines per page. |
| Versions | `st.navigation` needs Streamlit ≥ 1.36 and `px.scatter_map` needs Plotly ≥ 5.24. Update `requirements.txt` (currently `streamlit>=1.30`, `plotly>=5.18`). |
| State | Store the selected plant in `st.session_state["facility_id"]` so it persists across pages. |
| Caching | `@st.cache_data` for result CSVs and the cohort; `@st.cache_resource` for the fusion engine and satellite client (currently re-created on interaction). |
| Forms | Wrap inputs in `st.form` so the engine runs once on submit, not on every slider move. |
| Robustness | Wrap result-file loads in a helper that shows `st.warning` with the missing path and the command to regenerate it. |
| Offline | Self-host fonts and icon; remove runtime calls to `icons8` and Google Fonts. |
| Exports | `st.download_button` for the dossier (markdown/PDF) and for the benchmark table (CSV). |
| Testing | Add `streamlit.testing.v1.AppTest` smoke tests: every page loads without exception with the bundled data; the Screen page returns one of the four verdicts. |
| Cockpit HTML | If kept, render it from a Jinja-style template filled from result files; otherwise delete it from `README` and the repo tree. |
| Accessibility | Keyboard-reachable controls (default), alt text for the map and charts via captions, no color-only status. |

---

## 8. Implementation plan

| Step | Task | Effort |
|---|---|---|
| 1 | Content corrections from `VeriCBAM_Necessary_Fixes.md` that touch the UI (page 7 data source, cockpit numbers, regulation names, wording, sidebar details) | 2-3 h |
| 2 | Add `.streamlit/config.toml`, `theme.css`, `components.py` (`metric_card`, `verdict_badge`, `scope_banner`, `load_metrics`); replace repeated HTML | 3-4 h |
| 3 | Convert to `st.navigation` with the grouped structure; move pages into `src/ui/pages/` | 3-4 h |
| 4 | Build the **Screen a declaration** page (form, hero verdict, waterfall, missing-evidence list, dossier download); retire the separate fusion simulator | 1 day |
| 5 | Rebuild the **Benchmark results** page (headline table with CIs, recall vs δ, triage curve, reliability, collapsed legacy section) | 4-6 h |
| 6 | Plant explorer tabs; satellite page rewrite with honest framing | 4-6 h |
| 7 | `AppTest` smoke tests; screenshots for the report and README; offline check | 2-3 h |

**If you only have half a day:** do steps 1 and 2, add `scope_banner()` to every page, and replace the page-7 data source. That removes the credibility problems and most of the visual repetition.

---

## 9. Checklist

- [ ] No metric in the UI or in static HTML that is not read from a result file
- [ ] Graded 326-case results are the primary benchmark view; legacy is labelled
- [ ] Scope banner on every page
- [ ] Verdict is the largest element on the Screen page, with interval and evidence completeness
- [ ] "Insufficient Evidence" shown (with reason) wherever capacity or history is missing
- [ ] Satellite described as auxiliary/inconclusive everywhere
- [ ] Regulation names correct (Delegated 2025/2551; Implementing 2025/2546 and 2025/2547)
- [ ] Fonts and icons work offline
- [ ] Personal details moved to the About page
- [ ] Smoke tests pass for every page
