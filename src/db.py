from __future__ import annotations

import sqlite3

from src.config import DATA_DIR, SQLITE_PATH


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS studies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_key TEXT UNIQUE,
        title TEXT NOT NULL,
        source TEXT,
        original_filename TEXT,
        survey_schema_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS analysis_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_key TEXT NOT NULL,
        plan_name TEXT NOT NULL,
        analysis_plan_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS kpi_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_key TEXT NOT NULL,
        plan_name TEXT NOT NULL,
        kpi_id TEXT NOT NULL,
        kpi_name TEXT NOT NULL,
        output_type TEXT,
        chart_suggestion TEXT,
        result_json TEXT NOT NULL,
        executed_code TEXT,
        executed_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()