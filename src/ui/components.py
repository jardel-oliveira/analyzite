from __future__ import annotations

import streamlit as st

from src.ui.charts import render_chart_from_result
from src.ui.tables import render_result_table


def render_chip_row(values: list[str]) -> None:
    if not values:
        return

    html = "".join([f'<span class="sai-chip">{value}</span>' for value in values])
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state(
    title: str,
    description: str | None = None,
    kind: str = "info",
) -> None:
    if kind == "warning":
        st.warning(f"{title}\n\n{description or ''}")
    elif kind == "success":
        st.success(f"{title}\n\n{description or ''}")
    elif kind == "error":
        st.error(f"{title}\n\n{description or ''}")
    else:
        st.info(f"{title}\n\n{description or ''}")


def render_key_value_block(items: dict[str, str]) -> None:
    for key, value in items.items():
        st.markdown(f"**{key}**")
        st.write(value)


def render_kpi_card(item: dict) -> None:
    st.markdown('<div class="sai-kpi-card">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="sai-kpi-header">
            <div class="sai-kpi-title">{item['kpi_name']}</div>
            <div class="sai-kpi-meta">
                <span class="sai-kpi-badge">{item.get('output_type', '')}</span>
                <span class="sai-kpi-badge">{item.get('chart_suggestion', '')}</span>
                <span class="sai-kpi-badge">{item.get('status', '')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if item.get("description"):
        st.markdown(
            f'<div class="sai-kpi-description">{item["description"]}</div>',
            unsafe_allow_html=True,
        )

    render_chart_from_result(item)

    tabs = st.tabs(["Tabela", "Lógica", "Código"])

    with tabs[0]:
        render_result_table(item)

    with tabs[1]:
        st.write(item.get("formula_logic", ""))

    with tabs[2]:
        st.code(item.get("executed_code", ""), language="python")

    st.markdown("</div>", unsafe_allow_html=True)