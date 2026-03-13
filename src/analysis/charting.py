from __future__ import annotations

import pandas as pd


def payload_to_dataframe(payload: dict) -> pd.DataFrame:
    kind = payload.get("kind")

    if kind == "dataframe":
        return pd.DataFrame(payload.get("rows", []))

    if kind == "series":
        return pd.DataFrame(payload.get("rows", []))

    if kind == "dict":
        value = payload.get("value", {})
        if isinstance(value, dict):
            return pd.DataFrame([value])
        return pd.DataFrame()

    if kind == "list":
        value = payload.get("value", [])
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                return pd.DataFrame(value)
            return pd.DataFrame({"value": value})
        return pd.DataFrame()

    return pd.DataFrame()


def guess_category_value_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    if df.empty or len(df.columns) == 0:
        return None, None

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

    category_col = non_numeric_cols[0] if non_numeric_cols else df.columns[0]
    value_col = numeric_cols[0] if numeric_cols else None

    if value_col is None and len(df.columns) >= 2:
        category_col = df.columns[0]
        value_col = df.columns[1]

    return category_col, value_col


def guess_stacked_columns(df: pd.DataFrame) -> tuple[str | None, str | None, str | None]:
    if df.empty or len(df.columns) < 3:
        return None, None, None

    return df.columns[0], df.columns[1], df.columns[2]


def scalar_from_payload(payload: dict):
    if payload.get("kind") == "scalar":
        return payload.get("value")
    return None


def is_plottable_dataframe(df: pd.DataFrame) -> bool:
    return not df.empty and len(df.columns) >= 2