from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class ManualTestCase:
    test_id: str
    description: str
    preconditions: str
    test_steps: str
    expected_result: str
    actual_result: str
    status: str
    automation_candidate: str
    priority: str

    @property
    def automation_priority(self) -> str:
        return self.priority or "Medium"


def load_manual_test_cases(file_path: str | Path) -> list[ManualTestCase]:
    workbook = load_workbook(filename=file_path, read_only=True, data_only=True)
    worksheet = workbook["Manual Test Cases"]

    rows = list(worksheet.iter_rows(values_only=True))
    if not rows or len(rows) < 2:
        return []

    headers = [str(cell or "").strip() for cell in rows[0]]
    required = [
        "Test Case ID",
        "Test Case Description",
        "Precondition",
        "Test Steps",
        "Expected Result",
        "Actual Result",
        "Status",
        "Automation Candidate",
        "Priority",
    ]

    missing = [header for header in required if header not in headers]
    if missing:
        raise ValueError(f"Missing required columns in manual test cases: {missing}")

    cases: list[ManualTestCase] = []
    for row in rows[1:]:
        row_map = {header: (row[idx] if idx < len(row) else "") for idx, header in enumerate(headers)}
        if not any(str(value or "").strip() for value in row_map.values()):
            continue

        cases.append(
            ManualTestCase(
                test_id=str(row_map.get("Test Case ID", "")).strip(),
                description=str(row_map.get("Test Case Description", "")).strip(),
                preconditions=str(row_map.get("Precondition", "")).strip(),
                test_steps=str(row_map.get("Test Steps", "")).strip(),
                expected_result=str(row_map.get("Expected Result", "")).strip(),
                actual_result=str(row_map.get("Actual Result", "")).strip(),
                status=str(row_map.get("Status", "")).strip() or "Not Run",
                automation_candidate=str(row_map.get("Automation Candidate", "")).strip() or "No",
                priority=str(row_map.get("Priority", "")).strip() or "Medium",
            )
        )
    return cases
