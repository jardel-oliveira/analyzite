from __future__ import annotations

import streamlit as st

from src.analysis.repository import get_study_by_key, list_studies
from src.ui.components import render_empty_state
from src.ui.layout import close_section, open_section, render_page_header


def render() -> None:
    render_page_header(
        "Estudos",
        "Histórico de estudos salvos e reabertura do schema no workspace atual.",
    )

    studies = list_studies()

    if not studies:
        render_empty_state(
            "Nenhum estudo salvo ainda.",
            "Faça a importação de um arquivo para começar a registrar estudos no banco local.",
            kind="info",
        )
        return

    open_section(
        "Histórico",
        "Lista dos estudos já persistidos no SQLite local.",
    )
    st.dataframe(studies, use_container_width=True)
    close_section()

    options = [study["study_key"] for study in studies]
    selected_key = st.selectbox(
        "Selecione um estudo",
        options=options,
    )

    if not selected_key:
        return

    selected_study = get_study_by_key(selected_key)

    if not selected_study:
        render_empty_state(
            "Estudo não encontrado.",
            "Não foi possível recuperar o estudo selecionado.",
            kind="warning",
        )
        return

    if st.button("Carregar estudo no workspace"):
        schema = selected_study["survey_schema_json"]
        st.session_state["current_study_key"] = selected_study["study_key"]
        st.session_state["current_study_title"] = selected_study["title"]
        st.session_state["current_schema"] = schema
        st.success("Estudo carregado no workspace atual.")

    open_section(
        "Resumo do estudo selecionado",
        "Visualização rápida do schema salvo.",
    )
    schema = selected_study["survey_schema_json"]
    study = schema.get("study", {})
    questions = schema.get("questions", [])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Título", study.get("title", ""))
    with col2:
        st.metric("Fonte", study.get("source", ""))
    with col3:
        st.metric("Perguntas", len(questions))

    with st.expander("Ver schema salvo"):
        st.json(schema)
    close_section()