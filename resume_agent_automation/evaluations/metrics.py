from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricResult:
    name: str
    score: float = 0.0
    threshold: float = 0.0
    pass_: bool = False
    reason: str = ""
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.pass_

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "threshold": self.threshold,
            "pass": self.pass_,
            "reason": self.reason,
            "error": self.error,
            **self.details,
        }
