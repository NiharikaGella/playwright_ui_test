@regression @smoke
Feature: Wikipedia search

Scenario: Search for Python and validate the article
    Given User opens the Wikipedia homepage
    When User searches for "Python"
    Then Search results page should show the article title
