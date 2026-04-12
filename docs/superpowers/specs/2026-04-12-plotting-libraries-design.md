# Plotting Libraries Compared — Design Spec

## Goal
Add a dashboard mini project comparing four Python plotting libraries (Plotly, Matplotlib, Altair, Bokeh) using the same financial dataset, plus a blog article for the Tech Stack tab covering the comparison and outlier handling in financial charts.

## Deliverables
1. **Dashboard page:** `dashboard/pages/41_Plotting_Libraries.py`
2. **Blog article:** `docs/_posts/2026-04-12-plotting-libraries-compared.html`
3. **Tab rename:** `docs/_tabs/misc.md` title Misc → Tech Stack
4. **Dependencies:** add `altair`, `bokeh` to `dashboard/requirements.txt`
5. **Test file:** `dashboard/tests/test_plotting_libraries.py`

---

## 1. Dashboard Page

### Layout

```
┌─────────────────────────────────────────────┐
│  Sidebar: Ticker picker, date range,        │
│           period presets (1M/3M/6M/1Y)      │
├─────────────────────────────────────────────┤
│  TOP SECTION (always visible)               │
│  ┌─────────────────────────────────────┐    │
│  │ st.data_editor — OHLCV table        │    │
│  │ (editable, default: AAPL 6 months)  │    │
│  └─────────────────────────────────────┘    │
│  Outlier callout: flags rows where any      │
│  value > 3 std devs from column mean        │
├─────────────────────────────────────────────┤
│  BOTTOM SECTION (tabs)                      │
│  ┌────────┬────────────┬────────┬────────┐  │
│  │ Plotly │ Matplotlib │ Altair │ Bokeh  │  │
│  ├────────┴────────────┴────────┴────────┤  │
│  │  Line chart    (Close vs Date)        │  │
│  │  Candlestick   (OHLC vs Date)         │  │
│  │  Bar chart     (Volume vs Date)       │  │
│  │  Histogram     (Daily returns dist)   │  │
│  └───────────────────────────────────────┘  │
│  All four charts stacked vertically per tab │
└─────────────────────────────────────────────┘
```

### Data Flow
- Sidebar inputs (ticker, date range) → yfinance fetch → `st.session_state["df"]`
- `st.data_editor` renders the dataframe; user edits write back to session state
- Daily returns computed as `df["Close"].pct_change()` from the (possibly edited) data
- Outlier detection: flag any value > 3 standard deviations from its column mean; show as `st.warning` listing affected row dates
- Each library tab reads from the same session state dataframe and renders all four chart types
- Editing a cell (e.g., spiking Close to 10x) triggers re-render across all tabs

### Default State
- Ticker: AAPL
- Period: 6 months
- No edits applied — clean yfinance data

### Per-Tab Implementation

**Plotly** (`plotly.graph_objects`):
- Line: `go.Scatter`
- Candlestick: `go.Candlestick` (native)
- Bar: `go.Bar` for volume
- Histogram: `go.Histogram` on daily returns
- Render via `st.plotly_chart(use_container_width=True)`

**Matplotlib** (`matplotlib.pyplot`):
- Line: `ax.plot()`
- Candlestick: manual `ax.bar()` + `ax.vlines()` for wicks (no mplfinance dependency)
- Bar: `ax.bar()` for volume
- Histogram: `ax.hist()` on daily returns
- Render via `st.pyplot(fig)`

**Altair** (`altair`):
- Line: `alt.Chart().mark_line()`
- Candlestick: layered `mark_rule` (wicks) + `mark_bar` (bodies) with color encoding on open vs close
- Bar: `mark_bar()` for volume
- Histogram: `alt.Chart().mark_bar()` with `alt.X` bin transform on daily returns
- Render via `st.altair_chart(use_container_width=True)`

**Bokeh** (`bokeh.plotting`):
- Line: `p.line()`
- Candlestick: `p.segment()` (wicks) + `p.vbar()` (bodies)
- Bar: `p.vbar()` for volume
- Histogram: `p.quad()` on numpy histogram bins of daily returns
- Render via `st.bokeh_chart(use_container_width=True)`

### Outlier Handling (visible in charts)
Each tab includes a brief annotation approach for outlier values:
- **Plotly:** `add_annotation()` pointing to outlier data points
- **Matplotlib:** `ax.annotate()` with arrow
- **Altair:** conditional color encoding (outlier points in red)
- **Bokeh:** `p.circle()` overlay with distinct color for outlier points

---

## 2. Blog Article

**File:** `docs/_posts/2026-04-12-plotting-libraries-compared.html`
**Front matter:**
```yaml
---
layout: post
title: "Plotting Libraries Compared — Plotly, Matplotlib, Altair, Bokeh"
date: 2026-04-12
tags: [python, visualization, plotly, matplotlib, altair, bokeh, tech-stack]
categories:
  - Tech Stack
permalink: /tech-stack/plotting-libraries/
---
```

**Sections:**
1. **Intro** — why a quant developer should know more than one charting library
2. **The four libraries** — table summary (API style, interactivity, Streamlit support, learning curve) + prose on each library's philosophy:
   - Plotly: interactive-first, declarative, rich finance chart types
   - Matplotlib: imperative, pixel-level control, the ecosystem foundation
   - Altair: grammar-of-graphics, concise declarative transforms
   - Bokeh: interactive, server-side rendering, widget-native
3. **Same data, four views** — code snippets and screenshots from the dashboard page, link to live demo
4. **Outlier handling in financial charts:**
   - The visual problem: one extreme value compresses the rest of the chart
   - Detection: 3-sigma flagging
   - Display approaches per library: axis clipping, log scale, bin width tuning (histograms), annotation/markers
   - Code snippets showing each approach
5. **When to use what** — decision guide (2-3 sentence recommendation per library, honourable mention of Seaborn and mplfinance)
6. **Try it yourself** — link to the live QuantLab dashboard mini project

---

## 3. Tab Rename: Misc → Tech Stack

**File:** `docs/_tabs/misc.md`

Changes:
- `title: Misc` → `title: Tech Stack`
- Update lede text to reflect broader scope
- Add the plotting libraries post as a new entry in the "Technology references" section
- CSS class names (`misc-*`) can stay — they're internal, no public-facing impact
- `permalink: /misc/` stays unchanged to avoid breaking existing links; only the displayed title changes

---

## 4. Dependencies

Add to `dashboard/requirements.txt`:
```
altair>=5.2.0
bokeh>=3.3.0
```
Matplotlib is already a transitive dependency of Streamlit.

---

## 5. Test File

**File:** `dashboard/tests/test_plotting_libraries.py`

Follows the existing pattern in `conftest.py` (autouse mocks for yfinance, requests, etc.).

Tests:
- Page loads without error via `AppTest`
- Each library tab renders (tab switching doesn't crash)
- Outlier detection flags correct rows when data has a spiked value
- Data editor round-trip: edited values propagate to chart data
