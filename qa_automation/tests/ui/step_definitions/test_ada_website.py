from pytest_bdd import given, scenario, then

from tests.ui.pages.HomePage import HomePage


@scenario("../features/ada_homepage.feature", "Verify the ADA home page heading and tiles")
def test_ada_homepage():
    pass


def home_page(page):
    return HomePage(page)


@given("the user navigates to the ADA home page")
def navigate_to_ada_home_page(page):
    home_page(page).navigate_to_home_page()


@then("the ADA home page heading should be displayed")
def verify_ada_home_page_heading(page):
    home_page(page).assert_home_page_heading()


@then("the ADA home page tiles should be displayed")
def verify_ada_home_page_tiles(page):
    home_page(page).assert_home_page_tiles()
