import pandas as pd
import streamlit as st
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, inspect, text

from app_core.config import DB_PATH, DB_URI
from app_core.sql_utils import validate_sql


@st.cache_resource
def load_db_resources():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at: {DB_PATH}")

    db = SQLDatabase.from_uri(DB_URI)
    engine = create_engine(DB_URI)
    schema = db.get_table_info()
    return db, engine, schema


def run_sql(engine, sql: str) -> pd.DataFrame:
    if not validate_sql(sql):
        raise ValueError("Unsafe SQL detected or query was not a SELECT statement.")
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def quote_identifier(identifier: str) -> str:
    escaped = identifier.replace('"', '""')
    return f'"{escaped}"'


@st.cache_data
def get_store_kpis(_engine) -> dict:
    sql = text(
        """
        SELECT
            COALESCE(SUM(i.Total), 0) AS total_revenue,
            COUNT(i.InvoiceId) AS total_invoices,
            COUNT(DISTINCT c.CustomerId) AS total_customers,
            COALESCE(AVG(i.Total), 0) AS avg_order_value
        FROM Invoice i
        JOIN Customer c ON i.CustomerId = c.CustomerId
        """
    )
    with _engine.connect() as conn:
        row = pd.read_sql(sql, conn).iloc[0]
    return {
        "total_revenue": float(row["total_revenue"]),
        "total_invoices": int(row["total_invoices"]),
        "total_customers": int(row["total_customers"]),
        "avg_order_value": float(row["avg_order_value"]),
    }


@st.cache_data
def get_revenue_by_country(_engine) -> pd.DataFrame:
    sql = text(
        """
        SELECT
            c.Country AS country,
            SUM(i.Total) AS revenue
        FROM Invoice i
        JOIN Customer c ON i.CustomerId = c.CustomerId
        GROUP BY c.Country
        ORDER BY revenue DESC
        """
    )
    with _engine.connect() as conn:
        return pd.read_sql(sql, conn)


@st.cache_data
def get_top_customers_by_revenue(_engine, limit: int = 10) -> pd.DataFrame:
    sql = text(
        """
        SELECT
            c.CustomerId,
            c.FirstName || ' ' || c.LastName AS customer_name,
            c.Country AS country,
            SUM(il.UnitPrice * il.Quantity) AS revenue
        FROM Customer c
        JOIN Invoice i ON c.CustomerId = i.CustomerId
        JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
        GROUP BY c.CustomerId, c.FirstName, c.LastName, c.Country
        ORDER BY revenue DESC
        LIMIT :limit_value
        """
    )
    with _engine.connect() as conn:
        return pd.read_sql(sql, conn, params={"limit_value": limit})


@st.cache_data
def get_revenue_by_genre(_engine) -> pd.DataFrame:
    sql = text(
        """
        SELECT
            g.Name AS genre,
            SUM(il.UnitPrice * il.Quantity) AS revenue
        FROM Genre g
        JOIN Track t ON g.GenreId = t.GenreId
        JOIN InvoiceLine il ON t.TrackId = il.TrackId
        JOIN Invoice i ON il.InvoiceId = i.InvoiceId
        GROUP BY g.GenreId, g.Name
        ORDER BY revenue DESC
        """
    )
    with _engine.connect() as conn:
        return pd.read_sql(sql, conn)


@st.cache_data
def get_monthly_revenue_trend(_engine) -> pd.DataFrame:
    sql = text(
        """
        SELECT
            strftime('%Y-%m', i.InvoiceDate) AS month,
            SUM(i.Total) AS revenue
        FROM Invoice i
        GROUP BY strftime('%Y-%m', i.InvoiceDate)
        ORDER BY month
        """
    )
    with _engine.connect() as conn:
        df = pd.read_sql(sql, conn)
    df["month"] = pd.to_datetime(df["month"] + "-01")
    return df


@st.cache_data
def get_top_selling_tracks(_engine, limit: int = 15) -> pd.DataFrame:
    sql = text(
        """
        SELECT
            t.Name AS track_name,
            ar.Name AS artist,
            al.Title AS album,
            SUM(il.UnitPrice * il.Quantity) AS total_sales
        FROM InvoiceLine il
        JOIN Track t ON il.TrackId = t.TrackId
        JOIN Album al ON t.AlbumId = al.AlbumId
        JOIN Artist ar ON al.ArtistId = ar.ArtistId
        GROUP BY t.TrackId, t.Name, ar.Name, al.Title
        ORDER BY total_sales DESC
        LIMIT :limit_value
        """
    )
    with _engine.connect() as conn:
        return pd.read_sql(sql, conn, params={"limit_value": limit})


@st.cache_data
def get_database_overview(_engine):
    inspector = inspect(_engine)
    tables = inspector.get_table_names()

    table_rows = []
    table_columns = []
    relationships = []

    with _engine.connect() as conn:
        for table in tables:
            safe_table = quote_identifier(table)
            row_count_sql = text(f"SELECT COUNT(*) AS row_count FROM {safe_table}")
            row_count = int(pd.read_sql(row_count_sql, conn).iloc[0]["row_count"])

            columns = inspector.get_columns(table)
            column_count = len(columns)
            pk_cols = set((inspector.get_pk_constraint(table) or {}).get("constrained_columns", []) or [])

            table_rows.append(
                {
                    "table_name": table,
                    "row_count": row_count,
                    "column_count": column_count,
                }
            )

            for col in columns:
                table_columns.append(
                    {
                        "table_name": table,
                        "column_name": col["name"],
                        "type": str(col.get("type", "")),
                        "nullable": col.get("nullable", True),
                        "is_primary_key": col["name"] in pk_cols,
                    }
                )

            for fk in inspector.get_foreign_keys(table):
                relationships.append(
                    {
                        "from_table": table,
                        "from_columns": ", ".join(fk.get("constrained_columns", [])),
                        "to_table": fk.get("referred_table", ""),
                        "to_columns": ", ".join(fk.get("referred_columns", [])),
                    }
                )

        summary_stats = {}
        table_set = set(tables)

        if {"Invoice", "InvoiceLine"}.issubset(table_set):
            revenue_sql = text(
                """
                SELECT
                    COALESCE(SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity), 0) AS total_revenue
                FROM InvoiceLine
                """
            )
            total_revenue = float(pd.read_sql(revenue_sql, conn).iloc[0]["total_revenue"])
            summary_stats["Estimated Revenue"] = f"${total_revenue:,.2f}"

        if "Customer" in table_set:
            customer_sql = text("SELECT COUNT(*) AS customer_count FROM Customer")
            customer_count = int(pd.read_sql(customer_sql, conn).iloc[0]["customer_count"])
            summary_stats["Customers"] = f"{customer_count:,}"

        if "Track" in table_set:
            track_sql = text("SELECT COUNT(*) AS track_count FROM Track")
            track_count = int(pd.read_sql(track_sql, conn).iloc[0]["track_count"])
            summary_stats["Tracks"] = f"{track_count:,}"

    table_overview_df = pd.DataFrame(table_rows).sort_values("row_count", ascending=False)
    columns_df = pd.DataFrame(table_columns)
    relationships_df = pd.DataFrame(relationships)
    return table_overview_df, columns_df, relationships_df, summary_stats

