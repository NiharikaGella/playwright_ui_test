from pytest_bdd import given, scenario, then, when

from tests.ui.pages.WikipediaPage import WikipediaPage


@scenario("../features/wikipedia_search.feature", "Search for Python and validate the article")
def test_wikipedia_search():
    pass


def wikipedia_page(page):
    return WikipediaPage(page)


@given("User opens the Wikipedia homepage")
def open_wikipedia_homepage(page):
    wikipedia_page(page).navigate_to_wikipedia()


@when('User searches for "Python"')
def search_for_python(page):
    wikipedia_page(page).search_for("Python")


@then("Search results page should show the article title")
def verify_article_title(page):
    wikipedia_page(page).assert_article_loaded()
