from __future__ import annotations

import streamlit as st


def render_page_header(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<p class="sai-page-header-subtitle">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="sai-page-header">
            <div class="sai-page-header-title">{title}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def open_section(title: str, caption: str | None = None) -> None:
    caption_html = f'<p class="sai-section-caption">{caption}</p>' if caption else ""
    st.markdown(
        f"""
        <div class="sai-section-card">
            <div class="sai-section-title">{title}</div>
            {caption_html}
        """,
        unsafe_allow_html=True,
    )


def close_section() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_divider() -> None:
    st.markdown('<div class="sai-divider"></div>', unsafe_allow_html=True)