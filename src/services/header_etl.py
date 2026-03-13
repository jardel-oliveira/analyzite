from __future__ import annotations

from typing import List, Tuple

import pandas as pd

from src.utils.text import normalize_for_match, normalize_spaces


KNOWN_ADMIN_COLUMNS = {
    "dataresposta",
    "desc_questionario",
    "desc questionario",
    "idpessoa",
    "nomepessoa",
    "datanascimento",
    "idade",
    "respostaadmin",
    "cpf",
    "email",
    "telefone",
    "sexo",
    "cidade",
    "uf",
    "data de resposta",
    "nome",
    "respondentid",
    "participantid",
    "id",
}


ADMIN_HINTS = [
    "idpessoa",
    "nomepessoa",
    "dataresposta",
    "desc_questionario",
    "idade",
    "sexo",
    "email",
]


QUESTION_HINTS = [
    "?",
    "qual",
    "quais",
    "como",
    "com que",
    "o quanto",
    "em uma escala",
    "por que",
    "você",
    "voce",
    "costuma",
    "utiliza",
    "possui",
]


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    text = normalize_spaces(str(value))
    if text.lower().startswith("unnamed:"):
        return ""
    if text.lower() == "nan":
        return ""
    return text


def score_header_row(row_values: List[str]) -> int:
    score = 0
    filled = [v for v in row_values if v]

    if len(filled) >= 5:
        score += 3

    for value in filled:
        norm = normalize_for_match(value)

        if norm in KNOWN_ADMIN_COLUMNS:
            score += 4

        if any(h in norm for h in ADMIN_HINTS):
            score += 2

        if any(h in norm for h in QUESTION_HINTS):
            score += 3

        if len(value) > 20:
            score += 1

        if "?" in value:
            score += 2

    return score


def detect_header_row(df_raw: pd.DataFrame, max_scan_rows: int = 20) -> int:
    best_idx = 0
    best_score = -1

    limit = min(max_scan_rows, len(df_raw))

    for idx in range(limit):
        row = [clean_cell(v) for v in df_raw.iloc[idx].tolist()]
        score = score_header_row(row)

        if score > best_score:
            best_score = score
            best_idx = idx

    return best_idx


def make_unique_columns(columns: List[str]) -> List[str]:
    seen: dict[str, int] = {}
    result: List[str] = []

    for idx, col in enumerate(columns):
        base = clean_cell(col)
        if not base:
            base = f"col_{idx}"

        if base not in seen:
            seen[base] = 1
            result.append(base)
        else:
            seen[base] += 1
            result.append(f"{base}__{seen[base]}")

    return result


def promote_header(df_raw: pd.DataFrame, header_row_index: int) -> pd.DataFrame:
    header = [clean_cell(v) for v in df_raw.iloc[header_row_index].tolist()]
    data = df_raw.iloc[header_row_index + 1 :].copy()
    data.columns = make_unique_columns(header)
    data = data.reset_index(drop=True)

    empty_cols = [c for c in data.columns if not normalize_spaces(c)]
    if empty_cols:
        data = data.drop(columns=empty_cols, errors="ignore")

    return data


def standardize_headers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [clean_cell(c) for c in df.columns]
    return df


def split_admin_and_questions(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    admin_cols = []
    question_cols = []

    for col in df.columns:
        clean = clean_cell(col)
        norm = normalize_for_match(clean)

        if not clean:
            continue

        if norm in KNOWN_ADMIN_COLUMNS:
            admin_cols.append(clean)
            continue

        if any(h in norm for h in ADMIN_HINTS):
            admin_cols.append(clean)
            continue

        question_cols.append(clean)

    return admin_cols, question_cols