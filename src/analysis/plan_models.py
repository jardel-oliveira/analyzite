from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


ChartSuggestion = Literal["bar", "pie", "stacked_bar", "scorecard", "table"]
OutputType = Literal["percentage", "count", "mean", "distribution", "text_summary"]


class KPIModel(BaseModel):
    id: str
    name: str
    description: str
    based_on_questions: List[str] = Field(default_factory=list)
    analytical_role: str
    chart_suggestion: ChartSuggestion
    output_type: OutputType
    formula_logic: str
    python_pandas_code: str


class AnalysisPlanModel(BaseModel):
    study_title: str
    kpis: List[KPIModel]