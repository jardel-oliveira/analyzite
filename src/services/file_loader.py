from __future__ import annotations

from io import BytesIO

import pandas as pd


def try_read_excel(file_bytes: bytes) -> pd.DataFrame:
    bio = BytesIO(file_bytes)

    try:
        return pd.read_excel(bio, engine="openpyxl")
    except Exception:
        pass

    bio.seek(0)
    try:
        return pd.read_excel(bio, engine="xlrd")
    except Exception:
        pass

    raise ValueError("Falha ao ler como Excel padrão.")


def try_read_html_table(file_bytes: bytes) -> pd.DataFrame:
    html = file_bytes.decode("utf-8", errors="ignore")
    tables = pd.read_html(html, header=None)
    if not tables:
        raise ValueError("Nenhuma tabela HTML encontrada.")
    return tables[0]


def try_read_csv(file_bytes: bytes) -> pd.DataFrame:
    bio = BytesIO(file_bytes)

    encodings = ["utf-8", "latin1", "cp1252"]
    separators = [",", ";", "\t"]

    for encoding in encodings:
        for separator in separators:
            try:
                bio.seek(0)
                return pd.read_csv(bio, encoding=encoding, sep=separator)
            except Exception:
                continue

    raise ValueError("Falha ao ler como CSV.")


def load_raw_tabular_file(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    lower_name = file_name.lower()

    if lower_name.endswith(".xlsx"):
        bio = BytesIO(file_bytes)
        return pd.read_excel(bio, header=None, engine="openpyxl")

    if lower_name.endswith(".xls"):
        try:
            bio = BytesIO(file_bytes)
            return pd.read_excel(bio, header=None, engine="xlrd")
        except Exception:
            return try_read_html_table(file_bytes)

    if lower_name.endswith(".csv"):
        bio = BytesIO(file_bytes)
        encodings = ["utf-8", "latin1", "cp1252"]
        separators = [",", ";", "\t"]

        for encoding in encodings:
            for separator in separators:
                try:
                    bio.seek(0)
                    return pd.read_csv(bio, encoding=encoding, sep=separator, header=None)
                except Exception:
                    continue

    raise ValueError("Formato não suportado. Use .xls, .xlsx ou .csv")