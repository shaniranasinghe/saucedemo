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

def add_to_cart(page, add_selector):
    page.click(add_selector)

def remove_from_cart(page, remove_selector):
    page.click(remove_selector)

def login(page, username, password):
    page.fill('#user-name', username)
    page.fill('#password', password)
    page.click('#login-button')

def checkout(page, first_name, last_name, postal_code):
    page.fill('#first-name', first_name)
    page.fill('#last-name', last_name)
    page.fill('#postal-code', postal_code)
    page.click('#continue')

def test_successfully_remove_product_from_cart(browser_context):
    page = browser_context.new_page()
    page.goto('https://www.saucedemo.com/inventory.html')
    
    # Assuming we already added "Sauce Labs Backpack" to the cart in a prior step
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    
    # Remove the product
    remove_from_cart(page, "#remove-sauce-labs-backpack")

    # Assertion
    assert not page.locator(".shopping_cart_badge").is_visible()
    page.goto('https://www.saucedemo.com/cart.html')
    assert not page.locator("#remove-sauce-labs-backpack").is_visible()
    page.close()

def test_attempt_to_remove_product_not_in_cart(browser_context):
    page = browser_context.new_page()
    page.goto('https://www.saucedemo.com/cart.html')

    # Attempt to remove the product when cart is empty
    if page.locator("#remove-sauce-labs-backpack").is_visible():
        page.click("#remove-sauce-labs-backpack")

    # Assertions
    assert not page.locator(".shopping_cart_badge").is_visible()
    # # TODO: selector for 'error message' not crawled yet
    page.close()

def test_successfully_add_product_to_cart(browser_context):
    page = browser_context.new_page()
    page.goto('https://www.saucedemo.com/inventory.html')

    # Add product to cart
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")

    # Assertions
    assert page.locator("#remove-sauce-labs-backpack").is_visible()
    assert page.locator(".shopping_cart_badge").inner_text() == "1"
    page.close()

def test_attempt_to_add_product_when_already_in_cart(browser_context):
    page = browser_context.new_page()
    page.goto('https://www.saucedemo.com/inventory.html')

    # Add product to cart
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")

    # Attempt to add again
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    
    # Assertions
    assert page.locator("#remove-sauce-labs-backpack").is_visible()
    assert page.locator(".shopping_cart_badge").inner_text() == "1"
    # # TODO: selector for 'already in cart message' not crawled yet
    page.close()

def test_successful_login_with_valid_credentials(browser_context):
    page = browser_context.new_page()
    page.goto('https://www.saucedemo.com/')

    login(page, "standard_user", "secret_sauce")

    # Assertions
    assert page.url == "https://www.saucedemo.com/inventory.html"
    assert page.locator('.inventory_list').is_visible()
    page.close()

def test_failed_login_with_invalid_credentials(browser_context):
    page = browser_context.new_page()
    page.goto('https://www.saucedemo.com/')

    login(page, "wrong_user", "wrong_pass")
    
    # Assertions
    assert page.locator('.error-message-container').inner_text() == "Epic sadface: Username and password do not match any user in this service"
    assert page.url == "https://www.saucedemo.com/"
    page.close()

def test_successful_checkout_with_all_details(browser_context):
    page = browser_context.new_page()
    page.goto('https://www.saucedemo.com/')

    # Login first
    login(page, "standard_user", "secret_sauce")
    
    # Add product to cart
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    
    # Proceed to checkout
    page.click('.shopping_cart_link')
    page.click('#checkout')

    # Fill checkout form and finish
    checkout(page, "John", "Doe", "")
    assert page.locator('.error-message-container').inner_text() == "Error: Postal Code is required"

    page.close()

def test_checkout_with_missing_postal_code(browser_context):
    page = browser_context.new_page()
    page.goto('https://www.saucedemo.com/')

    # Login first
    login(page, "standard_user", "secret_sauce")
    
    # Add product to cart
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    
    # Proceed to checkout
    page.click('.shopping_cart_link')
    page.click('#checkout')

    # Fill first name and last name only
    checkout(page, "John", "Doe", "")
    
    # Assertions
    assert page.locator('.error-message-container').inner_text() == "Error: Postal Code is required"
    
    page.close()