from __future__ import annotations

import os
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from resume_agent_automation.config.settings import settings
from resume_agent_automation.pages.resume_agent_page import ResumeAgentPage
from resume_agent_automation.utils.excel_reader import load_manual_test_cases


@pytest.fixture(scope="session")
def manual_cases():
    path = settings.MANUAL_CASE_FILE
    if not path.exists():
        pytest.skip(f"Manual case workbook not found: {path}")
    return load_manual_test_cases(path)


@pytest.fixture(scope="session")
def selected_case_ids():
    return ["TC_RES_001", "TC_RES_002", "TC_RES_004", "TC_RES_006", "TC_RES_014"]


@pytest.fixture(scope="session")
def browser_context():
    if os.getenv("RUN_LIVE_UI_TESTS", "false").lower() != "true":
        pytest.skip("Live UI automation is disabled. Set RUN_LIVE_UI_TESTS=true to run against the application.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
        page = browser.new_page()
        yield ResumeAgentPage(page, settings.APP_URL)
        browser.close()


@pytest.fixture(scope="session")
def resume_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
        page = browser.new_page()
        yield ResumeAgentPage(page, settings.APP_URL)
        browser.close()
