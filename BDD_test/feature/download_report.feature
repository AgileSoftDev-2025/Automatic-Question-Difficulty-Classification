Feature: Download Classification Report
  As a user
  I want to download the classification report
  So that I can save the result for documentation

  Scenario: Successfully download a classification report
    Given I am logged in for downloading classification report
    When I navigate to the classification history page for downloading classification report
    And I click the download report icon
    Then The report file should be downloaded successfully
