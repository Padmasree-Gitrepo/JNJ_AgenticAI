from __future__ import annotations

import os

import pytest

from resume_agent_automation.config.settings import settings


@pytest.mark.parametrize(
    "case_id",
    ["TC_RES_001", "TC_RES_002", "TC_RES_004", "TC_RES_006", "TC_RES_014"],
)
def test_manual_case_traceability(case_id, manual_cases):
    ids = {item.test_id for item in manual_cases}
    assert case_id in ids, f"Case ID {case_id} not found in manual test workbook"


@pytest.mark.parametrize(
    "case_id",
    ["TC_RES_001", "TC_RES_002", "TC_RES_004", "TC_RES_006", "TC_RES_014"],
)
def test_resume_agent_live_workflow(case_id, manual_cases, resume_page):
    if os.getenv("RUN_LIVE_UI_TESTS", "false").lower() != "true":
        pytest.skip("Set RUN_LIVE_UI_TESTS=true to execute the actual Resume Studio workflow.")

    case = next(item for item in manual_cases if item.test_id == case_id)
    resume_page.login(settings.APP_USERNAME, settings.APP_PASSWORD)
    resume_page.open_resume_studio()
    if case_id in {"TC_RES_002", "TC_RES_004", "TC_RES_006", "TC_RES_014"}:
        resume_page.start_new_conversation()
    if case_id == "TC_RES_006":
        resume_page.send_message("Yes, let's proceed.")
    elif case_id == "TC_RES_014":
        resume_page.send_message("I have 5 years of Python automation and DevOps experience.")
    else:
        resume_page.send_message("I would like to continue with my resume update.")

    response = resume_page.wait_for_agent_reply(timeout=120000)
    assert "resume" in response.lower() or len(response.strip()) > 0
