import pandas as pd
import plotly.express as px
import streamlit as st

from app_core.database import (
    get_monthly_revenue_trend,
    get_revenue_by_country,
    get_revenue_by_genre,
    get_store_kpis,
    get_top_customers_by_revenue,
    get_top_selling_tracks,
)


def generate_chat_chart(df: pd.DataFrame, question: str):
    if df.empty or len(df.columns) < 1:
        return None

    for col in df.columns:
        if df[col].dtype == "object":
            try:
                df[col] = pd.to_datetime(df[col])
            except (ValueError, TypeError):
                pass

    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns
    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns

    if len(datetime_cols) >= 1 and len(numeric_cols) >= 1:
        df_sorted = df.sort_values(by=datetime_cols[0], ascending=True)
        return px.line(df_sorted, x=datetime_cols[0], y=numeric_cols[0], title=question, markers=True)

    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        df_sorted = df.sort_values(by=numeric_cols[0], ascending=False)
        if len(df_sorted) > 20:
            df_sorted = df_sorted.head(20)
            title = f"{question} (Top 20)"
        else:
            title = question
        return px.bar(df_sorted, x=categorical_cols[0], y=numeric_cols[0], title=title)

    if len(categorical_cols) == 1 and len(numeric_cols) == 0:
        counts = df[categorical_cols[0]].value_counts().reset_index()
        counts.columns = [categorical_cols[0], "count"]
        if len(counts) <= 7:
            return px.pie(counts, names=categorical_cols[0], values="count", title=question)
        return px.bar(counts.head(20), x=categorical_cols[0], y="count", title=f"{question} (Top 20)")

    if len(numeric_cols) >= 2:
        return px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=question)

    return None


def apply_bi_chart_layout(fig, x_title: str, y_title: str, legend_title: str, show_legend: bool = True):
    fig.update_layout(
        template="plotly_white",
        xaxis_title=x_title,
        yaxis_title=y_title,
        title_font=dict(size=18),
        title_x=0.5,
        legend_title_text=legend_title,
        showlegend=show_legend,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            borderwidth=0,
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=430,
        margin=dict(l=20, r=120, t=60, b=20),
    )
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(15, 23, 42, 0.08)", automargin=True)


def render_store_kpis(engine):
    kpis = get_store_kpis(engine)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
    c2.metric("Total Number of Invoices", f"{kpis['total_invoices']:,}")
    c3.metric("Total Customers", f"{kpis['total_customers']:,}")
    c4.metric("Average Order Value", f"${kpis['avg_order_value']:,.2f}")


def render_revenue_by_country_chart(engine):
    df = get_revenue_by_country(engine)
    df = df.sort_values("revenue", ascending=False).reset_index(drop=True)

    if len(df) > 10:
        top_df = df.head(10).copy()
        others_revenue = df.loc[10:, "revenue"].sum()
        country_df = pd.concat(
            [top_df, pd.DataFrame([{"country": "Others", "revenue": others_revenue}])],
            ignore_index=True,
        )
    else:
        country_df = df.copy()

    country_df["segment"] = country_df["country"].apply(lambda x: "Others" if x == "Others" else "Top Countries")

    fig = px.bar(
        country_df,
        x="country",
        y="revenue",
        title="Revenue by Country",
        labels={"country": "Country", "revenue": "Revenue"},
        color="segment",
        color_discrete_map={"Top Countries": "#1D4ED8", "Others": "#94A3B8"},
        text="revenue",
    )
    apply_bi_chart_layout(fig, "Country", "Revenue (USD)", "Category")
    fig.update_traces(
        marker_line_width=0,
        texttemplate="$%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
    )
    fig.update_yaxes(tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)


def render_top_customers_chart(engine):
    df = get_top_customers_by_revenue(engine, limit=10)
    df = df.sort_values("revenue", ascending=True).reset_index(drop=True)
    df["segment"] = "Top 10"
    df.loc[df.index >= len(df) - 3, "segment"] = "Top 3"

    fig = px.bar(
        df,
        x="revenue",
        y="customer_name",
        orientation="h",
        title="Top 10 Customers by Revenue",
        labels={"customer_name": "Customer", "revenue": "Revenue"},
        color="segment",
        color_discrete_map={"Top 10": "#14B8A6", "Top 3": "#0F766E"},
    )
    apply_bi_chart_layout(fig, "Revenue (USD)", "Customer", "Rank Segment")
    fig.update_traces(
        marker_line_width=0,
        texttemplate="$%{x:,.2f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>",
    )
    fig.update_xaxes(tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)


def render_revenue_by_genre_chart(engine):
    df = get_revenue_by_genre(engine).copy()
    df["segment"] = "Other Genres"
    df.loc[df.index < 5, "segment"] = "Top 5 Genres"

    fig = px.bar(
        df.head(15),
        x="genre",
        y="revenue",
        title="Revenue by Genre",
        labels={"genre": "Genre", "revenue": "Revenue"},
        color="segment",
        color_discrete_map={"Top 5 Genres": "#0284C7", "Other Genres": "#7DD3FC"},
    )
    apply_bi_chart_layout(fig, "Genre", "Revenue (USD)", "Category")
    fig.update_traces(marker_line_width=0, hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>")
    fig.update_xaxes(tickangle=-20)
    fig.update_yaxes(tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)


def render_monthly_revenue_trend_chart(engine):
    df = get_monthly_revenue_trend(engine)
    df = df.assign(metric="Revenue")
    fig = px.line(
        df,
        x="month",
        y="revenue",
        color="metric",
        title="Monthly Revenue Trend",
        labels={"month": "Month", "revenue": "Revenue"},
        markers=True,
        color_discrete_map={"Revenue": "#0F766E"},
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    apply_bi_chart_layout(fig, "Month", "Revenue (USD)", "Metric", show_legend=False)
    fig.update_traces(hovertemplate="<b>%{x|%b %Y}</b><br>Revenue: $%{y:,.2f}<extra></extra>")
    fig.update_yaxes(tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)


def render_top_selling_tracks_table(engine):
    df = get_top_selling_tracks(engine, limit=15).rename(
        columns={
            "track_name": "Track Name",
            "artist": "Artist",
            "album": "Album",
            "total_sales": "Total Sales",
        }
    )
    st.dataframe(
        df,
        use_container_width=True,
        column_config={"Total Sales": st.column_config.NumberColumn(format="$%.2f")},
    )

