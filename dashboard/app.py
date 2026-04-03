import streamlit as st

st.set_page_config(
    page_title="FinBytes Labs",
    page_icon="📊",
    layout="wide",
)

st.sidebar.title("FinBytes Labs")
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

st.title("Welcome to FinBytes Labs")
st.markdown(
    "Interactive demos of quantitative finance projects. "
    "Select a project from the sidebar to get started."
)

st.markdown("### Available Projects")
st.markdown("- **Stock Risk Scanner** — Enter stock tickers, see risk metrics, AI narrative, and interactive charts")
