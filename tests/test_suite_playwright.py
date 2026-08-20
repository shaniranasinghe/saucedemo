import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

def test_successfully_remove_product_from_cart(page):
    # Given I have "Sauce Labs Backpack" in my shopping cart
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.click("#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")

    # When I click "Remove" on "Sauce Labs Backpack"
    page.click("#remove-sauce-labs-backpack")

    # Then the cart badge should not be displayed
    assert not page.query_selector(".shopping_cart_badge")

    # And "Sauce Labs Backpack" should no longer be in my cart
    assert not page.is_visible("#remove-sauce-labs-backpack")

def test_attempt_to_remove_a_product_not_in_cart(page):
    # Given I have no items in my shopping cart
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.click(".shopping_cart_link")

    # When I attempt to click "Remove" on "Sauce Labs Backpack"
    with pytest.raises(Exception):  # Assuming the remove button would not be visible
        page.click("#remove-sauce-labs-backpack")

    # Then I should see an error message
    # TODO: selector for error message not crawled yet

    # And the cart badge should not be displayed
    assert not page.query_selector(".shopping_cart_badge")

def test_successfully_add_product_to_cart(page):
    # Given I am on the SauceDemo product page
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")

    # When I click "Add to cart" on "Sauce Labs Backpack"
    page.click("#add-to-cart-sauce-labs-backpack")

    # Then the cart badge should be displayed with a count of 1
    assert page.inner_text(".shopping_cart_badge") == "1"

    # And "Sauce Labs Backpack" should be in my cart
    page.click(".shopping_cart_link")
    assert page.is_visible("#remove-sauce-labs-backpack")

def test_attempt_to_add_a_product_when_already_in_cart(page):
    # Given I have "Sauce Labs Backpack" in my shopping cart
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.click("#add-to-cart-sauce-labs-backpack")

    # When I click "Add to cart" on "Sauce Labs Backpack"
    page.click("#add-to-cart-sauce-labs-backpack")

    # Then I should see a message indicating the product is already in the cart
    # TODO: selector for the message not crawled yet

    # And the cart badge should still display a count of 1
    assert page.inner_text(".shopping_cart_badge") == "1"

def test_successful_login_with_valid_credentials(page):
    # Given I am on the login page
    page.goto("https://www.saucedemo.com")

    # When I enter valid username "standard_user"
    page.fill("#user-name", "standard_user")
    # And I enter valid password "secret_sauce"
    page.fill("#password", "secret_sauce")
    # And I click the login button
    page.click("#login-button")

    # Then I should be redirected to the products page
    assert page.url == "https://www.saucedemo.com/inventory.html"
    # And I should see the product inventory
    assert page.is_visible("#inventory_container")

def test_failed_login_with_invalid_credentials(page):
    # Given I am on the login page
    page.goto("https://www.saucedemo.com")

    # When I enter invalid username "wrong_user"
    page.fill("#user-name", "wrong_user")
    # And I enter invalid password "wrong_pass"
    page.fill("#password", "wrong_pass")
    # And I click the login button
    page.click("#login-button")

    # Then I should see an error message "Epic sadface: Username and password do not match any user in this service"
    assert page.inner_text("h3") == "Epic sadface: Username and password do not match any user in this service"
    # And I should remain on the login page
    assert page.url == "https://www.saucedemo.com/"

def test_successful_checkout_with_all_details(page):
    # Given I have items in my cart
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.click("#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")

    # When I proceed to checkout
    # And I fill in first name "John"
    page.fill("#first-name", "John")
    # And I fill in last name "Doe"
    page.fill("#last-name", "Doe")
    # And I leave the postal code empty
    page.fill("#postal-code", "")
    # And I click Continue
    page.click("#continue")

    # Then I should see the order summary
    assert page.is_visible(".summary_info")

    # When I click Finish
    page.click("#finish")

    # Then I should see "Thank you for your order!"
    assert page.inner_text(".complete-header") == "Thank you for your order!"

def test_checkout_with_missing_postal_code(page):
    # Given I have items in my cart
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.click("#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")

    # When I proceed to checkout
    # And I fill in first name "John"
    page.fill("#first-name", "John")
    # And I fill in last name "Doe"
    page.fill("#last-name", "Doe")
    # And I leave the postal code empty
    page.fill("#postal-code", "")
    # And I click Continue
    page.click("#continue")

    # Then I should see error "Error: Postal Code is required"
    assert page.inner_text("h3") == "Error: Postal Code is required"
    # And I should remain on the checkout information page
    assert page.url == "https://www.saucedemo.com/checkout-step-one.html"