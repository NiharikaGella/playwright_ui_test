import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.append(str(Path(__file__).resolve().parent / "qa_automation"))

from tests.ui.pages.LoginPage import LoginPage
import utils.filepaths as filepaths
from tests.ui.pages.BasePage import BasePage


LOGIN_URL = os.getenv(
    "LOGIN_URL",
    "https://analytical-data-access.education.gov.uk/"
)
USERNAME = os.getenv("WEBTEST_USERNAME") or os.getenv("webtestUser")
PASSWORD = os.getenv("WEBTEST_PASSWORD") or os.getenv("webtestUserPassword")


def perform_login_and_save_state():
    if not USERNAME or not PASSWORD:
        raise RuntimeError(
            "Set WEBTEST_USERNAME and WEBTEST_PASSWORD before running login_setup.py"
        )

    state_file = Path(filepaths.get_ui_storage_state_file_path())
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser_info = BasePage.get_browser()
        browser = getattr(playwright, browser_info["browser"]).launch(
            headless=os.getenv("HEADLESS", "true").lower() != "false",
            slow_mo=50,
        )
        context = browser.new_context()
        page = context.new_page()

        LoginPage(page).complete_login(LOGIN_URL, USERNAME, PASSWORD)
        context.storage_state(path=str(state_file))

        context.close()
        browser.close()
        print(f"Login state captured and saved to {state_file}")


if __name__ == "__main__":
    perform_login_and_save_state()
