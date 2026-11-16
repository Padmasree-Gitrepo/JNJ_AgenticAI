from __future__ import annotations

import re

from playwright.sync_api import Page

from resume_agent_automation.config.settings import settings
from resume_agent_automation.pages.base_page import BasePage
from resume_agent_automation.utils.logger import build_logger

logger = build_logger("resume_agent_page", settings.LOGS_DIR)


class ResumeAgentPage(BasePage):
    def __init__(self, page: Page, base_url: str | None = None):
        super().__init__(page, base_url)

    def login(self, username: str | None = None, password: str | None = None) -> None:
        username = username or settings.APP_USERNAME
        password = password or settings.APP_PASSWORD
        if not username or not password:
            raise RuntimeError("APP_USERNAME and APP_PASSWORD must be set in the environment or .env file before running live UI tests.")

        self.goto()

        sign_in_entry = self.page.get_by_role("button", name="Sign In", exact=True)
        sign_in_entry.wait_for(state="visible", timeout=settings.PLAYWRIGHT_TIMEOUT)
        sign_in_entry.click()
        self.page.wait_for_url("**/login**", wait_until="domcontentloaded", timeout=settings.PLAYWRIGHT_TIMEOUT)

        username_field = self.page.locator('input[name="username"]:visible')
        username_field.wait_for(state="visible", timeout=settings.PLAYWRIGHT_TIMEOUT)
        if username_field.count() != 1:
            raise RuntimeError(f"Expected one visible username field, found {username_field.count()}.")
        username_field.fill(username)

        password_field = self.page.locator('input[placeholder="Password"]:visible')
        password_field.wait_for(state="visible", timeout=settings.PLAYWRIGHT_TIMEOUT)
        if password_field.count() != 1:
            raise RuntimeError(f"Expected one visible password field, found {password_field.count()}.")
        password_field.fill(password)

        self.page.get_by_role("button", name="Sign in", exact=False).click()
        self.page.wait_for_load_state("networkidle")

    def open_resume_studio(self) -> None:
        candidates = [
            self.page.get_by_role("button", name=re.compile(r"resume", re.I)),
            self.page.get_by_text("Resume Studio", exact=False),
            self.page.get_by_text("Resume Agent", exact=False),
            self.page.locator("button:has-text('Resume')"),
            self.page.locator("a:has-text('Resume')"),
        ]
        for locator in candidates:
            try:
                if locator.count() > 0 and locator.first.is_visible():
                    locator.first.click()
                    return
            except Exception:
                continue

        raise RuntimeError(
            "No Resume Studio / Resume Agent entry point was found in the current page. "
            "The live app does not expose the expected UI, so the workflow must be re-validated against the actual resume-agent page."
        )

    def start_new_conversation(self) -> None:
        locator = self.page.get_by_role("button", name=re.compile(r"start new conversation|new conversation", re.I))
        if locator.count() > 0:
            locator.first.click()
            return
        raise RuntimeError("Start new conversation control not found in Resume Studio.")

    def send_message(self, text: str) -> None:
        box = self.page.locator("textarea, input[type='text']").last
        if box.count() == 0:
            raise RuntimeError("No chat input control found in the active Resume Studio view.")
        box.fill(text)
        self.page.get_by_role("button", name=re.compile(r"send|submit", re.I)).first.click()

    def wait_for_agent_reply(self, timeout: float = 60000) -> str:
        self.page.wait_for_function(
            "() => { const msg = document.body.innerText; return msg.length > 0; }",
            timeout=int(timeout),
        )
        return self.page.locator("body").inner_text()
