"""Etymology — interactive force-directed graph of English word roots."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
from tech_footer import render_tech_footer
import streamlit.components.v1 as components
from nav import render_sidebar

st.set_page_config(page_title="Etymology", page_icon="assets/logo.png", layout="wide")
render_sidebar()
st.title("Etymology")

st.markdown(
    "Word roots from Greek, Latin, and Proto-Indo-European — click a featured "
    "root or search for a word. The interactive graph is hosted on the FinBytes "
    "blog and embedded here."
)

components.iframe(
    "https://mish-codes.github.io/FinBytes/quant-lab/etymology/embed/",
    height=900,
    scrolling=True,
)

# -- Tech stack ---------------------------------------------------------------
render_tech_footer(["Jekyll", "D3.js", "vanilla JS", "YAML", "Streamlit components"])
