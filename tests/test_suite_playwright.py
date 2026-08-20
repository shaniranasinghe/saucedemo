import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()

def login(page, username, password):
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", username)
    page.fill("#password", password)
    page.click("#login-button")
    page.wait_for_url("https://www.saucedemo.com/inventory.html")

def add_to_cart(page, product_selector):
    page.click(product_selector)

def remove_from_cart(page, product_selector):
    page.click(product_selector)

def proceed_to_checkout(page):
    page.click(".shopping_cart_link")
    page.click("#checkout")

def fill_checkout_info(page, first_name, last_name, postal_code):
    page.fill("#first-name", first_name)
    page.fill("#last-name", last_name)
    page.fill("#postal-code", postal_code)
    page.click("#continue")

def test_successfully_remove_product_from_cart(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    remove_from_cart(page, "#remove-sauce-labs-backpack")

    assert not page.is_visible(".shopping_cart_badge")
    page.close()

def test_attempt_to_remove_product_not_in_cart(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    page.click(".shopping_cart_link")
    
    # TODO: selector for 'remove_backpack' not crawled yet
    page.close()

def test_successfully_add_product_to_cart(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")

    assert page.is_visible(".shopping_cart_badge")
    page.close()

def test_attempt_to_add_product_when_already_in_cart(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    
    assert page.is_visible(".shopping_cart_badge")
    page.close()

def test_successful_login_with_valid_credentials(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    assert page.url == "https://www.saucedemo.com/inventory.html"
    assert page.is_visible("#inventory_container")
    page.close()

def test_failed_login_with_invalid_credentials(browser):
    page = browser.new_page()
    page.goto("https://www.saucedemo.com")
    
    page.fill("#user-name", "wrong_user")
    page.fill("#password", "wrong_pass")
    page.click("#login-button")
    
    assert page.is_visible("text=Epic sadface: Username and password do not match any user in this service")
    assert page.url == "https://www.saucedemo.com/"
    page.close()

def test_successful_checkout_with_all_details(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    proceed_to_checkout(page)
    fill_checkout_info(page, "John", "Doe", "12345")
    
    assert page.is_visible(".complete-header")
    assert page.inner_text(".complete-header") == "Thank you for your order!"
    page.close()

def test_checkout_with_missing_postal_code(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    proceed_to_checkout(page)
    fill_checkout_info(page, "John", "Doe", "")
    
    assert page.is_visible("text=Error: Postal Code is required")
    assert page.url == "https://www.saucedemo.com/checkout-step-one.html"
    page.close()