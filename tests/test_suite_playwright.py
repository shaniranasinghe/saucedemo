import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="function")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()

def login(page):
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    assert page.url.endswith("/inventory.html")

def add_to_cart(page, add_selector):
    page.click(add_selector)

def remove_from_cart(page, remove_selector):
    page.click(remove_selector)

def test_successfully_remove_product_from_cart(browser_context):
    page = browser_context.new_page()
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    remove_from_cart(page, "#remove-sauce-labs-backpack")
    assert not page.locator(".shopping_cart_badge").is_visible()
    page.close()

def test_attempt_to_remove_a_product_not_in_cart(browser_context):
    page = browser_context.new_page()
    login(page)
    # Try removing before adding, expected to have no items in cart
    if page.locator("#remove-sauce-labs-backpack").is_visible():
        remove_from_cart(page, "#remove-sauce-labs-backpack")
    assert not page.locator(".shopping_cart_badge").is_visible()
    page.close()

def test_successfully_add_product_to_cart(browser_context):
    page = browser_context.new_page()
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    assert page.locator(".shopping_cart_badge").is_visible()
    assert page.locator(".shopping_cart_badge").inner_text() == "1"
    page.close()

def test_verify_cart_badge_is_not_displayed_when_no_products_added(browser_context):
    page = browser_context.new_page()
    page.goto("https://www.saucedemo.com")
    assert not page.locator(".shopping_cart_badge").is_visible()
    page.close()

def test_successful_checkout_with_all_details(browser_context):
    page = browser_context.new_page()
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "")
    page.click("#continue")
    assert page.url.endswith("/checkout-step-two.html")
    page.click("#finish")
    assert page.locator(".complete-header").inner_text() == "Thank you for your order!"
    page.close()

def test_checkout_with_missing_postal_code(browser_context):
    page = browser_context.new_page()
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "")
    page.click("#continue")
    assert page.locator(".error-message-container").inner_text() == "Error: Postal Code is required"
    assert page.url.endswith("/checkout-step-one.html")
    page.close()

def test_successful_login_with_valid_credentials(browser_context):
    page = browser_context.new_page()
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    assert page.url.endswith("/inventory.html")
    assert page.locator("#inventory_container").is_visible()
    page.close()

def test_failed_login_with_invalid_credentials(browser_context):
    page = browser_context.new_page()
    page.goto("https://www.saucedemo.com/")
    page.fill("#user-name", "wrong_user")
    page.fill("#password", "wrong_pass")
    page.click("#login-button")
    assert page.locator(".error-message-container").inner_text() == "Epic sadface: Username and password do not match any user in this service"
    assert page.url.endswith("/index.html")
    page.close()