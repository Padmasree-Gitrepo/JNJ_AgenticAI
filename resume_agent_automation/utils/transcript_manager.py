from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from resume_agent_automation.config.settings import settings


class TranscriptManager:
    def __init__(self, transcripts_dir: str | Path | None = None):
        self.transcripts_dir = Path(transcripts_dir or settings.TRANSCRIPTS_DIR)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)

    def save(self, test_id: str, payload: dict) -> Path:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        file_path = self.transcripts_dir / f"{test_id}_{ts}.json"
        file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return file_path
