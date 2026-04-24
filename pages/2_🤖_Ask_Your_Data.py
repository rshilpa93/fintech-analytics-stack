import streamlit as st
import duckdb
import anthropic
import pandas as pd
import re

# ── Config ──
st.set_page_config(
    page_title="Ask Your Fintech Data",
    page_icon="🤖",
    layout="wide"
)

DB_PATH = "fintech_analytics/fintech.duckdb"

# ── Schema context for the LLM ──
SCHEMA_CONTEXT = """
You are an expert analytics engineer. You have access to a fintech analytics database with these tables:

TABLE: main.customer_metrics
- customer_id (VARCHAR) - unique customer identifier
- full_name (VARCHAR) - customer full name
- plan_type (VARCHAR) - 'basic' or 'premium'
- state (VARCHAR) - Canadian province code (ON, BC, AB)
- signup_date (DATE) - when customer signed up
- total_transactions (INTEGER) - total number of completed transactions
- total_deposits (DECIMAL) - sum of all deposits in dollars
- total_outflows (DECIMAL) - sum of all withdrawals and purchases in dollars
- net_balance (DECIMAL) - total_deposits minus total_outflows
- first_transaction_date (DATE) - date of first transaction
- last_transaction_date (DATE) - date of last transaction
- active_months (INTEGER) - number of distinct months with activity
- engagement_tier (VARCHAR) - 'high', 'medium', or 'low' based on active_months

TABLE: main.monthly_summary
- transaction_month (DATE) - first day of the month
- active_customers (INTEGER) - distinct customers who transacted that month
- total_transactions (INTEGER) - total number of transactions
- total_deposits (DECIMAL) - total deposits in dollars
- total_outflows (DECIMAL) - total outflows in dollars
- avg_transaction_size (DECIMAL) - average transaction amount

TABLE: main.stg_transactions (raw transaction data)
- transaction_id (INTEGER)
- customer_id (VARCHAR)
- transaction_date (DATE)
- transaction_type (VARCHAR) - 'deposit', 'withdrawal', or 'purchase'
- amount (DECIMAL)
- product_type (VARCHAR) - 'savings' or 'checking'
- transaction_month (DATE)

TABLE: main.stg_customers (raw customer data)
- customer_id (VARCHAR)
- full_name (VARCHAR)
- signup_date (DATE)
- plan_type (VARCHAR) - 'basic' or 'premium'
- state (VARCHAR)

Rules:
- Always use fully qualified table names (main.table_name)
- Return only the SQL query, nothing else — no explanation, no markdown, no backticks
- Write clean, readable SQL with CTEs where helpful
- If the question cannot be answered with the available data, return: ERROR: <reason>
"""

def get_sql_from_question(question: str, client: anthropic.Anthropic) -> str:
    """Use Claude to convert a natural language question to SQL."""
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"{SCHEMA_CONTEXT}\n\nConvert this question to SQL:\n{question}"
            }
        ]
    )
    return message.content[0].text.strip()

def run_query(sql: str) -> pd.DataFrame:
    """Execute SQL against DuckDB and return a DataFrame."""
    con = duckdb.connect(DB_PATH, read_only=True)
    result = con.execute(sql).df()
    con.close()
    return result

def explain_result(question: str, sql: str, df: pd.DataFrame, client: anthropic.Anthropic) -> str:
    """Use Claude to explain the query result in plain English."""
    data_preview = df.to_string(index=False, max_rows=20)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""A user asked: "{question}"

The SQL query returned this data:
{data_preview}

Write a concise 2-3 sentence plain English summary of what the data shows. 
Be specific with numbers. Don't mention SQL or technical details."""
            }
        ]
    )
    return message.content[0].text.strip()

# ── UI ──
st.title("🤖 Ask Your Fintech Data")
st.caption("Natural language → SQL → Results · Powered by Claude + dbt + DuckDB")

st.divider()

# Initialize session state
if "question" not in st.session_state:
    st.session_state.question = ""

# API key input
with st.sidebar:
    st.header("⚙️ Setup")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.caption("Get your key at console.anthropic.com")
    st.divider()
    st.header("💡 Example Questions")
    st.caption("Select one to load it into the question box, then click Ask →")
    examples = [
        "— select an example —",
        "Who are the top 5 customers by net balance?",
        "What is the average deposit amount for premium vs basic customers?",
        "Which month had the most active customers?",
        "How many customers are in each engagement tier?",
        "What's the total deposits by province?",
        "Show me customers who haven't transacted since January 2024",
        "What percentage of customers are on the premium plan?",
        "Which customers have more outflows than deposits?",
    ]
    selected = st.selectbox("Examples", examples, label_visibility="collapsed")
    if selected != "— select an example —":
        st.session_state.question = selected

st.divider()

# Question input
question = st.text_input(
    "Ask a question about your data",
    value=st.session_state.question,
    placeholder="e.g. Who are the top 5 customers by net balance?",
)

col1, col2 = st.columns([1, 5])
with col1:
    run = st.button("Ask →", type="primary", use_container_width=True)

if run and question:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
        st.stop()

    client = anthropic.Anthropic(api_key=api_key)

    with st.spinner("Thinking..."):
        # Step 1: Generate SQL
        sql = get_sql_from_question(question, client)

        if sql.startswith("ERROR:"):
            st.error(sql)
            st.session_state.run_query = False
            st.stop()

        # Step 2: Run query
        try:
            df = run_query(sql)
        except Exception as e:
            st.error(f"Query failed: {e}")
            with st.expander("Generated SQL"):
                st.code(sql, language="sql")
            st.session_state.run_query = False
            st.stop()

        # Step 3: Explain result
        explanation = explain_result(question, sql, df, client)

    # Reset flag
    st.session_state.run_query = False

    # ── Display results ──
    st.success(f"✓ Found {len(df)} row{'s' if len(df) != 1 else ''}")

    # Plain English summary
    st.info(f"💬 {explanation}")

    # Data table
    st.subheader("Results")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # SQL expander
    with st.expander("View generated SQL"):
        st.code(sql, language="sql")

elif run and not question:
    st.warning("Please enter a question.")

# ── Footer ──
st.divider()
st.caption("Built with Claude API · dbt · DuckDB · Streamlit · [GitHub](https://github.com/rshilpa93/fintech-analytics-stack)")
