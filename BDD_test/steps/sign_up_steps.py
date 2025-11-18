from behave import given, when, then
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.common.exceptions import NoAlertPresentException

@given("I open the landing page")
def step_open_landing_page(context):
    context.browser = webdriver.Chrome()
    context.browser.get("http://127.0.0.1:8000/")
    time.sleep(1)

@when("I navigate to the login page")
def step_go_to_login(context):
    context.browser.find_element("css selector", "a[href='/users/login/']").click()
    time.sleep(1)

@when("I choose to go to the sign up page")
def step_go_to_signup(context):
    context.browser.find_element("css selector", "a[href='/users/register/']").click()
    time.sleep(1)

@when("I fill the sign up form with valid data")
def step_fill_form(context):
    context.browser.find_element("id", "username-input").send_keys("testuser1")
    context.browser.find_element("id", "email-input").send_keys("testuser1@gmail.com")
    context.browser.find_element("id", "password-input").send_keys("Password@123!!")
    context.browser.find_element("id", "confirm-password-input").send_keys("Password@123!!")
    context.browser.find_element("id", "terms-checkbox").click()
    time.sleep(1)

@when("I fill the form with mismatched passwords")
def step_fill_mismatch(context):
    context.browser.find_element("id", "username-input").send_keys("wrongtest3")
    context.browser.find_element("id", "email-input").send_keys("wrongtest3@gmail.com")
    context.browser.find_element("id", "password-input").send_keys("Password123!!")
    context.browser.find_element("id", "confirm-password-input").send_keys("WrongPassword!!")
    context.browser.find_element("id", "terms-checkbox").click()
    time.sleep(1)

@when("I fill the sign up form without accepting terms")
def step_no_terms(context):
    context.browser.find_element("id", "username-input").send_keys("notermsuser3")
    context.browser.find_element("id", "email-input").send_keys("noterms3@gmail.com")
    context.browser.find_element("id", "password-input").send_keys("Password123!!")
    context.browser.find_element("id", "confirm-password-input").send_keys("Password123!!")
    time.sleep(1)

@when("I submit the form")
def step_submit(context):
    context.browser.find_element("id", "register-submit-btn").click()
    time.sleep(2)

@then("I should see a success message")
def step_success_message(context):
    page = context.browser.page_source.lower()

    assert "success" in page \
        or "account created" in page \
        or "please login" in page \
        or "registration" in page, \
        "Success message not found."
    
    context.browser.quit()

@then("I should see an error message")
def step_error(context):
    try:
        alert = context.browser.switch_to.alert
        text = alert.text.lower()
        assert "please" in text or "error" in text
        alert.accept()
    except NoAlertPresentException:
        assert "error" in context.browser.page_source.lower()
    finally:
        context.browser.quit()

@then("I should see a password mismatch error")
def step_pw_error(context):
    assert "password" in context.browser.page_source.lower() \
        and "match" in context.browser.page_source.lower()
    context.browser.quit()

@then("I should see a terms-of-service warning")
def step_terms(context):
    try:
        alert = context.browser.switch_to.alert
        text = alert.text.lower()
        assert "terms" in text or "policy" in text
        alert.accept()
    except NoAlertPresentException:
        assert "terms" in context.browser.page_source.lower()
    finally:
        context.browser.quit()