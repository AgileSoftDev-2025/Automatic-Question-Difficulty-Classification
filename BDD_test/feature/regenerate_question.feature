Feature: Regenerate Question
  As a user
  I want to regenerate a question to a different Bloom level
  So that I can obtain a transformed version of the question

  Scenario: Successfully regenerate a question to a new Bloom level
    Given I logged in for viewing classification results
    And I am on the results page of a completed file
    When I click the regenerate button for a question
    And I select a new Bloom level in the regenerate modal
    And I confirm the regeneration
    Then I should see a regenerated question appear
    And the regenerated question should have a generated label