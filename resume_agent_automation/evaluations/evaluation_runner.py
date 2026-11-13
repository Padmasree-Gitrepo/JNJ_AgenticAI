from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from resume_agent_automation.config.settings import settings
from integrations.deepeval_judge import evaluate_agent_response
from resume_agent_automation.utils.excel_reader import ManualTestCase
from resume_agent_automation.utils.logger import build_logger

logger = build_logger("evaluation_runner", settings.LOGS_DIR)


class EvaluationRunner:
    def __init__(self, transcripts_dir: str | Path | None = None, reports_dir: str | Path | None = None):
        self.transcripts_dir = Path(transcripts_dir or settings.TRANSCRIPTS_DIR)
        self.reports_dir = Path(reports_dir or settings.REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run_case(self, case: ManualTestCase, actual_response: str, context: str, judge_model=None) -> dict:
        result = evaluate_agent_response(
            input_text=f"{case.description}\n\n{case.test_steps}",
            actual_output=actual_response,
            reference_context=context,
            judge_model=judge_model,
        )

        report = {
            "test_id": case.test_id,
            "scenario": case.description,
            "automation_status": case.automation_candidate,
            "status": case.status,
            "answer_relevancy_score": result["answer_relevancy"].get("score"),
            "faithfulness_score": result["faithfulness"].get("score"),
            "hallucination_consistency_score": result["hallucination"].get("consistency_score"),
            "hallucination_risk": result["hallucination"].get("hallucination_risk"),
            "configured_thresholds": {
                "answer_relevancy": settings.DEEP_EVAL_THRESHOLD,
                "faithfulness": settings.DEEP_EVAL_THRESHOLD,
                "hallucination_risk": settings.HALLUCINATION_RISK_THRESHOLD,
            },
            "overall_pass": result["overall_pass"],
            "details": result,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        return report

    def write_csv(self, rows: list[dict], file_name: str = "evaluation_summary.csv") -> Path:
        file_path = self.reports_dir / file_name
        fieldnames = [
            "test_id",
            "scenario",
            "automation_status",
            "status",
            "answer_relevancy_score",
            "faithfulness_score",
            "hallucination_consistency_score",
            "hallucination_risk",
            "overall_pass",
            "timestamp_utc",
        ]
        with file_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key, "") for key in fieldnames})
        return file_path

    def write_html(self, rows: list[dict], file_name: str = "evaluation_report.html") -> Path:
        file_path = self.reports_dir / file_name
        rows_html = "\n".join(
            f"<tr><td>{row.get('test_id','')}</td><td>{row.get('scenario','')}</td><td>{row.get('overall_pass','')}</td><td>{row.get('hallucination_risk','')}</td></tr>"
            for row in rows
        )
        html = f"""
        <html><head><title>Resume Agent Evaluation Report</title></head>
        <body>
        <h1>Resume Agent Evaluation Report</h1>
        <table border='1'>
            <thead><tr><th>Test ID</th><th>Scenario</th><th>Pass</th><th>Hallucination Risk</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        </body></html>
        """
        file_path.write_text(html, encoding="utf-8")
        return file_path
