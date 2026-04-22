import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# ── Config ──

# ── Connect to DuckDB ──
DB_PATH = "fintech_analytics/fintech.duckdb"
con = duckdb.connect(DB_PATH, read_only=True)

# ── Load data ──
customer_metrics = con.execute("SELECT * FROM main.customer_metrics").df()
monthly_summary  = con.execute("SELECT * FROM main.monthly_summary").df()

# ── Header ──
st.title("📊 Fintech Analytics Dashboard")
st.caption("Built with dbt + DuckDB + Streamlit · [GitHub](https://github.com/rshilpa93/fintech-analytics-stack)")

st.divider()

# ── KPI Row ──
col1, col2, col3, col4 = st.columns(4)

total_customers    = len(customer_metrics)
total_deposits     = customer_metrics["total_deposits"].sum()
avg_net_balance    = customer_metrics["net_balance"].mean()
high_engagement    = len(customer_metrics[customer_metrics["engagement_tier"] == "high"])

col1.metric("Total Customers",     total_customers)
col2.metric("Total Deposits",      f"${total_deposits:,.0f}")
col3.metric("Avg Net Balance",     f"${avg_net_balance:,.0f}")
col4.metric("High Engagement",     f"{high_engagement} customers")

st.divider()

# ── Row 2: Monthly trends + Engagement tier ──
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Monthly Deposits vs Outflows")
    monthly_summary["transaction_month"] = pd.to_datetime(monthly_summary["transaction_month"])
    monthly_long = monthly_summary.melt(
        id_vars="transaction_month",
        value_vars=["total_deposits", "total_outflows"],
        var_name="type", value_name="amount"
    )
    monthly_long["type"] = monthly_long["type"].map({
        "total_deposits": "Deposits",
        "total_outflows": "Outflows"
    })
    fig1 = px.bar(
        monthly_long,
        x="transaction_month", y="amount", color="type",
        barmode="group",
        color_discrete_map={"Deposits": "#1a4fba", "Outflows": "#e2e8f0"},
        labels={"transaction_month": "Month", "amount": "Amount ($)", "type": ""}
    )
    fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Customer Engagement Tiers")
    tier_counts = customer_metrics["engagement_tier"].value_counts().reset_index()
    tier_counts.columns = ["tier", "count"]
    fig2 = px.pie(
        tier_counts, names="tier", values="count",
        color="tier",
        color_discrete_map={"high": "#1a4fba", "medium": "#60a5fa", "low": "#e2e8f0"},
        hole=0.4
    )
    fig2.update_layout(paper_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Row 3: Monthly active customers + Customer table ──
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("Monthly Active Customers")
    fig3 = px.line(
        monthly_summary,
        x="transaction_month", y="active_customers",
        markers=True,
        color_discrete_sequence=["#1a4fba"],
        labels={"transaction_month": "Month", "active_customers": "Active Customers"}
    )
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig3, use_container_width=True)

with col_right2:
    st.subheader("Top Customers by Net Balance")
    top_customers = customer_metrics[["full_name", "plan_type", "total_deposits", "net_balance", "engagement_tier"]] \
        .sort_values("net_balance", ascending=False) \
        .head(8) \
        .rename(columns={
            "full_name": "Name",
            "plan_type": "Plan",
            "total_deposits": "Deposits ($)",
            "net_balance": "Net Balance ($)",
            "engagement_tier": "Tier"
        })
    top_customers["Deposits ($)"]    = top_customers["Deposits ($)"].map("${:,.0f}".format)
    top_customers["Net Balance ($)"] = top_customers["Net Balance ($)"].map("${:,.0f}".format)
    st.dataframe(top_customers, use_container_width=True, hide_index=True)

st.divider()
st.caption("Data: Synthetic fintech dataset · Models: dbt Core · Warehouse: DuckDB")
