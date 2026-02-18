from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleNewsQuery:
    q: str
    hl: str = "en"
    gl: str = "US"

    @property
    def ceid(self) -> str:
        # Google News often uses ceid=GL:HL
        return f"{self.gl}:{self.hl}"
