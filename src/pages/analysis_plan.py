from __future__ import annotations

import json

import streamlit as st

from src.analysis.executor import execute_analysis_plan
from src.analysis.repository import save_analysis_plan, save_kpi_results
from src.analysis.validator import validate_analysis_plan_dict
from src.ui.components import render_empty_state
from src.ui.layout import close_section, open_section, render_page_header


def render_result_preview(item: dict) -> None:
    st.markdown(f"**{item['kpi_name']}**")
    st.caption(
        f"Tipo: {item.get('output_type', '')} | Gráfico: {item.get('chart_suggestion', '')} | Status: {item.get('status', '')}"
    )

    if item["status"] == "error":
        st.error(item.get("error", "Erro desconhecido"))
        with st.expander("Código executado"):
            st.code(item.get("executed_code", ""), language="python")
        return

    payload = item.get("result", {})
    kind = payload.get("kind")

    if kind == "scalar":
        st.metric("Resultado", payload.get("value"))
    elif kind in {"dataframe", "series"}:
        import pandas as pd
        df_res = pd.DataFrame(payload.get("rows", []))
        st.dataframe(df_res, use_container_width=True)
    elif kind == "dict":
        st.json(payload.get("value"))
    elif kind == "list":
        st.json(payload.get("value"))
    else:
        st.write(payload)

    with st.expander("Código executado"):
        st.code(item.get("executed_code", ""), language="python")


def render() -> None:
    render_page_header(
        "Analysis Plan",
        "Importação, validação e execução do plano analítico gerado pelo agente.",
    )

    current_study_key = st.session_state.get("current_study_key")
    current_study_title = st.session_state.get("current_study_title")
    current_df = st.session_state.get("current_df")

    if not current_study_key or current_df is None:
        render_empty_state(
            "Nenhum estudo ativo com DataFrame em memória.",
            "Importe um arquivo na página de Importação antes de carregar o analysis_plan.json.",
            kind="warning",
        )
        return

    open_section(
        "Contexto atual",
        "Resumo do estudo atualmente carregado no workspace.",
    )
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Study Key", current_study_key)
    with col2:
        st.metric("Study Title", current_study_title or "")
    close_section()

    open_section(
        "Upload do plano analítico",
        "Envie o analysis_plan.json produzido pelo agente de IA.",
    )
    plan_name = st.text_input("Nome do plano analítico", value="plano_inicial")
    uploaded_plan = st.file_uploader(
        "Arquivo analysis_plan.json",
        type=["json"],
        key="analysis_plan_upload_v2",
    )
    close_section()

    if uploaded_plan is None:
        render_empty_state(
            "Nenhum analysis_plan.json enviado ainda.",
            "Depois do upload vamos validar o schema do plano e os códigos Python/Pandas.",
            kind="info",
        )
        return

    try:
        plan_dict = json.loads(uploaded_plan.getvalue().decode("utf-8"))
    except Exception as exc:
        render_empty_state(
            "Falha ao ler o JSON enviado.",
            str(exc),
            kind="error",
        )
        return

    plan, validation_errors = validate_analysis_plan_dict(plan_dict)

    open_section(
        "Validação do plano",
        "Checagem estrutural e técnica antes da execução.",
    )
    if validation_errors:
        st.error("Foram encontrados problemas no analysis_plan.json.")
        for err in validation_errors:
            st.write(f"• {err}")
        close_section()
        return

    st.success("analysis_plan.json validado com sucesso.")
    with st.expander("Ver JSON validado"):
        st.json(plan.model_dump())
    close_section()

    open_section(
        "Execução",
        "Execute o plano analítico com base no DataFrame atualmente carregado.",
    )
    if st.button("Executar plano analítico"):
        results = execute_analysis_plan(current_df, plan)

        save_analysis_plan(
            study_key=current_study_key,
            plan_name=plan_name,
            analysis_plan_json=plan.model_dump(),
        )

        save_kpi_results(
            study_key=current_study_key,
            plan_name=plan_name,
            kpi_results=results,
        )

        st.session_state["current_plan_name"] = plan_name
        st.session_state["last_results"] = results

        st.success("Plano executado e resultados salvos com sucesso.")
    close_section()

    if st.session_state.get("last_results"):
        open_section(
            "Prévia dos resultados",
            "Resumo dos KPIs executados na sessão atual.",
        )
        for item in st.session_state["last_results"]:
            render_result_preview(item)
        close_section()