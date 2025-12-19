Feature: View Classification Results
  As a user
  I want to view classification results
  So that I can check the analysis outcome of my uploaded questions

  Scenario: Successfully open classification results for a completed file
    Given I logged in for viewing classification results
    And I am on the homepage
    When I select a completed file
    And I click the view results button
    Then I should be redirected to the results page