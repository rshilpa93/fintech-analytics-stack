import streamlit as st

st.set_page_config(
    page_title="Fintech Analytics Stack",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Fintech Analytics Stack")
st.caption("Built with dbt + DuckDB + Streamlit + Claude API")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/1_📊_KPI_Dashboard.py", label="KPI Dashboard", icon="📊")
    st.caption("Monthly trends, customer engagement tiers, deposit vs outflow analysis")

with col2:
    st.page_link("pages/2_🤖_Ask_Your_Data.py", label="Ask Your Data", icon="🤖")
    st.caption("Type any business question in plain English and get instant SQL results")
