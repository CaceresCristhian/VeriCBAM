# VeriCBAM Stitch Design System Specification

## Overview
This document specifies the design system guidelines for VeriCBAM (EU CBAM Emissions Consistency Assessment & Decision Support System). The system leverages the **Google Stitch Cockpit** dark-mode palette for executive regulatory visualization, combining crisp contrast, precise data density, and technical typography.

---

## 1. Color Palette

| Name | Hex Code | Role / Use Case |
| :--- | :--- | :--- |
| **Canvas Background** | `#0f131c` | Deep dark space for the main dashboard viewport |
| **Surface Container** | `#1c2028` | Cards, metric bento boxes, sidebar panels, input fields |
| **Border / Divider** | `#2d3440` | Highlighting card margins and structural borders |
| **Primary Accent (Cyan)** | `#8ed5ff` | Primary buttons, active tab indicators, glowing scatter points |
| **Secondary / Compliant (Emerald)** | `#4edea3` | Feasible/Consistent verdicts, compliant status badges |
| **Warning / Potential (Amber)** | `#facc15` | Potential inconsistency warnings, medium risk flags |
| **Risk / Violation (Crimson)** | `#ef4444` / `#ffb4ab` | Physical floor violations, high inconsistency risk badges |
| **Text Primary** | `#f1f5f9` | Primary headings, metric figures |
| **Text Secondary** | `#94a3b8` | Subtitles, labels, secondary metadata |

---

## 2. Typography

* **Body & Headings:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif`
* **Metrics, Numerical Data & Chemical Formulas:** `JetBrains Mono`, `Fira Code`, `monospace`

---

## 3. UI Component Specifications

### Bento-Style Metric Cards
- Background: `#1c2028`
- Border: `1px solid #2d3440`
- Border Radius: `12px`
- Padding: `20px`
- Title Label: `12px uppercase`, font-weight `600`, color `#94a3b8`
- Value: `28px`, font-family `JetBrains Mono`, color `#f1f5f9`
- Badge / Subtitle: `12px`, with status-dependent background pill (#4edea322 for green, #ef444422 for red).

### Status Badges
- **Consistent / Compliant:** Background `#064e3b`, Text `#4edea3`, Border `#047857`
- **Potential Inconsistency:** Background `#713f12`, Text `#facc15`, Border `#a16207`
- **High Inconsistency Risk:** Background `#7f1d1d`, Text `#ffb4ab`, Border `#b91c1c`
- **Insufficient Evidence:** Background `#1e293b`, Text `#94a3b8`, Border `#475569`

---

## 4. Charting Guidelines (Plotly & Folium)
- **Canvas:** `#0f131c`
- **Paper Background:** `#0f131c`
- **Grid Lines:** `#2d3440`
- **Font Color:** `#94a3b8`
- **Plot Colors:** `#8ed5ff` (Primary Cyan), `#4edea3` (Emerald), `#ef4444` (Crimson), `#facc15` (Amber).
