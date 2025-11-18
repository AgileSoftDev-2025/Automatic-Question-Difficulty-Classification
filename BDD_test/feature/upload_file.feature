Feature: Upload Question File
  As a user
  I want to upload a file
  So that the system can process it

  Scenario: Successful upload of a valid file
    Given I logged in for upload file
    And I navigates to the question upload page
    When I selects a valid file in a supported format
    And I uploads the file
    Then the upload should be successful

  Scenario: Upload fails due to invalid file format
    Given I logged in for upload file
    And I navigates to the question upload page
    When I selects a file with an unsupported format
    Then the upload button should remain disabled
