from __future__ import annotations

from typing import List

from src.analysis.plan_models import AnalysisPlanModel


FORBIDDEN_SNIPPETS = [
    "import ",
    "__import__",
    "open(",
    "exec(",
    "eval(",
    "compile(",
    "subprocess",
    "os.",
    "sys.",
    "pathlib",
    "requests",
    "pickle",
]


def validate_analysis_plan_dict(plan_dict: dict) -> tuple[AnalysisPlanModel | None, List[str]]:
    errors: List[str] = []

    try:
        plan = AnalysisPlanModel.model_validate(plan_dict)
    except Exception as exc:
        return None, [f"Erro de schema: {exc}"]

    if not plan.kpis:
        errors.append("O analysis_plan.json não possui KPIs.")

    for idx, kpi in enumerate(plan.kpis, start=1):
        code = kpi.python_pandas_code or ""

        if "result" not in code:
            errors.append(f"KPI {idx} [{kpi.id}] não define a variável final `result`.")

        for forbidden in FORBIDDEN_SNIPPETS:
            if forbidden in code:
                errors.append(
                    f"KPI {idx} [{kpi.id}] contém trecho proibido: {forbidden}"
                )

    return plan, errors