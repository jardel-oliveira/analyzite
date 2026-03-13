from __future__ import annotations

import streamlit as st

from src.db import init_db
from src.pages import (
    analysis_plan,
    dashboard,
    home,
    import_data,
    schema_viewer,
    studies,
)
from src.ui.theme import load_css

st.set_page_config(
    page_title="Survey AI App",
    page_icon="📊",
    layout="wide",
)

PAGES = {
    "Home": home.render,
    "Importação": import_data.render,
    "Schema": schema_viewer.render,
    "Analysis Plan": analysis_plan.render,
    "Dashboard": dashboard.render,
    "Estudos": studies.render,
}


def init_session_state() -> None:
    defaults = {
        "current_df": None,
        "current_study_key": None,
        "current_study_title": None,
        "current_schema": None,
        "current_plan_name": None,
        "last_results": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> str:
    with st.sidebar:
        st.title("Survey AI")
        st.caption("Research analytics workspace")

        current_title = st.session_state.get("current_study_title")
        current_schema = st.session_state.get("current_schema")
        last_results = st.session_state.get("last_results")

        if current_title:
            st.success(f"Estudo atual: {current_title}")
        else:
            st.info("Nenhum estudo carregado")

        total_questions = len(current_schema.get("questions", [])) if current_schema else 0
        total_kpis = len(last_results) if last_results else 0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Perguntas", total_questions)
        with col2:
            st.metric("KPIs", total_kpis)

        page = st.radio(
            "Navegação",
            options=list(PAGES.keys()),
            index=0,
        )

    return page


def main() -> None:
    init_db()
    init_session_state()
    load_css()
    selected_page = render_sidebar()
    render_fn = PAGES[selected_page]
    render_fn()


if __name__ == "__main__":
    main()