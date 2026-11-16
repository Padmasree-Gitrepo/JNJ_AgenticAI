from __future__ import annotations

from typing import Any

from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, HallucinationMetric
from deepeval.models import OllamaModel
from deepeval.test_case import LLMTestCase

from resume_agent_automation.config.settings import settings
from resume_agent_automation.utils.logger import build_logger

logger = build_logger("deepeval_judge", settings.LOGS_DIR)


def build_ollama_judge(
    model_name: str | None = None,
    base_url: str | None = None,
    temperature: float | None = None,
) -> OllamaModel:
    judge_model = OllamaModel(
        model=model_name or settings.OLLAMA_JUDGE_MODEL,
        base_url=base_url or settings.OLLAMA_BASE_URL,
        temperature=temperature if temperature is not None else 0,
    )
    logger.info("Configured DeepEval judge model=%s base_url=%s", judge_model.model, judge_model.base_url)
    return judge_model


def _measure_metric(metric: Any, test_case: LLMTestCase) -> dict[str, Any]:
    try:
        score = float(metric.measure(test_case, _show_indicator=False))
        reason = getattr(metric, "reason", "") or "No reason supplied."
        threshold = float(getattr(metric, "threshold", 0.0) or 0.0)
        success = bool(getattr(metric, "success", False))
        return {
            "score": score,
            "threshold": threshold,
            "pass": success,
            "reason": reason,
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - evaluation failure is intentionally captured
        logger.exception("DeepEval metric execution failed")
        return {
            "score": 0.0,
            "threshold": 0.0,
            "pass": False,
            "reason": f"Evaluation error: {exc}",
            "error": str(exc),
        }


def evaluate_agent_response(
    *,
    input_text: str,
    actual_output: str,
    reference_context: str,
    judge_model: OllamaModel | None = None,
) -> dict[str, Any]:
    model = judge_model or build_ollama_judge()

    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        context=[reference_context],
        retrieval_context=[reference_context],
    )

    answer_metric = AnswerRelevancyMetric(model=model, threshold=settings.DEEP_EVAL_THRESHOLD, include_reason=True, async_mode=False)
    faith_metric = FaithfulnessMetric(model=model, threshold=settings.DEEP_EVAL_THRESHOLD, include_reason=True, async_mode=False)
    hallucination_metric = HallucinationMetric(model=model, threshold=0.70, include_reason=True, async_mode=False)

    raw_hall_metric = _measure_metric(hallucination_metric, test_case)
    hallucination_consistency_score = float(raw_hall_metric.get("score") or 0.0)
    hallucination_risk = max(0.0, 1.0 - hallucination_consistency_score)

    results = {
        "answer_relevancy": _measure_metric(answer_metric, test_case),
        "faithfulness": _measure_metric(faith_metric, test_case),
        "hallucination": {
            **raw_hall_metric,
            "consistency_score": hallucination_consistency_score,
            "hallucination_risk": hallucination_risk,
            "threshold": settings.HALLUCINATION_RISK_THRESHOLD,
            "pass": hallucination_risk <= settings.HALLUCINATION_RISK_THRESHOLD,
        },
    }

    results["overall_pass"] = (
        results["answer_relevancy"]["pass"]
        and results["faithfulness"]["pass"]
        and results["hallucination"]["pass"]
    )
    return results
