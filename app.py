import streamlit as st
import os
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# --- LangChain ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="AI SQL Analyst",
    page_icon="📊",
    layout="wide"
)

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("GOOGLE_API_KEY missing in .env")
    st.stop()

DB_URI = "sqlite:///Chinook_Sqlite.sqlite"

# ---------------- RESOURCES ----------------

@st.cache_resource
def get_resources():
    db = SQLDatabase.from_uri(DB_URI)
    engine = create_engine(DB_URI)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        max_output_tokens=2048
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True,
        agent_type="zero-shot-react-description"
    )

    schema = db.get_table_info()

    return db, engine, llm, agent, schema


db, engine, llm, agent_executor, DB_SCHEMA = get_resources()

# ---------------- SQL SAFETY ----------------

FORBIDDEN = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

def validate_sql(sql):
    upper = sql.upper()
    return not any(word in upper for word in FORBIDDEN)


# ---------------- SQL GENERATION CHAIN ----------------

SQL_PROMPT = """
You are a SQLite expert.

Return ONLY valid SQLite SQL.

Rules:
- No markdown
- No explanation
- No comments
- Only SELECT queries
- Use LIMIT when results may be large

Schema:
{schema}

Question:
{question}

SQL:
"""

prompt = ChatPromptTemplate.from_template(SQL_PROMPT)

sql_chain = (
    RunnablePassthrough.assign(schema=lambda _: DB_SCHEMA)
    | prompt
    | llm
    | StrOutputParser()
)

# ---------------- HELPERS ----------------

def clean_sql(sql):
    return (
        sql.replace("```sql", "")
        .replace("```", "")
        .strip()
    )


def run_sql_safe(sql):
    if not validate_sql(sql):
        raise ValueError("Unsafe SQL detected")

    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def auto_chart(df, question):
    numeric = df.select_dtypes(include="number").columns
    categorical = df.select_dtypes(exclude="number").columns

    if len(categorical) >= 1 and len(numeric) >= 1:
        return px.bar(
            df,
            x=categorical[0],
            y=numeric[0],
            title=question
        )

    if len(numeric) >= 2:
        return px.line(
            df,
            x=numeric[0],
            y=numeric[1],
            title=question
        )

    return None


# ---------------- UI ----------------

st.title("📊 AI Data Analyst")
st.caption("Ask questions → get SQL → get charts")

if "history" not in st.session_state:
    st.session_state.history = []

user_query = st.chat_input("Ask a data question...")

if user_query:
    st.chat_message("user").write(user_query)

    # -------- Agent Answer --------
    with st.chat_message("assistant"):
        st.subheader("🤖 Agent Answer")

        cb = StreamlitCallbackHandler(st.container())

        try:
            result = agent_executor.invoke(
                {"input": user_query},
                {"callbacks": [cb]}
            )
            st.write(result["output"])
        except Exception as e:
            st.error(f"Agent failed: {e}")

    # -------- Visualization --------

    viz_words = [
        "top", "trend", "compare", "chart",
        "graph", "distribution", "sales", "count"
    ]

    if any(w in user_query.lower() for w in viz_words):

        with st.status("Generating visualization...", expanded=True):

            try:
                raw_sql = sql_chain.invoke({"question": user_query})
                sql = clean_sql(raw_sql)

                st.code(sql, language="sql")

                df = run_sql_safe(sql)

                if df.empty:
                    st.warning("No data returned")
                else:
                    st.dataframe(df)

                    fig = auto_chart(df, user_query)

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Data not suitable for chart")

            except Exception as e:
                st.error(f"Visualization error: {e}")
