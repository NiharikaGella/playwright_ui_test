import re

from playwright.sync_api import Page, expect


class AmazonPage:
    URL = "https://www.amazon.com"
    SEARCH_INPUT = "#twotabsearchtextbox"
    SEARCH_RESULTS = "div[data-component-type='s-search-result']"
    ADD_TO_CART_BUTTON = "#add-to-cart-button"
    CART_COUNT = "#nav-cart-count"

    def __init__(self, page: Page):
        self.page = page
        self.timeout = 60000

    def navigate_to_amazon(self):
        self.page.set_default_navigation_timeout(self.timeout)
        self.page.goto(self.URL, wait_until="domcontentloaded")
        expect(self.page.locator(self.SEARCH_INPUT)).to_be_visible()

    def search_for(self, search_text: str):
        search_box = self.page.locator(self.SEARCH_INPUT)
        search_box.fill(search_text)
        search_box.press("Enter")

    def assert_search_results_displayed(self):
        expect(self.page).to_have_url(
            re.compile(
                r".*(?:[?&]k=office\+chairs|field-keywords=office(?:\+|%20)chairs).*"
            )
        )
        expect(self.page.locator(self.SEARCH_RESULTS).first).to_be_visible()

    def open_first_result(self):
        first_result = self.page.locator(self.SEARCH_RESULTS).first
        expect(first_result).to_be_visible(timeout=self.timeout)
        result_link = first_result.locator("a[href*='/dp/']").first
        expect(result_link).to_be_visible(timeout=self.timeout)
        result_link.click()
        self.page.wait_for_load_state("domcontentloaded", timeout=self.timeout)
        expect(self.add_to_cart_button()).to_be_visible(timeout=self.timeout)

    def add_to_cart_button(self):
        return self.page.get_by_role(
            "button", name=re.compile(r"^Add to cart", re.IGNORECASE)
        ).first

    def add_product_to_cart(self):
        add_to_cart = self.add_to_cart_button()
        expect(add_to_cart).to_be_visible(timeout=self.timeout)
        add_to_cart.click()
        expect(self.page.locator(self.CART_COUNT)).to_have_text(
            "1", timeout=self.timeout
        )

    def assert_cart_contains_item(self):
        expect(self.page.locator(self.CART_COUNT)).to_have_text(
            "1", timeout=self.timeout
        )
