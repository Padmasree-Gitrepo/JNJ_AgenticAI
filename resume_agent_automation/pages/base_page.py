from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Locator, Page

from resume_agent_automation.config.settings import settings
from resume_agent_automation.utils.logger import build_logger

logger = build_logger("base_page", settings.LOGS_DIR)


class BasePage:
    def __init__(self, page: Page, base_url: str | None = None):
        self.page = page
        self.base_url = (base_url or settings.APP_URL).rstrip("/")

    def goto(self, path: str = "") -> None:
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        logger.info("Navigating to %s", url)
        self.page.goto(url, wait_until="networkidle")

    def wait_for_ready(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")

    def take_screenshot(self, name: str, folder: str = "screenshots") -> str:
        directory = Path(settings.PROJECT_ROOT) / folder
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{name}.png"
        self.page.screenshot(path=str(file_path), full_page=True)
        return str(file_path)

    def is_visible(self, locator: Locator) -> bool:
        try:
            return bool(locator.is_visible())
        except Exception:
            return False

    def find_text(self, text: str, *, exact: bool = False) -> Locator:
        return self.page.get_by_text(text, exact=exact)
