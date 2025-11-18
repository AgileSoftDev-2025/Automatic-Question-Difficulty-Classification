Feature: View Classification History
  As a user
  I want to open the classification history page
  So that I can review previous classification results

  Scenario: Successfully open history page
    Given I am logged in for viewing classification history
    When I click the history option
    Then I should be redirected to the history page
    And I should see the history page loaded