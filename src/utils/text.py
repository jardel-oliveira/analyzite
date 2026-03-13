from __future__ import annotations

import re
import unicodedata


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def strip_accents(text: str) -> str:
    text = str(text)
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )


def normalize_for_match(text: str) -> str:
    text = normalize_spaces(text).lower()
    text = strip_accents(text)
    return text


def slug_question(text: str, index: int) -> str:
    base = normalize_spaces(text).lower()
    base = strip_accents(base)
    base = re.sub(r"[^a-z0-9]+", "_", base)
    base = re.sub(r"_+", "_", base).strip("_")
    return f"q{index:03d}" if not base else f"q{index:03d}_{base[:50]}"