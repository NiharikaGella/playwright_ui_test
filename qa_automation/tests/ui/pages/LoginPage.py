from playwright.sync_api import Page, expect

from tests.ui.pages.BasePage import BasePage


class LoginPage(BasePage):
    """Reference page object for a Microsoft-style username/password login."""

    USERNAME_INPUT = 'input[type="email"]'
    PASSWORD_INPUT = 'input[type="password"]'
    NEXT_OR_SIGN_IN_BUTTON = 'input[type="submit"]'
    STAY_SIGNED_IN_BUTTON = 'input[value="Yes"]'

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_login_page(self, url: str):
        self.navigate_to_page(url)
        expect(self.page.locator(self.USERNAME_INPUT)).to_be_visible()

    def enter_username(self, username: str):
        self.page.locator(self.USERNAME_INPUT).fill(username)

    def click_next_or_sign_in(self):
        self.page.locator(self.NEXT_OR_SIGN_IN_BUTTON).click()

    def enter_password(self, password: str):
        expect(self.page.locator(self.PASSWORD_INPUT)).to_be_visible()
        self.page.locator(self.PASSWORD_INPUT).fill(password)

    def complete_login(self, url: str, username: str, password: str):
        self.navigate_to_login_page(url)
        self.enter_username(username)
        self.click_next_or_sign_in()
        self.enter_password(password)
        self.click_next_or_sign_in()

        stay_signed_in = self.page.locator(self.STAY_SIGNED_IN_BUTTON)
        if stay_signed_in.is_visible():
            stay_signed_in.click()

        self.page.wait_for_load_state("networkidle")
