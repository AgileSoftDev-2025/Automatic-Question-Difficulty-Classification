Feature: User Logout
  As a logged-in user
  I want to log out
  So that my session ends safely

  Scenario: Successful user logout
    Given I am logged in
    When I open the profile dropdown
    And I click the logout option
    Then I should be redirected to the landing page
    And I should see a logout success message