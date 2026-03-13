from __future__ import annotations

import streamlit as st

from src.ui.components import render_empty_state, render_kpi_card
from src.ui.layout import close_section, open_section, render_page_header


def render() -> None:
    render_page_header(
        "Dashboard",
        "Área de visualização dos KPIs, gráficos e resumos executivos.",
    )

    results = st.session_state.get("last_results")

    if not results:
        render_empty_state(
            "Nenhum resultado executado ainda.",
            "Depois que o plano analítico for executado, os KPIs aparecerão aqui.",
            kind="warning",
        )
        return

    success_results = [r for r in results if r.get("status") == "success"]
    error_results = [r for r in results if r.get("status") == "error"]

    open_section(
        "Resumo da execução",
        "Visão geral dos KPIs processados na sessão atual.",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("KPIs processados", len(results))
    with col2:
        st.metric("Sucesso", len(success_results))
    with col3:
        st.metric("Erros", len(error_results))
    close_section()

    open_section(
        "Filtros de visualização",
        "Filtre rapidamente os KPIs antes de visualizar os cards.",
    )
    status_filter = st.multiselect(
        "Status",
        options=["success", "error"],
        default=["success", "error"],
    )

    chart_filter = st.multiselect(
        "Tipo de gráfico",
        options=sorted(list({r.get("chart_suggestion", "table") for r in results})),
        default=sorted(list({r.get("chart_suggestion", "table") for r in results})),
    )
    close_section()

    filtered_results = [
        r for r in results
        if r.get("status") in status_filter and r.get("chart_suggestion", "table") in chart_filter
    ]

    open_section(
        "KPIs",
        "Cards visuais com gráfico, tabela, lógica e código.",
    )

    if not filtered_results:
        st.info("Nenhum KPI atende aos filtros selecionados.")
    else:
        for item in filtered_results:
            render_kpi_card(item)

    close_section()