from __future__ import annotations

from datetime import datetime
from typing import List

import pandas as pd

from src.models import QuestionModel, StructuredSurveyModel, StudyMetadata
from src.utils.text import normalize_for_match, normalize_spaces, slug_question


def infer_question_type(series: pd.Series, question_text: str) -> tuple[str, list[str], str | None]:
    non_null = series.dropna().astype(str).map(normalize_spaces)
    unique_vals = [v for v in non_null.unique().tolist() if v]

    q_norm = normalize_for_match(question_text)

    if not unique_vals:
        return "unknown", [], None

    if any(";" in v for v in unique_vals):
        options = set()
        for val in unique_vals:
            for part in val.split(";"):
                part = normalize_spaces(part)
                if part:
                    options.add(part)
        return "multiple_choice", sorted(options), ";"

    if "[" in question_text and "]" in question_text:
        return "matrix", sorted(unique_vals)[:30], None

    numeric_like = True
    numeric_values = []

    for v in unique_vals[:50]:
        try:
            numeric_values.append(float(v.replace(",", ".")))
        except Exception:
            numeric_like = False
            break

    if numeric_like and numeric_values:
        if all(0 <= x <= 10 for x in numeric_values):
            return "scale", sorted(unique_vals), None
        if all(1 <= x <= 5 for x in numeric_values):
            return "scale", sorted(unique_vals), None

    if len(unique_vals) <= 20:
        return "single_choice", sorted(unique_vals), None

    if any(term in q_norm for term in ["por que", "porque", "qual motivo", "descreva", "comente", "outro, qual"]):
        return "open_text", [], None

    return "open_text", [], None


def infer_analytical_role(question_text: str, q_type: str) -> str:
    text = normalize_for_match(question_text)

    if q_type == "open_text":
        return "aberta"

    if any(t in text for t in ["idade", "faixa etaria", "sexo", "cidade", "renda", "estado civil"]):
        return "perfil"

    if any(t in text for t in ["possui", "tem", "ja teve", "assinante", "cliente", "cartao"]):
        return "posse_produto"

    if any(t in text for t in ["frequencia", "com que frequencia", "quantas vezes", "costuma"]):
        return "frequencia_uso"

    if any(t in text for t in ["satisfeito", "satisfacao", "nota", "avalia", "avaliacao", "escala"]):
        return "satisfacao"

    if any(t in text for t in ["barreira", "dificuldade", "problema", "impede", "motivo para nao"]):
        return "barreira"

    if any(t in text for t in ["pretende", "intencao", "consideraria", "teria interesse"]):
        return "intencao"

    if any(t in text for t in ["atributo", "beneficio", "vantagem", "importante", "relevante"]):
        return "atributo_avaliado"

    if any(t in text for t in ["etapa", "jornada", "processo", "momento"]):
        return "jornada"

    if q_type in {"single_choice", "multiple_choice"}:
        return "comportamento"

    return "unknown"


def suggest_kpis(question_text: str, q_type: str, analytical_role: str) -> List[str]:
    text = normalize_for_match(question_text)
    kpis: List[str] = []

    if analytical_role == "perfil":
        kpis.extend([
            "distribuicao_percentual",
            "perfil_majoritario",
        ])

    if analytical_role == "posse_produto":
        kpis.extend([
            "penetracao_posse",
            "percentual_nao_possui",
        ])

    if analytical_role == "frequencia_uso":
        kpis.extend([
            "frequencia_alta",
            "frequencia_baixa",
            "score_engajamento",
        ])

    if analytical_role == "satisfacao":
        kpis.extend([
            "media_avaliacao",
            "top2box",
            "bottom2box",
        ])

    if analytical_role == "barreira":
        kpis.extend([
            "principais_barreiras",
            "participacao_por_barreira",
        ])

    if analytical_role == "intencao":
        kpis.extend([
            "intencao_positiva",
            "intencao_negativa",
        ])

    if analytical_role == "atributo_avaliado":
        kpis.extend([
            "atributos_mais_relevantes",
            "atributos_menos_relevantes",
        ])

    if analytical_role == "comportamento":
        kpis.extend([
            "participacao_por_resposta",
            "ranking_respostas",
        ])

    if q_type == "multiple_choice":
        kpis.append("multi_pick_rate")

    if q_type == "open_text":
        kpis.extend([
            "volume_respostas_abertas",
            "temas_frequentes",
        ])

    if "smiles" in text:
        kpis.append("afinidade_smiles")

    return sorted(list(set(kpis)))


def get_example_values(series: pd.Series, limit: int = 5) -> List[str]:
    non_null = series.dropna().astype(str).map(normalize_spaces)
    values = [v for v in non_null.unique().tolist() if v]
    return values[:limit]


def build_structured_json(
    df: pd.DataFrame,
    source: str,
    original_filename: str,
    study_title: str,
    admin_columns: List[str],
    question_columns: List[str],
    header_row_index: int,
) -> StructuredSurveyModel:
    questions = []

    for idx, col in enumerate(question_columns, start=1):
        series = df[col]
        q_type, options, separator = infer_question_type(series, col)
        role = infer_analytical_role(col, q_type)
        kpis = suggest_kpis(col, q_type, role)

        questions.append(
            QuestionModel(
                id=slug_question(col, idx),
                text=col,
                column_name=col,
                question_type=q_type,
                analytical_role=role,
                options_observed=options[:50],
                example_values=get_example_values(series),
                multi_separator=separator,
                null_count=int(series.isna().sum()),
                non_null_count=int(series.notna().sum()),
                distinct_count=int(series.dropna().astype(str).nunique()),
                suggested_kpis=kpis,
                related_columns=[],
            )
        )

    payload = StructuredSurveyModel(
        study=StudyMetadata(
            source=source,
            title=study_title,
            imported_at=datetime.now().isoformat(),
            original_filename=original_filename,
            total_rows=len(df),
            total_columns=len(df.columns),
            header_row_index=header_row_index,
        ),
        admin_columns=admin_columns,
        questions=questions,
    )

    return payload