# Fintech Analytics Stack

🚀 **[View Live Dashboard](https://fintech-analytics-dashboard.streamlit.app/)** | Built with dbt + DuckDB + Streamlit

A production-style analytics engineering project built with dbt + DuckDB, modeled after real fintech data infrastructure.

## What This Demonstrates
- Multi-layer dbt modeling (staging → marts)
- Fintech KPI calculations: deposits, outflows, net balance, engagement tiers
- Clean data transformation with business logic
- dbt best practices: ref(), materialization strategies, project structure

## Project Structure
```
models/
├── staging/
│   ├── stg_transactions.sql   # Cleaned transactions, completed only
│   └── stg_customers.sql      # Cleaned customer profiles
└── marts/
    ├── customer_metrics.sql   # Per-customer KPIs + engagement tier
    └── monthly_summary.sql    # Monthly active users, deposits, outflows
```

## Data Model
**Seeds (raw data)**
- `raw_transactions` — 20 transactions across 8 customers
- `raw_customers` — Customer profiles with plan type and province

**Staging layer** — cleaned, typed, filtered (completed transactions only)

**Marts layer** — business-ready tables:
- `customer_metrics`: total deposits, outflows, net balance, engagement tier (high/medium/low)
- `monthly_summary`: monthly active customers, transaction volume, avg transaction size

## How to Run
```bash
# Install dependencies
pip3 install dbt-duckdb

# Load seed data and run models
dbt seed && dbt run

# Run tests
dbt test
```

## Tech Stack
- **Transformation:** dbt Core 1.10
- **Warehouse:** DuckDB
- **Language:** SQL
- **Data:** Synthetic fintech transactions dataset
