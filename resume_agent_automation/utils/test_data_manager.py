from __future__ import annotations

import json
from pathlib import Path

from resume_agent_automation.config.settings import settings


class TestDataManager:
    def __init__(self, approved_inputs_dir: str | Path | None = None):
        self.approved_inputs_dir = Path(approved_inputs_dir or settings.APPROVED_INPUTS_DIR)
        self.approved_inputs_dir.mkdir(parents=True, exist_ok=True)

    def store(self, test_id: str, payload: dict) -> Path:
        file_path = self.approved_inputs_dir / f"{test_id}.json"
        file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return file_path
