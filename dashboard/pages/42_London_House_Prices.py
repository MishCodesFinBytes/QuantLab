"""London House Prices — postcode growth, comparison, and brand effect analysis."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from house_prices import (
    load_ppd,
    load_geojson,
    aggregate_by_district_year,
    get_all_districts_summary,
    compute_growth,
    query_brand_locations,
    assign_brand_districts,
)
from nav import render_sidebar
from test_tab import render_test_tab

st.set_page_config(page_title="London House Prices", page_icon="assets/logo.png", layout="wide")
render_sidebar()
st.title("London House Prices")

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
[data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

tab_growth, tab_compare, tab_brand, tab_tests = st.tabs(
    ["Postcode Growth", "Compare Postcodes", "Brand Effect", "Tests"]
)


@st.cache_data(show_spinner="Loading London house price data...")
def get_ppd():
    return load_ppd()


@st.cache_data(show_spinner="Loading map boundaries...")
def get_geojson():
    return load_geojson()


ppd = get_ppd()
geojson = get_geojson()
all_districts = sorted(ppd["postcode_district"].unique())

with tab_growth:
    with st.expander("How it works"):
        st.markdown("""
        - **Data source:** HM Land Registry Price Paid Data (2015-2024) — every residential property sale in London
        - **Postcode district:** the first part of a UK postcode (e.g., SW11, E14, N1)
        - **Map:** choropleth coloured by average price in the latest year
        - **Chart:** average price per year for the selected district
        """)

    col1, col2 = st.columns([1, 2])
    with col1:
        district = st.selectbox("Postcode District", all_districts, index=all_districts.index("SW11") if "SW11" in all_districts else 0, key="growth_district")
        year_range = st.slider("Year Range", 2015, 2024, (2015, 2024), key="growth_years")

    filtered = ppd[(ppd["date"].dt.year >= year_range[0]) & (ppd["date"].dt.year <= year_range[1])]
    agg = aggregate_by_district_year(filtered, district)
    summary = get_all_districts_summary(filtered)
    growth = compute_growth(filtered, district)

    with col2:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg Price", f"\u00a3{growth['end_price'] / 1000:.0f}k")
        c2.metric("Growth", f"{growth['growth_pct']}%")
        c3.metric("Peak Year", str(growth["peak_year"]))
        c4.metric("Transactions", f"{agg['count'].sum():,}" if len(agg) > 0 else "0")

    map_col, chart_col = st.columns([1, 1])

    with map_col:
        fig_map = px.choropleth_mapbox(
            summary,
            geojson=geojson,
            locations="postcode_district",
            featureidkey="properties.name",
            color="avg_price",
            color_continuous_scale="YlOrRd",
            mapbox_style="carto-positron",
            center={"lat": 51.5, "lon": -0.1},
            zoom=9,
            opacity=0.7,
            labels={"avg_price": "Avg Price"},
            title="Average Price by District",
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=450)
        st.plotly_chart(fig_map, use_container_width=True)

    with chart_col:
        if not agg.empty:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=agg["year"], y=agg["avg_price"],
                mode="lines+markers", name=district,
                line=dict(color="#2a7ae2", width=3),
            ))
            fig_line.update_layout(
                title=f"{district} — Average House Price",
                xaxis_title="Year", yaxis_title="Price (\u00a3)",
                height=450,
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info(f"No data found for {district}.")

with tab_compare:
    with st.expander("How it works"):
        st.markdown("""
        - Pick two postcode districts and a year range
        - Side-by-side line chart shows price trends for both
        - Metrics compare growth and average prices
        """)

    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        dist_a = st.selectbox("District A", all_districts, index=all_districts.index("SW11") if "SW11" in all_districts else 0, key="cmp_a")
    with cc2:
        dist_b = st.selectbox("District B", all_districts, index=all_districts.index("E14") if "E14" in all_districts else 1, key="cmp_b")
    with cc3:
        cmp_years = st.slider("Year Range", 2015, 2024, (2015, 2024), key="cmp_years")

    cmp_filtered = ppd[(ppd["date"].dt.year >= cmp_years[0]) & (ppd["date"].dt.year <= cmp_years[1])]
    agg_a = aggregate_by_district_year(cmp_filtered, dist_a)
    agg_b = aggregate_by_district_year(cmp_filtered, dist_b)
    growth_a = compute_growth(cmp_filtered, dist_a)
    growth_b = compute_growth(cmp_filtered, dist_b)

    mc1, mc2 = st.columns(2)
    with mc1:
        st.markdown(f"**{dist_a}**")
        st.metric("Avg Price", f"\u00a3{growth_a['end_price'] / 1000:.0f}k")
        st.metric("Growth", f"{growth_a['growth_pct']}%")
    with mc2:
        st.markdown(f"**{dist_b}**")
        st.metric("Avg Price", f"\u00a3{growth_b['end_price'] / 1000:.0f}k")
        st.metric("Growth", f"{growth_b['growth_pct']}%")

    fig_cmp = go.Figure()
    if not agg_a.empty:
        fig_cmp.add_trace(go.Scatter(x=agg_a["year"], y=agg_a["avg_price"], mode="lines+markers", name=dist_a, line=dict(color="#2a7ae2", width=3)))
    if not agg_b.empty:
        fig_cmp.add_trace(go.Scatter(x=agg_b["year"], y=agg_b["avg_price"], mode="lines+markers", name=dist_b, line=dict(color="#e24a4a", width=3)))
    fig_cmp.update_layout(title=f"{dist_a} vs {dist_b} — Average House Price", xaxis_title="Year", yaxis_title="Price (\u00a3)", height=450)
    st.plotly_chart(fig_cmp, use_container_width=True)

with tab_brand:
    with st.expander("How it works"):
        st.markdown("""
        - Enter a brand name (e.g., Waitrose, Pret, Costa, Greggs)
        - Queries OpenStreetMap for that brand's locations in London
        - Finds which postcode districts have that brand nearby
        - Compares average house price growth in districts **with** vs **without** the brand
        - The classic "Waitrose effect" analysis
        """)

    brand = st.text_input("Brand Name", value="Waitrose", key="brand_input")

    if brand:
        @st.cache_data(show_spinner=f"Finding {brand} locations in London...")
        def get_brand_locs(b):
            return query_brand_locations(b)

        @st.cache_data(show_spinner="Matching to postcode districts...")
        def get_brand_districts(b, _geojson):
            locs = get_brand_locs(b)
            districts = assign_brand_districts(locs, _geojson)
            return locs, districts

        try:
            locs, brand_districts = get_brand_districts(brand, geojson)
        except Exception as e:
            st.error(f"Could not fetch {brand} locations: {e}")
            locs, brand_districts = [], set()

        if not locs:
            st.warning(f"No '{brand}' locations found in London on OpenStreetMap.")
        else:
            st.success(f"Found {len(locs)} {brand} locations across {len(brand_districts)} postcode districts.")

            summary_all = get_all_districts_summary(ppd)
            summary_all["has_brand"] = summary_all["postcode_district"].isin(brand_districts)

            near = summary_all[summary_all["has_brand"]]
            far = summary_all[~summary_all["has_brand"]]
            avg_near = near["avg_price"].mean() if len(near) > 0 else 0
            avg_far = far["avg_price"].mean() if len(far) > 0 else 0

            bc1, bc2, bc3 = st.columns(3)
            bc1.metric(f"Near {brand}", f"\u00a3{avg_near / 1000:.0f}k")
            bc2.metric(f"Away from {brand}", f"\u00a3{avg_far / 1000:.0f}k")
            diff_pct = ((avg_near - avg_far) / avg_far * 100) if avg_far > 0 else 0
            bc3.metric("Premium", f"{diff_pct:+.1f}%")

            fig_brand = px.choropleth_mapbox(
                summary_all,
                geojson=geojson,
                locations="postcode_district",
                featureidkey="properties.name",
                color="has_brand",
                color_discrete_map={True: "#2ea043", False: "#ddd"},
                mapbox_style="carto-positron",
                center={"lat": 51.5, "lon": -0.1},
                zoom=9,
                opacity=0.7,
                labels={"has_brand": f"Has {brand}"},
                title=f"Postcode Districts with {brand}",
            )

            if locs:
                loc_df = pd.DataFrame(locs)
                fig_brand.add_trace(go.Scattermapbox(
                    lat=loc_df["lat"], lon=loc_df["lon"],
                    mode="markers",
                    marker=dict(size=8, color="#e24a4a"),
                    name=f"{brand} locations",
                    text=loc_df["name"],
                ))

            fig_brand.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=500)
            st.plotly_chart(fig_brand, use_container_width=True)

            fig_bar = go.Figure(data=[
                go.Bar(name=f"Near {brand}", x=["Average Price"], y=[avg_near], marker_color="#2ea043"),
                go.Bar(name=f"Away from {brand}", x=["Average Price"], y=[avg_far], marker_color="#aaa"),
            ])
            fig_bar.update_layout(title=f"The {brand} Effect", yaxis_title="Average Price (\u00a3)", barmode="group", height=350)
            st.plotly_chart(fig_bar, use_container_width=True)

with tab_tests:
    render_test_tab("test_london_house_prices.py")
