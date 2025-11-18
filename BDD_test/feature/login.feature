Feature: User Login
  As a registered user
  I want to log into my account
  So that I can access the system

  Scenario: Successful login
    Given I open the landing page for login
    When I navigate to the login page for login
    And I fill the login form with valid credentials
    And I submit the login form
    Then I should see the dashboard or login success message

  Scenario: Login fails with wrong password
    Given I open the landing page for login
    When I navigate to the login page for login
    And I fill the login form with an invalid password
    And I submit the login form
    Then I should see a login error message
