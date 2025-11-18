from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

@given("I logged in for upload file")
def step_impl(context):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-features=PasswordLeakDetection")
    options.add_argument("--disable-features=PasswordCheck")

    context.browser = webdriver.Chrome(options=options)
    context.browser.get("http://127.0.0.1:8000/users/login/")

    context.browser.find_element(By.NAME, "email").send_keys("testuser1@gmail.com")
    context.browser.find_element(By.NAME, "password").send_keys("Password@123!!")
    context.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)


@given("I navigates to the question upload page")
def step_impl(context):
    context.browser.get("http://127.0.0.1:8000/soal/")
    time.sleep(1)


@when("I selects a valid file in a supported format")
def step_impl(context):
    context.browser.find_element(By.ID, "file-input").send_keys(
        r"D:\1. Rehan\0. KULIAH\2. MATA KULIAH\SEMESTER 5\11. Pembangunan Perangkat Lunak Praktikum\Test_Behave\feature\test_files\UTS_I1_Kelompok 3 Bloomers_Data.pdf"
    )
    time.sleep(1)


@when("I selects a file with an unsupported format")
def step_impl(context):
    context.browser.find_element(By.ID, "file-input").send_keys(
        r"D:\1. Rehan\0. KULIAH\2. MATA KULIAH\SEMESTER 5\11. Pembangunan Perangkat Lunak Praktikum\Test_Behave\feature\test_files\test_png.png"
    )
    time.sleep(1)


@when("I uploads the file")
def step_impl(context):
    context.browser.find_element(By.ID, "classify-btn").click()
    time.sleep(2)


@then("the upload should be successful")
def step_impl(context):
    messages = context.browser.find_elements(By.CLASS_NAME, "bg-green-100")
    assert len(messages) > 0, "Success message not found."


@then("the upload button should remain disabled")
def step_impl(context):
    btn = context.browser.find_element(By.ID, "classify-btn")
    assert not btn.is_enabled(), "Upload button should stay disabled for invalid file."