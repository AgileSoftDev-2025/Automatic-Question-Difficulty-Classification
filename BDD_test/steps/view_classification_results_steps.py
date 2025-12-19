from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

@given("I logged in for viewing classification results")
def step_impl(context):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-features=PasswordLeakDetection")
    options.add_argument("--disable-features=PasswordCheck")

    context.browser = webdriver.Chrome(options=options)
    context.browser.get("http://127.0.0.1:8000/users/login/")

    context.browser.find_element(By.NAME, "email").send_keys("testuser1@gmail.com")
    context.browser.find_element(By.NAME, "password").send_keys("Password@123!!")
    context.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)


@given("I am on the homepage")
def step_impl(context):
    context.browser.get("http://127.0.0.1:8000/soal/")
    time.sleep(3)


@when("I select a completed file")
def step_impl(context):
    rows = context.browser.find_elements(By.CSS_SELECTOR, "tbody tr")

    for row in rows:
        eye_buttons = row.find_elements(By.CSS_SELECTOR, "a[title='View Classification Results']")

        if eye_buttons:
            context.selected_row = row
            context.view_button = eye_buttons[0]
            return

    assert False, "No row with a view results (eye) icon found."


@when("I click the view results button")
def step_impl(context):
    context.view_button.click()
    time.sleep(3)


@then("I should be redirected to the results page")
def step_impl(context):
    assert "/klasifikasi/hasil/" in context.browser.current_url
    time.sleep(3)