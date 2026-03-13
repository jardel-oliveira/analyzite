from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.analysis.repository import save_study
from src.config import PROCESSED_DIR, RAW_DIR
from src.parsers.lyssna import LyssnaParser
from src.parsers.testers import TestersParser
from src.ui.components import render_empty_state
from src.ui.layout import close_section, open_section, render_page_header


def render() -> None:
    render_page_header(
        "Importação",
        "Área de upload, processamento de arquivo e geração do survey schema.",
    )

    open_section(
        "Configuração de origem",
        "Escolha a plataforma de origem do arquivo antes do upload.",
    )
    source = st.selectbox(
        "Plataforma",
        ["Plataforma Testers", "Lyssna"],
    )
    close_section()

    open_section(
        "Upload do arquivo",
        "Envie um arquivo .xls, .xlsx ou .csv para iniciar o processamento.",
    )
    uploaded_file = st.file_uploader(
        "Arquivo de pesquisa",
        type=["xls", "xlsx", "csv"],
        key="survey_upload_v2",
    )
    close_section()

    if uploaded_file is None:
        render_empty_state(
            "Nenhum arquivo enviado ainda.",
            "Assim que você subir um arquivo, vamos detectar o cabeçalho, estruturar as perguntas e gerar o schema.",
            kind="info",
        )
        return

    file_name = uploaded_file.name
    file_bytes = uploaded_file.getvalue()

    raw_path = RAW_DIR / file_name
    raw_path.write_bytes(file_bytes)

    try:
        parser = TestersParser() if source == "Plataforma Testers" else LyssnaParser()
        result = parser.parse(file_name=file_name, file_bytes=file_bytes)

        df = result["dataframe"]
        structured = result["structured"]
        header_row_index = result.get("header_row_index", -1)

        structured_dict = structured.model_dump()
        study_key = Path(file_name).stem

        save_study(
            study_key=study_key,
            title=structured.study.title,
            source=structured.study.source,
            original_filename=file_name,
            survey_schema_json=structured_dict,
        )

        json_name = Path(file_name).stem + "_survey_schema.json"
        json_path = PROCESSED_DIR / json_name
        json_path.write_text(
            json.dumps(structured_dict, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        st.session_state["current_df"] = df
        st.session_state["current_study_key"] = study_key
        st.session_state["current_study_title"] = structured.study.title
        st.session_state["current_schema"] = structured_dict

        open_section(
            "Processamento concluído",
            "Resumo do arquivo processado e do schema gerado.",
        )
        st.success("Arquivo processado e study schema salvo com sucesso.")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Linhas", df.shape[0])
        with col2:
            st.metric("Colunas", df.shape[1])
        with col3:
            st.metric("Perguntas", len(structured.questions))
        with col4:
            st.metric("Header detectado", header_row_index)

        st.download_button(
            label="Baixar survey_schema.json",
            data=json.dumps(structured_dict, ensure_ascii=False, indent=2),
            file_name=json_name,
            mime="application/json",
        )
        close_section()

        open_section(
            "Preview do arquivo",
            "Primeiras linhas do dataframe já com cabeçalho promovido.",
        )
        st.dataframe(df.head(20), use_container_width=True)
        close_section()

        open_section(
            "Resumo das perguntas",
            "Visualização compacta das perguntas identificadas no questionário.",
        )
        preview_questions = [
            {
                "id": q.id,
                "pergunta": q.text,
                "tipo": q.question_type,
                "papel_analitico": q.analytical_role,
                "kpis_sugeridos": ", ".join(q.suggested_kpis),
            }
            for q in structured.questions[:50]
        ]
        st.dataframe(preview_questions, use_container_width=True)
        close_section()

        open_section(
            "Schema bruto",
            "O JSON completo fica recolhido por padrão para evitar uma tela longa demais.",
        )
        with st.expander("Ver survey schema completo"):
            st.json(structured_dict)
        close_section()

    except NotImplementedError as exc:
        render_empty_state(
            "Fluxo ainda não implementado para esta origem.",
            str(exc),
            kind="warning",
        )
    except Exception as exc:
        render_empty_state(
            "Erro ao processar o arquivo.",
            str(exc),
            kind="error",
        )