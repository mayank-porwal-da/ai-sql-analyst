import os

import streamlit as st

try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models import ChatOllama

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app_core.config import SQL_PROMPT
from app_core.sql_utils import clean_sql

QUESTION_CLASSIFIER_PROMPT = """
You are a strict classifier for a SQLite analytics assistant.

Database domain topics include:
- customers, invoices, sales, tracks, albums, artists, genres
- countries, billing, payments, revenue

Task:
Classify the user question into exactly one label:
- DB_QUERY: if the question can be answered using the database topics above
- NOT_DB_QUERY: if unrelated to the database or general chit-chat

Return only one token: DB_QUERY or NOT_DB_QUERY.

Question:
{question}
"""

SQL_FIX_PROMPT = """
The following SQL query failed.

Database Error:
{error_message}

SQL Query:
{sql_query}

Fix the SQL query using the database schema below.
Return ONLY the corrected SQLite SQL query.

Database Schema:
{schema}
"""


@st.cache_resource
def load_llm(model_name: str):
    if "gemini" in model_name.lower():
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("⚠️ GOOGLE_API_KEY not found in .env file.")
            st.stop()
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
        )

    return ChatOllama(
        model=model_name,
        base_url="http://localhost:11434",
        temperature=0,
    )


def build_sql_chain(model_name: str, db_schema: str):
    llm = load_llm(model_name)
    prompt = ChatPromptTemplate.from_template(SQL_PROMPT)
    return (
        RunnablePassthrough.assign(schema=lambda _: db_schema)
        | prompt
        | llm
        | StrOutputParser()
    )


def classify_question(model_name: str, question: str) -> str:
    llm = load_llm(model_name)
    prompt = ChatPromptTemplate.from_template(QUESTION_CLASSIFIER_PROMPT)
    chain = prompt | llm | StrOutputParser()
    label = chain.invoke({"question": question}).strip().upper()
    if label == "DB_QUERY":
        return "DB_QUERY"
    if label == "NOT_DB_QUERY":
        return "NOT_DB_QUERY"
    if "NOT_DB_QUERY" in label:
        return "NOT_DB_QUERY"
    return "DB_QUERY"


def generate_fixed_sql(model_name: str, db_schema: str, sql_query: str, error_message: str) -> str:
    llm = load_llm(model_name)
    prompt = ChatPromptTemplate.from_template(SQL_FIX_PROMPT)
    chain = prompt | llm | StrOutputParser()
    fixed_sql = chain.invoke(
        {
            "schema": db_schema,
            "sql_query": sql_query,
            "error_message": error_message,
        }
    )
    return clean_sql(fixed_sql)
