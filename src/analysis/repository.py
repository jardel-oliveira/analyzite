from __future__ import annotations

import json
from datetime import datetime

from src.db import get_connection


def save_study(
    study_key: str,
    title: str,
    source: str,
    original_filename: str,
    survey_schema_json: dict,
) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO studies (
        study_key, title, source, original_filename, survey_schema_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        study_key,
        title,
        source,
        original_filename,
        json.dumps(survey_schema_json, ensure_ascii=False),
        datetime.now().isoformat(),
    ))

    conn.commit()
    conn.close()


def list_studies() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT id, study_key, title, source, original_filename, created_at
    FROM studies
    ORDER BY id DESC
    """).fetchall()

    conn.close()
    return [dict(row) for row in rows]


def get_study_by_key(study_key: str) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute("""
    SELECT id, study_key, title, source, original_filename, survey_schema_json, created_at
    FROM studies
    WHERE study_key = ?
    """, (study_key,)).fetchone()

    conn.close()

    if not row:
        return None

    payload = dict(row)
    payload["survey_schema_json"] = json.loads(payload["survey_schema_json"])
    return payload


def save_analysis_plan(
    study_key: str,
    plan_name: str,
    analysis_plan_json: dict,
) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO analysis_plans (
        study_key, plan_name, analysis_plan_json, created_at
    ) VALUES (?, ?, ?, ?)
    """, (
        study_key,
        plan_name,
        json.dumps(analysis_plan_json, ensure_ascii=False),
        datetime.now().isoformat(),
    ))

    conn.commit()
    conn.close()


def list_analysis_plans(study_key: str) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT id, study_key, plan_name, analysis_plan_json, created_at
    FROM analysis_plans
    WHERE study_key = ?
    ORDER BY id DESC
    """, (study_key,)).fetchall()

    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["analysis_plan_json"] = json.loads(item["analysis_plan_json"])
        result.append(item)
    return result


def save_kpi_results(
    study_key: str,
    plan_name: str,
    kpi_results: list[dict],
) -> None:
    conn = get_connection()
    cur = conn.cursor()

    for item in kpi_results:
        cur.execute("""
        INSERT INTO kpi_results (
            study_key, plan_name, kpi_id, kpi_name, output_type,
            chart_suggestion, result_json, executed_code, executed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            study_key,
            plan_name,
            item["kpi_id"],
            item["kpi_name"],
            item.get("output_type"),
            item.get("chart_suggestion"),
            json.dumps(item, ensure_ascii=False),
            item.get("executed_code"),
            datetime.now().isoformat(),
        ))

    conn.commit()
    conn.close()


def list_kpi_results(study_key: str) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT id, study_key, plan_name, kpi_id, kpi_name, output_type,
           chart_suggestion, result_json, executed_at
    FROM kpi_results
    WHERE study_key = ?
    ORDER BY id DESC
    """, (study_key,)).fetchall()

    conn.close()
    return [dict(row) for row in rows]