# QuantLab Streamlit Visual Redesign

**Date:** 2026-04-14
**Status:** Final — ready for implementation plan

## Goal

Lift the QuantLab Streamlit dashboard from "default Streamlit theme + scattered styling" to a unified minimalist-chic visual identity, in two passes:

- **Pass A** — Redesign the landing page (`app.py`) into a portfolio-style front door with a typographic hero, a featured section, and a content-categorised project grid. Lock in the visual identity (palette, typography, helper functions) here.
- **Pass B** — Propagate the visual language to every other page via a shared `render_page_header()` helper and global CSS in `nav.py`, so the entire dashboard reads as one designed product.

## Non-goals

- No screenshots/thumbnails on cards (text-only — minimalist discipline)
- No dark mode (light only — consistent with the editorial brief)
- No mobile-first redesign (Streamlit handles mobile reflow OK at this layout level)
- No Streamlit page tests (UI rendering, manual verification only)
- No new pages or new features — pure visual lift on existing content
- No JavaScript beyond what Streamlit already injects
- No new Python dependencies (CSS-only customisations via `st.markdown(unsafe_allow_html=True)`)

## Visual identity

### Palette

The FinBytes logo is dropped from the UI entirely. The dashboard becomes its own brand: **QuantLab**, monochrome with a single warm amber accent.

| Role | Hex | Used for |
|---|---|---|
| Primary accent | `#d97706` (amber-600) | Links, primary buttons, hero accent stripe, active nav |
| Text | `#1a1a1a` | Body copy, headlines, labels |
| Muted text | `#6b6b6b` | Captions, source citations, expander explainers |
| Background | `#ffffff` | Page background |
| Secondary background | `#fafafa` | Cards, expander bodies |
| Border | `#e5e5e5` | Hairline card borders, subtle dividers |

The Streamlit theme config (`.streamlit/config.toml`) is updated:

```toml
[theme]
primaryColor = "#d97706"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#fafafa"
textColor = "#1a1a1a"
```

Charts (Plotly) keep their existing colour palettes — data visualisation is the only place colour appears at full saturation.

### Typography

Two free Google Fonts, paired:

- **Fraunces** (variable serif) — page titles, section headings. Soft modern serif with subtle warmth.
- **Inter** (variable sans) — everything else: body text, labels, captions, buttons.

Loaded via Google Fonts CDN in a global `<style>` injection from `nav.py`. No font files committed to the repo.

```html
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

CSS variable mapping:
```css
:root {
  --rvb-font-display: 'Fraunces', Georgia, serif;
  --rvb-font-body: 'Inter', system-ui, -apple-system, sans-serif;
}

