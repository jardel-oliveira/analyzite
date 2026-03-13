from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def _normalize_result(value: Any) -> dict:
    if isinstance(value, pd.DataFrame):
        return {
            "kind": "dataframe",
            "columns": value.columns.tolist(),
            "rows": value.head(500).to_dict(orient="records"),
        }

    if isinstance(value, pd.Series):
        return {
            "kind": "series",
            "name": value.name,
            "rows": value.reset_index().head(500).to_dict(orient="records"),
        }

    if isinstance(value, (int, float, str, bool)) or value is None:
        return {
            "kind": "scalar",
            "value": value,
        }

    if isinstance(value, list):
        return {
            "kind": "list",
            "value": value[:500],
        }

    if isinstance(value, dict):
        return {
            "kind": "dict",
            "value": value,
        }

    return {
        "kind": "repr",
        "value": repr(value),
    }


def execute_kpi_code(df: pd.DataFrame, code: str) -> dict:
    safe_globals: Dict[str, Any] = {
        "__builtins__": {
            "len": len,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "round": round,
            "float": float,
            "int": int,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "abs": abs,
            "range": range,
        },
        "pd": pd,
    }

    local_vars: Dict[str, Any] = {
        "df": df.copy(),
        "result": None,
    }

    exec(code, safe_globals, local_vars)

    if "result" not in local_vars:
        raise ValueError("O código do KPI deve definir uma variável chamada `result`.")

    return _normalize_result(local_vars["result"])


def execute_analysis_plan(df: pd.DataFrame, plan) -> List[dict]:
    results = []

    for kpi in plan.kpis:
        try:
            payload = execute_kpi_code(df, kpi.python_pandas_code)
            results.append(
                {
                    "kpi_id": kpi.id,
                    "kpi_name": kpi.name,
                    "description": kpi.description,
                    "output_type": kpi.output_type,
                    "chart_suggestion": kpi.chart_suggestion,
                    "formula_logic": kpi.formula_logic,
                    "based_on_questions": kpi.based_on_questions,
                    "status": "success",
                    "result": payload,
                    "executed_code": kpi.python_pandas_code,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "kpi_id": kpi.id,
                    "kpi_name": kpi.name,
                    "description": kpi.description,
                    "output_type": kpi.output_type,
                    "chart_suggestion": kpi.chart_suggestion,
                    "formula_logic": kpi.formula_logic,
                    "based_on_questions": kpi.based_on_questions,
                    "status": "error",
                    "error": str(exc),
                    "executed_code": kpi.python_pandas_code,
                }
            )

    return results