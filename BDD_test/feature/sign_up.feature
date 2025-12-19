Feature: User Sign Up
    Feature: User Sign Up
  As a new user
  I want to create an account
  So that I can log into the system

  Scenario: Successful user registration
    Given I open the landing page
    When I navigate to the login page
    And I choose to go to the sign up page
    And I fill the sign up form with valid data
    And I submit the form
    Then I should see a success message
  
  Scenario: Registration fails with empty fields
    Given I open the landing page
    When I navigate to the login page
    And I choose to go to the sign up page
    And I submit the form
    Then I should see an error message

  Scenario: Registration fails with mismatched passwords
    Given I open the landing page
    When I navigate to the login page
    And I choose to go to the sign up page
    And I fill the form with mismatched passwords
    And I submit the form
    Then I should see a password mismatch error

  Scenario: Registration fails if terms are not checked
    Given I open the landing page
    When I navigate to the login page
    And I choose to go to the sign up page
    And I fill the sign up form without accepting terms
    And I submit the form
    Then I should see a terms-of-service warning