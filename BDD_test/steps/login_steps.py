from behave import given, when, then
from selenium import webdriver
import time

@given("I open the landing page for login")
def step_open_landing_page(context):
    context.browser = webdriver.Chrome()
    context.browser.get("http://127.0.0.1:8000/")
    time.sleep(1)

@when("I navigate to the login page for login")
def step_go_to_login(context):
    context.browser.find_element("css selector", "a[href='/users/login/']").click()
    time.sleep(1)

@when("I fill the login form with valid credentials")
def step_fill_valid(context):
    context.browser.find_element("id", "email-input").send_keys("testuser1@gmail.com")
    context.browser.find_element("id", "password-input").send_keys("Password@123!!")
    time.sleep(1)

@when("I fill the login form with an invalid password")
def step_fill_invalid(context):
    context.browser.find_element("id", "email-input").send_keys("testuser1@gmail.com")
    context.browser.find_element("id", "password-input").send_keys("WrongPassword999")
    time.sleep(1)

@when("I submit the login form")
def step_submit_login(context):
    context.browser.find_element("id", "login-submit-btn").click()
    time.sleep(2)

@then("I should see the dashboard or login success message")
def step_login_success(context):
    page = context.browser.page_source.lower()

    assert "dashboard" in page \
        or "welcome" in page \
        or "success" in page \
        or "logged in" in page, \
        "Login success message NOT found."

    context.browser.quit()

@then("I should see a login error message")
def step_login_error(context):
    page = context.browser.page_source.lower()

    assert "invalid" in page \
        or "wrong password" in page \
        or "error" in page, \
        "Login error message NOT found."

    context.browser.quit()
