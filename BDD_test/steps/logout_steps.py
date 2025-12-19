from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

@given("I am logged in")
def step_logged_in(context):
    context.browser = webdriver.Chrome()
    context.browser.get("http://127.0.0.1:8000/users/login/")
    time.sleep(1)

    context.browser.find_element(By.ID, "email-input").send_keys("testuser1@gmail.com")
    context.browser.find_element(By.ID, "password-input").send_keys("Password@123!!")
    context.browser.find_element(By.ID, "login-submit-btn").click()
    time.sleep(2)

    assert "profile-menu-button" in context.browser.page_source.lower(), \
        "Login failed before logout scenario."

@when("I open the profile dropdown")
def step_open_profile_dropdown(context):
    profile_btn = context.browser.find_element(By.ID, "profile-menu-button")
    profile_btn.click()
    time.sleep(1)

@when("I click the logout option")
def step_click_logout(context):
    logout_link = context.browser.find_element(
        By.CSS_SELECTOR,
        "a[href='/users/logout/']"
    )
    logout_link.click()
    time.sleep(2)

@then("I should be redirected to the landing page")
def step_redirect_landing(context):
    current_url = context.browser.current_url
    assert "127.0.0.1:8000" in current_url, "Not redirected to landing page."

@then("I should see a logout success message")
def step_logout_message(context):
    page = context.browser.page_source.lower()

    assert "logged out" in page \
        or "success" in page \
        or "logout successful" in page, \
        "Logout success message not found."

    context.browser.quit()