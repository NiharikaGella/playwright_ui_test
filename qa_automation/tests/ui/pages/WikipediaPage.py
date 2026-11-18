from playwright.sync_api import Page, expect


class WikipediaPage:
    URL = "https://www.wikipedia.org"
    SEARCH_INPUT = "#searchInput"
    SEARCH_BUTTON = "button[type='submit']"
    TITLE = "#firstHeading"
    SUMMARY_SELECTOR = "#mw-content-text > div.mw-parser-output > p"
    SECTION_SELECTOR = "#mw-content-text h2"
    REFERENCE_SELECTOR = "#mw-content-text sup.reference"

    def __init__(self, page: Page):
        self.page = page
        self.timeout = 60000

    def navigate_to_wikipedia(self):
        self.page.set_default_navigation_timeout(self.timeout)
        self.page.goto(self.URL, wait_until="domcontentloaded")
        expect(self.page.locator(self.SEARCH_INPUT)).to_be_visible(timeout=self.timeout)

    def search_for(self, topic: str):
        search_box = self.page.locator(self.SEARCH_INPUT)
        search_box.fill(topic)
        search_box.press("Enter")
        self.page.wait_for_load_state("domcontentloaded", timeout=self.timeout)
        self.page.locator(self.TITLE).wait_for(state="visible", timeout=self.timeout)

    def assert_article_loaded(self):
        title = self.page.locator(self.TITLE).first.text_content() or ""
        assert title.strip(), "Wikipedia article title was not visible."
        assert "Python" in title, f"Expected article title to mention Python but got: {title}"

    def extract_summary(self):
        paragraphs = self.page.locator(self.SUMMARY_SELECTOR).all()
        for paragraph in paragraphs:
            text = paragraph.text_content() or ""
            clean_text = " ".join(text.split())
            if clean_text and len(clean_text) > 80:
                return clean_text
        raise AssertionError("No valid Wikipedia summary paragraph was found.")

    def assert_has_reference_or_section(self):
        sections = self.page.locator(self.SECTION_SELECTOR).count()
        references = self.page.locator(self.REFERENCE_SELECTOR).count()
        assert sections > 0 or references > 0, (
            f"Expected at least one section or reference on the page, but found "
            f"sections={sections}, references={references}."
        )
