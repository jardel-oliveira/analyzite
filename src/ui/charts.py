from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis.charting import (
    guess_category_value_columns,
    guess_stacked_columns,
    is_plottable_dataframe,
    payload_to_dataframe,
    scalar_from_payload,
)


def render_chart_from_result(item: dict) -> None:
    if item.get("status") == "error":
        st.error(item.get("error", "Erro desconhecido"))
        return

    payload = item.get("result", {})
    chart_type = item.get("chart_suggestion", "table")

    if chart_type == "scorecard":
        render_scorecard(payload, item.get("kpi_name", "Resultado"))
        return

    if chart_type == "bar":
        render_bar_chart(payload)
        return

    if chart_type == "pie":
        render_pie_chart(payload)
        return

    if chart_type == "stacked_bar":
        render_stacked_bar_chart(payload)
        return

    if chart_type == "table":
        render_table_fallback(payload)
        return

    render_table_fallback(payload)


def render_scorecard(payload: dict, label: str) -> None:
    value = scalar_from_payload(payload)
    if value is not None:
        st.metric(label, value)
        return

    df = payload_to_dataframe(payload)
    if not df.empty and len(df.columns) >= 1:
        st.metric(label, df.iloc[0, 0])
        return

    st.info("Não foi possível renderizar este KPI como card numérico.")


def render_bar_chart(payload: dict) -> None:
    df = payload_to_dataframe(payload)
    if not is_plottable_dataframe(df):
        render_table_fallback(payload)
        return

    category_col, value_col = guess_category_value_columns(df)
    if not category_col or not value_col:
        render_table_fallback(payload)
        return

    fig = px.bar(
        df,
        x=category_col,
        y=value_col,
        text=value_col,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=420,
        xaxis_title="",
        yaxis_title="",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_pie_chart(payload: dict) -> None:
    df = payload_to_dataframe(payload)
    if not is_plottable_dataframe(df):
        render_table_fallback(payload)
        return

    category_col, value_col = guess_category_value_columns(df)
    if not category_col or not value_col:
        render_table_fallback(payload)
        return

    fig = px.pie(
        df,
        names=category_col,
        values=value_col,
        hole=0.45,
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_stacked_bar_chart(payload: dict) -> None:
    df = payload_to_dataframe(payload)
    if df.empty or len(df.columns) < 3:
        render_table_fallback(payload)
        return

    category_col, series_col, value_col = guess_stacked_columns(df)
    if not category_col or not series_col or not value_col:
        render_table_fallback(payload)
        return

    fig = px.bar(
        df,
        x=category_col,
        y=value_col,
        color=series_col,
        text=value_col,
        barmode="stack",
    )
    fig.update_traces(textposition="inside")
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=440,
        xaxis_title="",
        yaxis_title="",
        legend_title="",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_table_fallback(payload: dict) -> None:
    df = payload_to_dataframe(payload)

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        return

    kind = payload.get("kind")

    if kind == "scalar":
        st.metric("Resultado", payload.get("value"))
    elif kind == "dict":
        st.json(payload.get("value"))
    elif kind == "list":
        st.json(payload.get("value"))
    else:
        st.write(payload)