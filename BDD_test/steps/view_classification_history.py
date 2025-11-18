from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


@given("I am logged in for viewing classification history")
def step_logged_in(context):
    context.browser = webdriver.Chrome()
    context.browser.get("http://127.0.0.1:8000/users/login/")
    time.sleep(1)

    # Login fields
    context.browser.find_element(By.ID, "email-input").send_keys("testuser1@gmail.com")
    context.browser.find_element(By.ID, "password-input").send_keys("Password@123!!")

    # Submit
    context.browser.find_element(By.ID, "login-submit-btn").click()
    time.sleep(2)

    # Ensure login success
    assert "profile-menu-button" in context.browser.page_source.lower(), \
        "Login failed before history scenario."


@when("I click the history option")
def step_click_history(context):
    history_link = context.browser.find_element(
        By.CSS_SELECTOR,
        "a[href='/klasifikasi/history/']"
    )
    history_link.click()
    time.sleep(2)


@then("I should be redirected to the history page")
def step_redirect_history(context):
    current_url = context.browser.current_url
    assert "/klasifikasi/history/" in current_url, \
        f"Expected to be on history page, but got {current_url}"


@then("I should see the history page loaded")
def step_history_loaded(context):
    page = context.browser.page_source.lower()

    assert "history" in page or "classification" in page, \
        "History page content not found."

    context.browser.quit()