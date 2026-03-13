from __future__ import annotations

from pathlib import Path
import streamlit as st


def load_css(css_path: str = "assets/css/main.css") -> None:
    path = Path(css_path)
    if not path.exists():
        st.warning(f"CSS não encontrado: {css_path}")
        return

    css = path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)