from playwright.sync_api import Page, expect

from tests.ui.pages.BasePage import BasePage


class HomePage(BasePage):
    """Reference page object for a tile-based ADA-style home page."""

    PAGE_URL = "https://analytical-data-access.education.gov.uk/"
    PAGE_TITLE = "Analytical Data Access (ADA)"
    PAGE_HEADING = "Analytical Data Access (ADA)"

    PAGE_HEADING_XPATH = "//h1[@class='govuk-heading-xl']"
    TILES_NAMES_XPATH = (
        "(//h2[normalize-space(@class)="
        "'govuk-heading-m visual-vyed-box-content-leaf'])"
    )
    TILES_DESCRIPTION_XPATH = "(//p[normalize-space(@class)='govuk-body'])"

    TILE_NAMES = [
        "Find data",
        "Analyse data",
        "Request data access",
        "Get support",
        "Reports and dashboards",
        "News and updates",
    ]

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_home_page(self):
        self.navigate_to_page(self.PAGE_URL)

    def assert_home_page_heading(self):
        expect(self.page).to_have_title(self.PAGE_TITLE)
        expect(self.page.locator(self.PAGE_HEADING_XPATH)).to_have_text(
            self.PAGE_HEADING
        )

    def assert_home_page_tiles(self):
        expect(self.page.locator(self.TILES_NAMES_XPATH)).to_have_count(
            len(self.TILE_NAMES)
        )
