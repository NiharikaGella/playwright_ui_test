from pytest_bdd import given, scenario, then, when

from tests.ui.pages.AmazonPage import AmazonPage


@scenario("../features/amazon_logic.feature", "Search for office chairs")
def test_amazon_search():
    pass


def amazon_page(page):
    return AmazonPage(page)


@given("User navigates to Amazon")
def navigate_to_amazon(page):
    amazon_page(page).navigate_to_amazon()


@when("User searches for office chairs")
def search_for_office_chairs(page):
    amazon_page(page).search_for("office chairs")


@then("Amazon search results should be displayed")
def verify_amazon_search_results(page):
    amazon_page(page).assert_search_results_displayed()


@when("User opens the first search result")
def open_first_search_result(page):
    amazon_page(page).open_first_result()


@when("User adds the product to the cart")
def add_product_to_cart(page):
    amazon_page(page).add_product_to_cart()


@then("The cart should contain one item")
def verify_cart_contains_item(page):
    amazon_page(page).assert_cart_contains_item()
