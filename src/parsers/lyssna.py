from __future__ import annotations

from src.parsers.base import BaseSurveyParser


class LyssnaParser(BaseSurveyParser):
    def parse(self, file_name: str, file_bytes: bytes):
        raise NotImplementedError("Parser Lyssna ainda não implementado.")