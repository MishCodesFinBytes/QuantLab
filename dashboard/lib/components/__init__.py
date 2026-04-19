"""Custom Streamlit components for the QuantLab dashboard.

Everything under this package is a declare_component front-end — small
vanilla-JS/HTML bundles that keep a long-lived WebGL/DOM state across
Streamlit reruns instead of ``components.html(...)`` which reloads its
iframe every rerun.
"""
