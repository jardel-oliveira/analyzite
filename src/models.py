from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


QuestionType = Literal[
    "single_choice",
    "multiple_choice",
    "open_text",
    "scale",
    "matrix",
    "unknown",
]

AnalyticalRole = Literal[
    "perfil",
    "posse_produto",
    "frequencia_uso",
    "comportamento",
    "satisfacao",
    "atributo_avaliado",
    "barreira",
    "intencao",
    "jornada",
    "segmentacao",
    "aberta",
    "unknown",
]


class StudyMetadata(BaseModel):
    source: str
    title: str
    imported_at: str
    original_filename: str
    total_rows: int
    total_columns: int
    header_row_index: int
    parser_version: str = "v2"


class QuestionModel(BaseModel):
    id: str
    text: str
    column_name: str
    question_type: QuestionType = "unknown"
    analytical_role: AnalyticalRole = "unknown"
    options_observed: List[str] = Field(default_factory=list)
    example_values: List[str] = Field(default_factory=list)
    multi_separator: Optional[str] = None
    null_count: int = 0
    non_null_count: int = 0
    distinct_count: int = 0
    suggested_kpis: List[str] = Field(default_factory=list)
    related_columns: List[str] = Field(default_factory=list)


class StructuredSurveyModel(BaseModel):
    study: StudyMetadata
    admin_columns: List[str]
    questions: List[QuestionModel]