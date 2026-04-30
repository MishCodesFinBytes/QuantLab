"""Big O Notation — same problem, different complexities, on one chart."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
from nav import render_sidebar
from page_header import render_page_header
from bigo import (
    PROBLEMS,
    run_problem,
    build_complexity_chart,
    build_variant_card,
)

st.set_page_config(page_title="Big O Notation", page_icon="assets/logo.png", layout="wide")
render_sidebar()
render_page_header("Big O Notation", "Same problem, different complexities — see the gap")

# Problem selector
problem_keys = list(PROBLEMS.keys())
problem_labels = {k: PROBLEMS[k].label for k in problem_keys}

col_sel, col_run = st.columns([3, 1])
with col_sel:
    chosen_key = st.selectbox(
        "Problem",
        options=problem_keys,
        format_func=lambda k: problem_labels[k],
        key="bigo_problem_key",
    )
with col_run:
    st.write("")
    run_clicked = st.button(
        "\u25b6 Run benchmark",
        key="bigo_run_btn",
        width='stretch',
    )

problem = PROBLEMS[chosen_key]
st.caption(problem.description)

with st.expander("About this problem", expanded=False):
    st.markdown(problem.explainer)

cache_key = f"bigo_results_{chosen_key}"
if run_clicked:
    with st.spinner(f"Running all variants of {problem_labels[chosen_key]}..."):
        st.session_state[cache_key] = run_problem(problem)

result = st.session_state.get(cache_key)
if result is None:
    st.info("Click **Run benchmark** to start.")
else:
    st.plotly_chart(build_complexity_chart(result), width='stretch')

    st.markdown("#### Per-algorithm detail")
    for vr in result.variant_results:
        card = build_variant_card(vr)
        with st.expander(card["headline"]):
            # Correctness warnings for this variant
            bad = [
                (k, n) for (k, n), ok in result.correctness.items()
                if k == vr.variant.key and not ok
            ]
            if bad:
                st.warning(
                    f"\u26a0 Results disagreed with other variants at "
                    f"n={', '.join(str(n) for _, n in bad)}"
                )
            st.dataframe(card["rows"], width='stretch', hide_index=True)

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Python", "Plotly", "Streamlit"])
