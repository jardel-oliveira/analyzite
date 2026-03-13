from __future__ import annotations

import streamlit as st

from src.ui.components import render_chip_row
from src.ui.layout import open_section, close_section, render_page_header


def render() -> None:
    render_page_header(
        "Home",
        "Workspace principal do Survey AI App, com visão rápida do estudo atual e do progresso analítico.",
    )

    current_schema = st.session_state.get("current_schema")
    last_results = st.session_state.get("last_results")

    total_questions = len(current_schema.get("questions", [])) if current_schema else 0
    total_kpis = len(last_results) if last_results else 0
    study_loaded = "Sim" if st.session_state.get("current_study_title") else "Não"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Estudo carregado", study_loaded)

    with col2:
        st.metric("Perguntas", total_questions)

    with col3:
        st.metric("KPIs executados", total_kpis)

    open_section(
        "Fluxo do produto",
        "Aqui vamos evoluir o app por camadas, da ingestão até a visualização moderna.",
    )
    render_chip_row([
        "Importação",
        "Schema",
        "Analysis Plan",
        "Dashboard",
        "SQLite",
        "UI Moderna",
    ])
    st.write(
        """
        Nesta nova arquitetura, vamos evoluir o app por camadas.

        Primeiro organizamos páginas e tema visual.
        Depois recolocamos o fluxo de importação.
        Em seguida, retomamos plano analítico, gráficos modernos e tabelas interativas.
        """
    )
    close_section()