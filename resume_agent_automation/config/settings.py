from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_URL = os.getenv("APP_URL", "https://dna-preprod.hashedin.com/home/me/")
    APP_USERNAME = os.getenv("APP_USERNAME")
    APP_PASSWORD = os.getenv("APP_PASSWORD")

    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_GENERATION_MODEL = os.getenv("OLLAMA_GENERATION_MODEL", "gemma2:2b")
    OLLAMA_JUDGE_MODEL = os.getenv("OLLAMA_JUDGE_MODEL", "gemma2:2b")
    OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))
    OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0"))

    PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    PLAYWRIGHT_TIMEOUT = int(os.getenv("PLAYWRIGHT_TIMEOUT", "30000"))
    DEEP_EVAL_THRESHOLD = float(os.getenv("DEEP_EVAL_THRESHOLD", "0.70"))
    HALLUCINATION_RISK_THRESHOLD = float(os.getenv("HALLUCINATION_RISK_THRESHOLD", "0.30"))

    PROJECT_ROOT = BASE_DIR
    TEST_DATA_DIR = BASE_DIR / "test_data"
    MANUAL_CASE_FILE = TEST_DATA_DIR / "manual_test_cases.xlsx"
    TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
    REPORTS_DIR = BASE_DIR / "reports"
    SCREENSHOTS_DIR = BASE_DIR / "screenshots"
    LOGS_DIR = BASE_DIR / "logs"
    APPROVED_INPUTS_DIR = BASE_DIR / "approved_test_inputs"


settings = Settings()
