from pathlib import Path
import streamlit as st

HERE = Path(__file__).parent

st.set_page_config(
    page_title="FinBytes QuantLabs",
    page_icon="📊",
    layout="wide",
)

# Sidebar
st.sidebar.image(str(HERE / "assets" / "logo.png"), width=180)
st.sidebar.title("FinBytes QuantLabs")
st.sidebar.markdown("**Built by** [Manisha](https://mishcodesfinbytes.github.io/FinBytes/)")
st.sidebar.markdown("---")

st.sidebar.markdown("### Projects")
st.sidebar.markdown("- [Stock Risk Scanner](Stock_Risk_Scanner)")
st.sidebar.markdown("- *More coming soon...*")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Built with:** Python, FastAPI, SQLAlchemy, "
    "Docker, Claude API, Streamlit"
)
st.sidebar.markdown(
    "[GitHub Repo](https://github.com/MishCodesFinBytes/QuantLab) · "
    "[Blog](https://mishcodesfinbytes.github.io/FinBytes/quant-lab/stock-risk-scanner/) · "
    "[System Health](System_Health)"
)

# Main landing page
st.title("FinBytes QuantLabs")
st.markdown(
    "Interactive demos of quantitative finance projects. "
    "Select a project from the sidebar to get started."
)

st.markdown("---")

st.markdown("### Available Projects")

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
        **📊 Stock Risk Scanner**

        Enter stock tickers and portfolio weights to get:
        - 5 risk metrics (VaR, CVaR, drawdown, volatility, Sharpe)
        - AI-powered risk narrative
        - Interactive Plotly charts

        [Launch →](Stock_Risk_Scanner)
        """
    )
with col2:
    st.markdown(
        """
        **🔧 More Projects**

        Future projects will appear here as new pages.
        The dashboard is built as a multi-page Streamlit app —
        each project is a self-contained page.
        """
    )
