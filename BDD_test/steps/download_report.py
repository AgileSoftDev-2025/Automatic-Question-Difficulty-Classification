import os
import time
from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")

def setup_browser():
    # Folder download khusus
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    return webdriver.Chrome(options=chrome_options)

@given("I am logged in for downloading classification report")
def step_logged_in(context):
    context.browser = setup_browser()
    context.browser.get("http://127.0.0.1:8000/users/login/")
    time.sleep(1)

    context.browser.find_element(By.ID, "email-input").send_keys("testuser1@gmail.com")
    context.browser.find_element(By.ID, "password-input").send_keys("Password@123!!")
    context.browser.find_element(By.ID, "login-submit-btn").click()
    time.sleep(2)

    assert "profile-menu-button" in context.browser.page_source.lower(), \
        "Login failed."

@when("I navigate to the classification history page for downloading classification report")
def step_go_to_history(context):
    history_btn = context.browser.find_element(By.LINK_TEXT, "History")
    history_btn.click()
    time.sleep(2)

    assert "klasifikasi/history" in context.browser.current_url.lower(), \
        "Did not navigate to history page."

@when("I click the download report icon")
def step_click_download(context):
    download_icon = context.browser.find_element(
        By.CSS_SELECTOR, "a[href^='/klasifikasi/download/']"
    )
    download_icon.click()
    time.sleep(3) 

@then("The report file should be downloaded successfully")
def step_verify_download(context):
    timeout = 10
    file_found = None

    for _ in range(timeout):
        files = os.listdir(DOWNLOAD_DIR)
        files = [f for f in files if not f.endswith(".crdownload")]

        if len(files) > 0:
            file_found = files[0]
            break

        time.sleep(1)

    assert file_found is not None, "No downloaded file found."

    context.browser.quit()
