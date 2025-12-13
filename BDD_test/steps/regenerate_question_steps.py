from behave import given, when, then
from selenium.webdriver.common.by import By
import time


@given("I am on the results page of a completed file")
def step_impl(context):
    # Ambil file pertama yang punya tombol view results
    context.browser.get("http://127.0.0.1:8000/soal/")
    time.sleep(2)

    rows = context.browser.find_elements(By.CSS_SELECTOR, "tbody tr")

    for row in rows:
        button = row.find_elements(By.CSS_SELECTOR, "a[title='View Classification Results']")
        if button:
            button[0].click()
            time.sleep(3)
            return

    assert False, "No completed file found."


@when("I click the regenerate button for a question")
def step_impl(context):
    regen_buttons = context.browser.find_elements(By.CSS_SELECTOR, ".regenerate-btn")

    assert regen_buttons, "No regenerate button found."

    context.regen_button = regen_buttons[0]
    context.regen_button.click()
    time.sleep(2)


@when("I select a new Bloom level in the regenerate modal")
def step_impl(context):
    # Target select: <select id="modal-target-level">
    target_select = context.browser.find_element(By.ID, "modal-target-level")

    # Ganti dari default C3 → C4 misalnya
    for option in target_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value") == "C2":   # kamu bisa ganti target level
            option.click()
            break

    time.sleep(1)


@when("I confirm the regeneration")
def step_impl(context):
    confirm_btn = context.browser.find_element(By.ID, "confirm-regenerate-btn")
    confirm_btn.click()

    # regenerate proses lama: kasih waktu 10–20 detik
    time.sleep(12)


@then("I should see a regenerated question appear")
def step_impl(context):
    regenerated_cards = context.browser.find_elements(
        By.CSS_SELECTOR,
        "article.question-card[data-regenerated='true']"
    )

    assert regenerated_cards, "No regenerated question appears."
    context.regenerated_card = regenerated_cards[0]
    time.sleep(1)


@then("the regenerated question should have a generated label")
def step_impl(context):
    labels = context.regenerated_card.find_elements(By.CSS_SELECTOR, "h4 span")

    found = any("(Regenerated)" in el.text for el in labels)
    assert found, "Generated label not found."