html, body, [class*="st-"], [class*="streamlit"] {
  font-family: var(--rvb-font-body);
}
h1, h2, h3 {
  font-family: var(--rvb-font-display);
  font-weight: 600;
  letter-spacing: -0.01em;
}
```

### Sidebar

The FinBytes logo image is removed. The sidebar header becomes pure typography:

```
QuantLab
Built by Manisha
─────────
[ … nav links … ]
```

Where "QuantLab" is the Fraunces title and the byline is small Inter muted grey.

## Architecture

### Files

**Quant_lab repo — modified files:**

| Path | Change |
|---|---|
| `dashboard/.streamlit/config.toml` | Update palette to amber + monochrome |
| `dashboard/lib/nav.py` | Inject global CSS (font load + theme variables + sidebar polish + expander styling already there). Replace logo image with text title. |
| `dashboard/app.py` | Full rewrite — new landing page (Welcome tab + System Health tab) |
| `dashboard/lib/page_header.py` | NEW — shared `render_page_header(title, subtitle=None)` helper |
| `dashboard/pages/*.py` | Each page replaces `st.title("X")` with `render_page_header("X", "subtitle")` (Pass B) |

**No new dependencies. No new data files. No tests.**

### Why this split

- All visual identity (CSS, fonts, palette) lives in **one place** (`nav.py`'s global injection) so future pages get it for free without per-page boilerplate.
- The landing page is **its own concern** in `app.py`, decoupled from the other pages.
- The page header helper is a **single function** in `lib/page_header.py` that every page calls — one place to change the heading style across the entire dashboard.
- The existing expander styling we shipped earlier stays where it is (already inside `nav.py`'s global CSS block). No duplication.

## Pass A — Landing page

### Structure

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│                      QuantLab                              │
│       Interactive finance and data experiments             │
│                     in Python                              │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  [ Welcome ]  [ System Health ]                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Featured                                                  │
│                                                            │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │ London     │ │ Etymology  │ │ Big O      │              │
│  │ House      │ │            │ │ Notation   │              │
│  │ Prices     │ │ Force-     │ │            │              │
│  │            │ │ directed   │ │ Log-log    │              │
│  │ Choropleth │ │ graph of   │ │ comparison │              │
│  │ maps...    │ │ word roots │ │ of algo... │              │
│  │            │ │            │ │            │              │
│  │ Python ·   │ │ D3.js ·    │ │ Python ·   │              │
│  │ Plotly     │ │ vanilla JS │ │ Plotly     │              │
│  └────────────┘ └────────────┘ └────────────┘              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │ Rent vs    │ │ Portfolio  │ │ Plotting   │              │
│  │ Buy        │ │ Optimisat. │ │ Libraries  │              │
│  │ London     │ │            │ │ Compared   │              │
│  └────────────┘ └────────────┘ └────────────┘              │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Personal finance & property                               │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐  │
│  │ ...│ │ ...│ │ ...│ │ ...│ │ ...│ │ ...│ │ ...│ │ ...│  │
│  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘  │
│                                                            │
│  Stocks & markets                                          │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ...             │
│                                                            │
│  Analytics & Fintech                                       │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ...                           │
│                                                            │
│  Tech demos & references                                   │
│  ┌────┐ ┌────┐ ┌────┐                                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Tab structure

Two tabs at the top of `app.py`:

1. **Welcome** (default) — the landing content shown above
2. **System Health** — the existing system status checks (preserved as-is, just moved into a tab)

### Hero

Pure typography, no logo, no image:

- **Title**: `QuantLab` — Fraunces serif, ~3.5rem, weight 600, letter-spacing -0.02em
- **Subtitle**: `Interactive finance and data experiments in Python` — Inter sans, ~1.1rem, muted grey, weight 400

Centered, generous vertical padding (4-5rem top, 3rem bottom). Hairline divider below the subtitle in border colour. No accent stripe on v1.

### Featured section

`<h2>Featured</h2>` (Fraunces serif), then a 3-column grid of 6 cards. Each featured card:

- White background, hairline border, generous padding (~1.5rem)
- **Title** — Fraunces serif, ~1.3rem, amber colour, link
- **Description** — Inter sans, body colour, ~0.95rem, 1-2 lines
- **Tech badges** — Inter sans, 0.75rem, muted grey, separated by ` · `
- Hover: subtle amber border, no shadow change

The 6 featured projects:
1. London House Prices (`/london-house-prices/`)
2. Etymology (`/quant-lab/etymology/embed/` via the Streamlit Etymology page)
3. Big O Notation (`/Big_O`)
4. Rent vs Buy London (`/Rent_vs_Buy`)
5. Portfolio Optimization (`/Portfolio_Optimization`)
6. Plotting Libraries Compared (`/Plotting_Libraries`)

### Categorised grid

`<h2>` for each category (Fraunces serif), then a responsive grid of compact cards (6-column on wide, 2-column on narrow). Each grid card:

- White background, hairline border, smaller padding (~1rem)
- **Title** — Inter sans (NOT Fraunces — visual hierarchy: featured cards use serif, grid cards use sans), ~1rem, amber colour, link, weight 600
- **Description** — Inter sans, body colour, ~0.85rem, 1 line
- **Tech badges** — even smaller, muted grey

Categories in this order (capstones bumped to the bottom of their category):

1. **Personal finance & property** — London House Prices, Rent vs Buy London, Credit Card Calculator, Loan Amortization, Loan Comparison, Retirement Calculator, Investment Planner, Budget Tracker, Personal Finance dashboard
2. **Stocks & markets** — Stock Tracker, Stock Analysis, Stock Prediction, Portfolio Optimization, Algo Trading Backtest, VaR & CVaR, Time Series, Anomaly Detection, Crypto Portfolio, Stock Risk Scanner *(capstone, last)*
3. **Analytics & Fintech** — Benchmark Rates, Currency Dashboard, Sentiment Analysis, Market Insights, ESG Tracker, Loan Default Prediction, Customer Clustering, Financial Reporting, Bond/Credit Risk AWS *(capstone, last)*
4. **Tech demos & references** — Big O Notation, Etymology, Plotting Libraries Compared

### Card data source

Project metadata (title, description, tech list, sidebar slug) is hardcoded in a single Python module:

```python
# dashboard/lib/projects.py
from dataclasses import dataclass

@dataclass
class Project:
    key: str           # sidebar page filename without .py and number prefix
    label: str         # display name
    description: str   # 1-line description
    tech: list[str]
    page_link: str     # streamlit page_link target
    is_capstone: bool = False

PROJECTS_BY_CATEGORY: dict[str, list[Project]] = {
    "Personal finance & property": [...],
    "Stocks & markets": [...],
    "Analytics & Fintech": [...],
    "Tech demos & references": [...],
}

FEATURED_KEYS = [
    "london_house_prices",
    "etymology",
    "big_o",
    "rent_vs_buy",
    "portfolio_optimization",
    "plotting_libraries",
]

def featured() -> list[Project]:
    flat = [p for projs in PROJECTS_BY_CATEGORY.values() for p in projs]
    by_key = {p.key: p for p in flat}
    return [by_key[k] for k in FEATURED_KEYS if k in by_key]
```

The landing page reads from this module. To add or remove a project from the dashboard later, you edit one Python file. No HTML/CSS changes needed.

## Pass B — Propagate visual language

### `render_page_header()` helper

New file `dashboard/lib/page_header.py`:

```python
"""Shared page header — call at the top of every dashboard page.

Renders a typographic h1 + optional subtitle that picks up the
global Fraunces/Inter styles injected by nav.render_sidebar().
"""

import streamlit as st


def render_page_header(title: str, subtitle: str | None = None) -> None:
    st.markdown(
        f'<h1 class="ql-page-title">{title}</h1>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<p class="ql-page-subtitle">{subtitle}</p>',
            unsafe_allow_html=True,
        )
```

The classes `ql-page-title` and `ql-page-subtitle` are styled by the global CSS in `nav.py`:

```css
.ql-page-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0.5rem 0 0.25rem;
  color: #1a1a1a;
}
.ql-page-subtitle {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 1rem;
  color: #6b6b6b;
  margin: 0 0 1.5rem;
}
```

### Per-page migration

Each existing page in `dashboard/pages/` is updated to:

1. Import `render_page_header` from `lib.page_header`
2. Replace `st.title("X")` with `render_page_header("X", "optional subtitle")`
3. Optionally replace inline tagline `st.caption(...)` calls that immediately follow the title with the subtitle parameter

Subtitle copy for each page is curated as part of the migration (1-line tagline that complements the title — e.g. "Stock Risk Scanner" → "Full-stack portfolio risk analysis with FastAPI, Postgres, and Claude").

### Global CSS in `nav.py`

The existing global injection in `_GLOBAL_STYLES` (currently has expander text styling only) is expanded to include:

1. Google Fonts `<link>` for Fraunces + Inter
2. CSS variables for the palette
3. Body font override → Inter
4. Heading font override → Fraunces
5. Streamlit widget label sizing/colour to use Inter at consistent weight
6. Streamlit primary button styling to use the amber accent
7. The existing expander text rules (smaller, greyer)
8. The new `.ql-page-title` and `.ql-page-subtitle` classes
9. The new `.ql-card`, `.ql-card-grid`, `.ql-featured-grid` classes for the landing page
10. The new `.ql-section-heading` class for the categorised grid section labels

A single block, ~120 lines of CSS, lives entirely in `nav.py` so it loads once per page render automatically.

### Sidebar text-only header

Replace this:

```python
st.sidebar.image(str(ASSETS / "logo.png"), width=180)
st.sidebar.title("FinBytes QuantLabs")
st.sidebar.markdown("**Built by** [Manisha](https://mish-codes.github.io/FinBytes/)")
```

With this:

```python
st.sidebar.markdown(
    '<div class="ql-sidebar-brand">'
    '<div class="ql-sidebar-title">QuantLab</div>'
    '<div class="ql-sidebar-byline">Built by '
    '<a href="https://mish-codes.github.io/FinBytes/">Manisha</a>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)
```

CSS for those classes added to the global block.

The logo image file (`dashboard/assets/logo.png`) stays in the repo for now (still used as page favicon via `st.set_page_config(page_icon=...)`) but is no longer rendered as content.

## Implementation order

Pass A first (one PR), Pass B second (separate PR), so the visual decisions can be validated on the landing page before propagating to 30 other pages.

**Pass A PR contents:**
1. Update `.streamlit/config.toml` palette
2. Expand `nav.py` global CSS (fonts, palette vars, sidebar polish, plus all the new component classes)
3. Replace sidebar header with text version in `nav.py`
4. Create `dashboard/lib/projects.py` with the project registry
5. Create `dashboard/lib/page_header.py` (used by Pass B but exists from Pass A so the helper is in place)
6. Rewrite `dashboard/app.py` with tabs + landing content

**Pass B PR contents:**
7. For each page in `dashboard/pages/*.py`: replace `st.title(...)` with `render_page_header(...)`, curate subtitle copy
8. Spot-check 3-4 representative pages in the browser

Both PRs target master via the working branch.

## Testing

No automated tests — pure visual changes, all manual verification. Manual checklist for Pass A:

- [ ] Landing page loads without errors
- [ ] Hero "QuantLab" appears in serif Fraunces, subtitle in sans Inter
- [ ] Welcome tab is the default; System Health is in the second tab
- [ ] System Health checks still work (data fetches, table rendering)
- [ ] Featured grid shows 6 cards with serif titles in amber
- [ ] Each categorised grid shows the right projects in the right order
- [ ] Capstones appear last in their category
- [ ] Card title links navigate to the correct sidebar page
- [ ] Sidebar shows "QuantLab" text title (no logo image)
- [ ] Hairline borders, hover states render
- [ ] Mobile (resize browser <768px) reflows to 1-column without breaking

Manual checklist for Pass B:

- [ ] Every page in `pages/` shows the new `render_page_header()` styled title
- [ ] Subtitles are sensible and don't repeat the title
- [ ] No page has a duplicate title (old `st.title` left behind)
- [ ] Existing functionality on each page still works (calculators compute, dataframes render)

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Google Fonts CDN blocked / slow | Fonts load with `font-display: swap`. Fallback fonts (Georgia, system-ui) render immediately. Acceptable degradation. |
| Streamlit class names change in a future version, breaking CSS selectors | Use semantic class names on our own elements (`.ql-*`) for as much as possible. Only target Streamlit internals where unavoidable (expanders). Document version assumption in `nav.py` comment. |
| Logo file path still referenced as `page_icon` | Keep `assets/logo.png` in the repo. Only its rendering as visible UI content is removed. |
| Pages migrating to `render_page_header` accidentally lose existing intro markdown | Migration is done one page at a time, with manual spot-check before commit. The helper only replaces the title call; subsequent `st.markdown(...)` blocks are untouched. |
| The new landing page slows app cold-start (font CDN fetch, more markdown) | Negligible. Streamlit caches per-session, fonts load once. |

## Open questions

None. All design decisions locked.

## Next step

Invoke the `superpowers:writing-plans` skill to break this spec into an implementation plan with task-by-task TDD-style checkpoints (manual-only for visual changes).
