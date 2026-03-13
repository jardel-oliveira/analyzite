from __future__ import annotations

import streamlit as st

from src.ui.components import render_empty_state
from src.ui.layout import close_section, open_section, render_page_header


def render() -> None:
    render_page_header(
        "Schema",
        "Visualização resumida do survey schema e da estrutura do estudo carregado.",
    )

    schema = st.session_state.get("current_schema")

    if not schema:
        render_empty_state(
            "Nenhum schema carregado ainda.",
            "Faça a importação de um estudo para habilitar esta seção.",
            kind="warning",
        )
        return

    study = schema.get("study", {})
    questions = schema.get("questions", [])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Título", study.get("title", ""))

    with col2:
        st.metric("Fonte", study.get("source", ""))

    with col3:
        st.metric("Perguntas", len(questions))

    open_section(
        "Schema bruto",
        "O JSON completo fica recolhido por padrão para evitar uma página gigante.",
    )
    with st.expander("Ver schema bruto"):
        st.json(schema)
    close_section()