from pathlib import Path
import streamlit as st

HERE = Path(__file__).parent

st.set_page_config(
    page_title="FinBytes QuantLabs",
    page_icon="📊",
    layout="wide",
)

# Sidebar with logo
st.sidebar.image(str(HERE / "assets" / "logo.png"), width=180)
st.sidebar.title("FinBytes QuantLabs")
st.sidebar.markdown("**Built by** [Manisha](https://mishcodesfinbytes.github.io/FinBytes/)")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Built with:** Python, FastAPI, SQLAlchemy, "
    "Docker, Claude API, Streamlit"
)
st.sidebar.markdown(
    "[GitHub Repo](https://github.com/MishCodesFinBytes/QuantLab) · "
    "[Blog Post](https://mishcodesfinbytes.github.io/FinBytes/quant-lab/stock-risk-scanner/)"
)

# Main landing page
st.title("Welcome to FinBytes QuantLabs")
st.markdown(
    "Interactive demos of quantitative finance projects. "
    "Select a project from the sidebar to get started."
)

st.markdown("### Available Projects")
st.markdown("- **Stock Risk Scanner** — Enter stock tickers, see risk metrics, AI narrative, and interactive charts")
