from __future__ import annotations

from src.parsers.base import BaseSurveyParser
from src.services.file_loader import load_raw_tabular_file
from src.services.header_etl import (
    detect_header_row,
    promote_header,
    split_admin_and_questions,
    standardize_headers,
)
from src.services.json_exporter import build_structured_json


class TestersParser(BaseSurveyParser):
    def parse(self, file_name: str, file_bytes: bytes):
        df_raw = load_raw_tabular_file(file_name, file_bytes)

        header_row_index = detect_header_row(df_raw)
        df = promote_header(df_raw, header_row_index)
        df = standardize_headers(df)

        admin_cols, question_cols = split_admin_and_questions(df)

        study_title = "Estudo sem título"

        for col in df.columns:
            if col.lower() in {"desc_questionario", "desc questionario"} and df[col].notna().any():
                study_title = str(df[col].dropna().iloc[0]).strip()
                break

        return {
            "dataframe": df,
            "structured": build_structured_json(
                df=df,
                source="Plataforma Testers",
                original_filename=file_name,
                study_title=study_title,
                admin_columns=admin_cols,
                question_columns=question_cols,
                header_row_index=header_row_index,
            ),
            "header_row_index": header_row_index,
        }