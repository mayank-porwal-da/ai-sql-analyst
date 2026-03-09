import time

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from app_core.charts import (
    generate_chat_chart,
    render_monthly_revenue_trend_chart,
    render_revenue_by_country_chart,
    render_revenue_by_genre_chart,
    render_store_kpis,
    render_top_customers_chart,
    render_top_selling_tracks_table,
)
from app_core.config import MODEL_OPTIONS
from app_core.database import get_database_overview, load_db_resources, run_sql
from app_core.llm import build_sql_chain, classify_question, generate_fixed_sql
from app_core.sql_utils import clean_sql

# Load environment variables from .env file (for GOOGLE_API_KEY)
load_dotenv()


# -----------------------------
# APP CONFIG
# -----------------------------

st.set_page_config(
    page_title="AI SQL Analyst",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI SQL Analyst")
st.caption("Ask questions → Generate SQL → Visualize results")

if "selected_model" not in st.session_state:
    st.session_state.selected_model = MODEL_OPTIONS[0]

if "history" not in st.session_state:
    st.session_state.history = []


# -----------------------------
# LOAD RESOURCES (CACHED)
# -----------------------------

db, engine, db_schema = load_db_resources()


def execute_sql_with_retries(model_name: str, schema: str, initial_sql: str, max_retries: int = 2):
    current_sql = initial_sql
    retries_used = 0

    while True:
        try:
            df = run_sql(engine, current_sql)
            return df, current_sql, retries_used
        except Exception as exc:
            if retries_used >= max_retries:
                raise exc
            retries_used += 1
            current_sql = generate_fixed_sql(
                model_name=model_name,
                db_schema=schema,
                sql_query=current_sql,
                error_message=str(exc),
            )


# -----------------------------
# APP SECTIONS
# -----------------------------

store_tab, chat_tab, dashboard_tab = st.tabs(
    ["🏬 Store Dashboard", "💬 Chatbot", "🗄️ Database Dashboard"]
)


# -----------------------------
# STORE DASHBOARD TAB
# -----------------------------

with store_tab:
    st.subheader("Store Dashboard")
    st.caption("Business intelligence dashboard powered by SQL + pandas (no LLM).")

    st.markdown("### Key Performance Indicators")
    render_store_kpis(engine)

    st.markdown("### Sales Distribution")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        render_revenue_by_country_chart(engine)
    with c2:
        render_top_customers_chart(engine)

    st.markdown("### Product and Trend Insights")
    c3, c4 = st.columns(2, gap="large")
    with c3:
        render_revenue_by_genre_chart(engine)
    with c4:
        render_monthly_revenue_trend_chart(engine)

    st.markdown("### Top Selling Tracks")
    render_top_selling_tracks_table(engine)


# -----------------------------
# CHAT TAB
# -----------------------------

with chat_tab:
    with st.container():
        st.markdown("### ⚙️ Chatbot Settings")
        settings_col, action_col = st.columns([3, 1])
        with settings_col:
            selected_model = st.selectbox(
                "Choose AI Model",
                MODEL_OPTIONS,
                index=MODEL_OPTIONS.index(st.session_state.selected_model),
                key="selected_model",
                help="Llama and Qwen run locally. Gemini requires an internet connection and the API key in your .env file.",
            )
            if "gemini" not in selected_model:
                st.caption("Ensure the selected model is pulled in your local Ollama instance.")
        with action_col:
            st.write("")
            st.write("")
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.history = []
                st.rerun()

    st.divider()

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                if "content" in msg:
                    st.write(msg["content"])
                if "sql" in msg:
                    with st.expander("View Generated SQL"):
                        st.code(msg["sql"], language="sql")
                if "error" in msg:
                    st.error(msg["error"])
                if "df" in msg and not msg["df"].empty:
                    st.dataframe(msg["df"], use_container_width=True)
                if "chart" in msg and msg["chart"]:
                    st.plotly_chart(msg["chart"], use_container_width=True)
                if "time" in msg:
                    st.caption(f"⏱️ **Completed in {msg['time']:.2f} seconds**")

    user_query = st.chat_input("Ask a question about the database...")

    if user_query:
        st.session_state.history.append({"role": "user", "content": user_query})

        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            try:
                start_time = time.time()
                st.caption("🧠 Processing Request...")

                question_type = classify_question(selected_model, user_query)
                if question_type == "NOT_DB_QUERY":
                    guidance = (
                        "This assistant is designed to answer questions related to the Chinook database. "
                        "Please ask questions about customers, tracks, artists, invoices, or sales."
                    )
                    st.info(guidance)
                    st.session_state.history.append({"role": "assistant", "content": guidance})
                    st.stop()

                sql_chain = build_sql_chain(selected_model, db_schema)
                sql_placeholder = st.empty()
                raw_sql = ""

                for chunk in sql_chain.stream({"question": user_query}):
                    raw_sql += chunk
                    sql_placeholder.markdown(f"```text\n{raw_sql} \n```")

                sql = clean_sql(raw_sql)
                sql_placeholder.empty()

                if sql.upper().startswith("UNSAFE:"):
                    st.error("🛑 Security Alert: Destructive query blocked.")
                    st.info(f"💡 {sql[7:].strip()}")
                    st.session_state.history.append(
                        {
                            "role": "assistant",
                            "error": sql,
                            "df": pd.DataFrame(),
                            "chart": None,
                        }
                    )
                    st.stop()

                if sql.upper().startswith("OUT_OF_SCOPE:"):
                    st.warning("⚠️ Out of Context")
                    st.info(f"💡 {sql[13:].strip()}")
                    available_tables = ", ".join(db.get_usable_table_names())
                    st.caption(f"Available tables: {available_tables}")

                    st.session_state.history.append(
                        {
                            "role": "assistant",
                            "error": sql,
                            "df": pd.DataFrame(),
                            "chart": None,
                        }
                    )
                    st.stop()

                with st.spinner("Executing Query against Database..."):
                    df, final_sql, retries_used = execute_sql_with_retries(
                        model_name=selected_model,
                        schema=db_schema,
                        initial_sql=sql,
                        max_retries=2,
                    )

                with st.expander("View Generated SQL", expanded=True):
                    st.code(final_sql, language="sql")

                if retries_used > 0:
                    st.info(f"Auto-corrected SQL and retried {retries_used} time(s).")

                elapsed_time = time.time() - start_time

                if df.empty:
                    empty_msg = (
                        "No results were found for this query.\n"
                        "Try modifying your question or ask about available customers, tracks, artists, invoices, or sales."
                    )
                    st.info(empty_msg)
                    st.caption(f"⏱️ **Completed in {elapsed_time:.2f} seconds**")
                    st.session_state.history.append(
                        {
                            "role": "assistant",
                            "content": empty_msg,
                            "sql": final_sql,
                            "df": df,
                            "chart": None,
                            "time": elapsed_time,
                        }
                    )
                else:
                    st.subheader("Query Result")
                    st.dataframe(df, use_container_width=True)

                    chart = generate_chat_chart(df, user_query)
                    if chart:
                        st.subheader("Visualization")
                        st.plotly_chart(chart, use_container_width=True)
                    else:
                        st.info("Data not suitable for an automatic chart.")

                    st.caption(f"⏱️ **Completed in {elapsed_time:.2f} seconds**")

                    st.session_state.history.append(
                        {
                            "role": "assistant",
                            "sql": final_sql,
                            "df": df,
                            "chart": chart,
                            "time": elapsed_time,
                        }
                    )

            except ValueError as ve:
                st.error(f"⚠️ {ve}")
                st.session_state.history.append({"role": "assistant", "error": str(ve)})

            except Exception as e:
                st.error("⚠️ The AI generated an invalid SQL query. Try rephrasing your question.")
                with st.expander("View Error Details"):
                    st.write(e)
                st.session_state.history.append({"role": "assistant", "error": "Invalid SQL generated."})


# -----------------------------
# DATABASE DASHBOARD TAB
# -----------------------------

with dashboard_tab:
    st.subheader("Database Dashboard")
    st.caption("Static database overview (no LLM calls).")

    table_overview_df, columns_df, relationships_df, summary_stats = get_database_overview(engine)

    total_tables = int(table_overview_df["table_name"].nunique()) if not table_overview_df.empty else 0
    total_rows = int(table_overview_df["row_count"].sum()) if not table_overview_df.empty else 0
    total_relationships = int(len(relationships_df))

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Tables", f"{total_tables:,}")
    m2.metric("Total Rows (All Tables)", f"{total_rows:,}")
    m3.metric("Foreign Key Relationships", f"{total_relationships:,}")

    if summary_stats:
        stat_cols = st.columns(len(summary_stats))
        for i, (label, value) in enumerate(summary_stats.items()):
            stat_cols[i].metric(label, value)

    st.markdown("### Tables and Row Counts")
    st.dataframe(
        table_overview_df.rename(
            columns={
                "table_name": "Table",
                "row_count": "Rows",
                "column_count": "Columns",
            }
        ),
        use_container_width=True,
    )

    if not table_overview_df.empty:
        top_n = min(10, len(table_overview_df))
        chart_df = table_overview_df.head(top_n).copy()
        fig = px.bar(
            chart_df,
            x="table_name",
            y="row_count",
            title=f"Top {top_n} Tables by Row Count",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Key Relationships")
    if relationships_df.empty:
        st.info("No foreign key relationships found in this database.")
    else:
        st.dataframe(
            relationships_df.rename(
                columns={
                    "from_table": "From Table",
                    "from_columns": "From Columns",
                    "to_table": "To Table",
                    "to_columns": "To Columns",
                }
            ),
            use_container_width=True,
        )

    st.markdown("### Table Structure")
    if columns_df.empty:
        st.info("No column metadata found.")
    else:
        selected_table = st.selectbox(
            "Inspect table columns",
            options=table_overview_df["table_name"].tolist() if not table_overview_df.empty else [],
        )
        if selected_table:
            table_cols = columns_df[columns_df["table_name"] == selected_table].copy()
            st.dataframe(
                table_cols.rename(
                    columns={
                        "column_name": "Column",
                        "type": "Type",
                        "nullable": "Nullable",
                        "is_primary_key": "Primary Key",
                    }
                )[["Column", "Type", "Nullable", "Primary Key"]],
                use_container_width=True,
            )
