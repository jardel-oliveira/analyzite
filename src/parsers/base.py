from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseSurveyParser(ABC):
    @abstractmethod
    def parse(self, file_name: str, file_bytes: bytes) -> Any:
        raise NotImplementedError