from __future__ import annotations

import os

import pytest

from integrations.deepeval_judge import build_ollama_judge, evaluate_agent_response


@pytest.mark.parametrize(
    "input_text, actual_output, context",
    [
        (
            "Update my resume summary to emphasize Python automation experience.",
            "Updated the summary to emphasize Python automation and quality engineering experience.",
            "The candidate has Python automation experience and quality engineering work. The summary should reflect that experience accurately.",
        ),
        (
            "Add the skills section for Python, Playwright, and pytest.",
            "The skills section now includes Python, Playwright, and pytest.",
            "Skills section should include Python, Playwright, and pytest if the user asks for it.",
        ),
    ],
)
def test_deepeval_metrics_equivalent(input_text, actual_output, context):
    if not os.getenv("USE_DEEPEVAL", "false").lower() == "true":
        pytest.skip("Set USE_DEEPEVAL=true to execute DeepEval metrics against a local Ollama judge.")

    judge = build_ollama_judge()
    result = evaluate_agent_response(input_text=input_text, actual_output=actual_output, reference_context=context, judge_model=judge)
    assert "answer_relevancy" in result
    assert "faithfulness" in result
    assert "hallucination" in result
