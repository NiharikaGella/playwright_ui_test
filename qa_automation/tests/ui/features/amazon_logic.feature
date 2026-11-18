@regression @smoke
Feature: Amazon search

    Scenario: Search for office chairs
        Given User navigates to Amazon
        When User searches for office chairs
        Then Amazon search results should be displayed
        When User opens the first search result
        And User adds the product to the cart
        Then The cart should contain one item