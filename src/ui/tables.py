from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from src.analysis.charting import payload_to_dataframe


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def render_result_table(item: dict) -> None:
    if item.get("status") == "error":
        st.error(item.get("error", "Erro desconhecido"))
        return

    payload = item.get("result", {})
    df = payload_to_dataframe(payload)

    if df.empty:
        kind = payload.get("kind")
        if kind == "scalar":
            st.write(payload.get("value"))
        elif kind == "dict":
            st.json(payload.get("value"))
        elif kind == "list":
            st.json(payload.get("value"))
        else:
            st.info("Sem tabela estruturada para este KPI.")
        return

    st.dataframe(df, use_container_width=True)

    csv_bytes = dataframe_to_csv_bytes(df)
    st.download_button(
        label="Baixar CSV",
        data=csv_bytes,
        file_name=f"{item['kpi_id']}.csv",
        mime="text/csv",
        key=f"download_{item['kpi_id']}",
    )