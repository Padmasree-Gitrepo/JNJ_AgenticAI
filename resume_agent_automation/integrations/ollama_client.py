from __future__ import annotations

import json
from typing import Any

import requests

from resume_agent_automation.config.settings import settings
from resume_agent_automation.utils.logger import build_logger

logger = build_logger("ollama_client", settings.LOGS_DIR)


class OllamaClient:
    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_GENERATION_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/api/generate"
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def list_models(self) -> list[str]:
        response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        models = []
        for model in data.get("models", []):
            name = model.get("name")
            if name:
                models.append(name)
        return models

    def ensure_model_available(self, model_name: str | None = None) -> str:
        model = model_name or self.model
        available = self.list_models()
        if model not in available:
            raise RuntimeError(f"Ollama model '{model}' is not available at {self.base_url}. Install and pull it first.")
        return model

    def generate(self, prompt: str, *, model: str | None = None, temperature: float | None = None) -> str:
        resolved_model = self.ensure_model_available(model or self.model)
        payload = {
            "model": resolved_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature if temperature is not None else settings.OLLAMA_TEMPERATURE},
        }
        logger.info("Generating Ollama response with model=%s", resolved_model)
        result = self._request(payload)
        return str(result.get("response", "")).strip()

    def generate_structured(self, prompt: str, *, model: str | None = None, temperature: float | None = None) -> dict[str, Any]:
        response = self.generate(prompt, model=model, temperature=temperature)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}
