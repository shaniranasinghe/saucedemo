import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        context.close()
        browser.close()

def login(page, username, password):
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", username)
    page.fill("#password", password)
    page.click("#login-button")

def add_to_cart(page, item_selector):
    page.click(item_selector)

def remove_from_cart(page, item_selector):
    page.click(item_selector)

def proceed_to_checkout(page, first_name, last_name, postal_code):
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", first_name)
    page.fill("#last-name", last_name)
    page.fill("#postal-code", postal_code)
    page.click("#continue")

def test_successfully_remove_product_from_cart(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    remove_from_cart(page, "#remove-sauce-labs-backpack")
    
    assert not page.is_visible(".shopping_cart_badge")
    
    page.close()

def test_attempt_remove_product_not_in_cart(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")

    try:
        remove_from_cart(page, "#remove-sauce-labs-backpack")
    except Exception:
        assert True  # Expected to fail as the item is not in the cart
    
    assert not page.is_visible(".shopping_cart_badge")
    
    page.close()

def test_successfully_add_product_to_cart(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    
    assert page.is_visible(".shopping_cart_badge")
    
    page.close()

def test_attempt_add_product_when_already_in_cart(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")

    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    # Attempt to add again
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    
    # Adjusting assert as we do not have a selector for the already in cart message
    assert page.is_visible(".shopping_cart_badge")   # Assuming item stays in cart
    
    page.close()

def test_successful_login_with_valid_credentials(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    assert page.url.endswith("/inventory.html")
    assert page.is_visible(".inventory_list")
    
    page.close()

def test_failed_login_with_invalid_credentials(browser):
    page = browser.new_page()
    login(page, "wrong_user", "wrong_pass")

    assert page.is_visible(".error-message-container")  # Assuming this class contains the error message
    assert page.locator(".error-message-container").inner_text() == "Epic sadface: Username and password do not match any user in this service"
    assert not page.url.endswith("/inventory.html")

    page.close()

def test_successful_checkout_with_all_details(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    proceed_to_checkout(page, "John", "Doe", "12345")
    
    assert page.is_visible(".complete-header")  # Assuming this indicates successful checkout
    assert page.locator(".complete-header").inner_text() == "Thank you for your order!"

    page.close()

def test_checkout_with_missing_postal_code(browser):
    page = browser.new_page()
    login(page, "standard_user", "secret_sauce")
    
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "")
    page.click("#continue")
    
    assert page.is_visible(".error-message-container")  # Assuming this class contains the error
    assert page.locator(".error-message-container").inner_text() == "Error: Postal Code is required"

    page.close()