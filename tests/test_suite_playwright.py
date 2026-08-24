import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope='function')
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
    page.goto('https://www.saucedemo.com')
    page.fill('#user-name', username)
    page.fill('#password', password)
    page.click('#login-button')

def go_to_cart(page):
    page.click('.shopping_cart_link')

def proceed_to_checkout(page):
    page.click('#checkout')

def fill_checkout_info(page, first_name, last_name, postal_code):
    page.fill('#first-name', first_name)
    page.fill('#last-name', last_name)
    page.fill('#postal-code', postal_code)

def complete_checkout(page):
    page.click('#continue')
    page.click('#finish')

def test_successfully_remove_product_from_cart(browser_context):
    page = browser_context.new_page()
    login(page, 'standard_user', 'secret_sauce')
    add_to_cart(page, '#add-to-cart-sauce-labs-backpack')
    go_to_cart(page)
    remove_from_cart(page, '#remove-sauce-labs-backpack')
    
    assert not page.locator('.shopping_cart_badge').is_visible()

    # TODO: Assert "Sauce Labs Backpack" should no longer be in the cart
    page.close()

def test_attempt_to_remove_product_not_in_cart(browser_context):
    page = browser_context.new_page()
    login(page, 'standard_user', 'secret_sauce')
    go_to_cart(page)

    # Attempt to click remove on an item not in the cart
    try:
        page.click('#remove-sauce-labs-backpack')
    except Exception:
        pass  # Button would not be visible

    assert not page.locator('.shopping_cart_badge').is_visible()
    # TODO: Assert appropriate error message displayed 
    page.close()

def test_successfully_add_product_to_cart(browser_context):
    page = browser_context.new_page()
    login(page, 'standard_user', 'secret_sauce')
    add_to_cart(page, '#add-to-cart-sauce-labs-backpack')
    
    assert page.locator('.shopping_cart_badge').is_visible()
    assert page.locator('#remove-sauce-labs-backpack').is_visible()  # After adding to cart
    # TODO: Assert "Sauce Labs Backpack" should be in the cart
    page.close()

def test_attempt_to_add_product_when_already_in_cart(browser_context):
    page = browser_context.new_page()
    login(page, 'standard_user', 'secret_sauce')
    add_to_cart(page, '#add-to-cart-sauce-labs-backpack')
    
    # Attempt to add the same product again
    page.click('#add-to-cart-sauce-labs-backpack')
    
    assert page.locator('#remove-sauce-labs-backpack').is_visible()  # Should be visible, toggled
    assert page.locator('.shopping_cart_badge').inner_text() == "1"  # Badge should still show "1"
    
    page.close()

def test_successful_login_with_valid_credentials(browser_context):
    page = browser_context.new_page()
    login(page, 'standard_user', 'secret_sauce')
    
    assert page.url.endswith('/inventory.html')
    assert page.locator('.inventory_list').is_visible()  # Inventory should be visible
    
    page.close()

def test_failed_login_with_invalid_credentials(browser_context):
    page = browser_context.new_page()
    login(page, 'wrong_user', 'wrong_pass')
    
    assert page.locator('.error-message-container').inner_text() == "Epic sadface: Username and password do not match any user in this service"
    assert page.url.endswith('/')

    page.close()

def test_successful_checkout_with_all_details(browser_context):
    page = browser_context.new_page()
    login(page, 'standard_user', 'secret_sauce')
    add_to_cart(page, '#add-to-cart-sauce-labs-backpack')
    go_to_cart(page)
    proceed_to_checkout(page)
    fill_checkout_info(page, 'John', 'Doe', '12345')
    complete_checkout(page)
    
    assert page.locator('.complete-header').inner_text() == "Thank you for your order!"
    
    page.close()

def test_checkout_with_missing_postal_code(browser_context):
    page = browser_context.new_page()
    login(page, 'standard_user', 'secret_sauce')
    add_to_cart(page, '#add-to-cart-sauce-labs-backpack')
    go_to_cart(page)
    proceed_to_checkout(page)
    fill_checkout_info(page, 'John', 'Doe', '')
    
    page.click('#continue')
    
    assert page.locator('.error-message-container').inner_text() == "Error: Postal Code is required"
    
    page.close()