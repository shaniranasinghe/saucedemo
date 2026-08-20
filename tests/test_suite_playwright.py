import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope='module')
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture(scope='function')
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

def test_successfully_remove_item_from_cart(page):
    # Given I have "Sauce Labs Backpack" in my cart
    page.goto("https://www.saucedemo.com")
    page.fill("input#user-name", "standard_user")
    page.fill("input#password", "secret_sauce")
    page.click("input[type='submit']")
    page.click("#add-to-cart-sauce-labs-backpack")
    page.click("#react-burger-menu-btn")
    page.click("a#shopping_cart_container .shopping_cart_link")
    
    # When I click "Remove" on "Sauce Labs Backpack"
    page.click("text=Remove")
    
    # Then the cart badge should show "0"
    assert page.locator(".shopping_cart_badge").inner_text() == "0"
    
    # And "Sauce Labs Backpack" should no longer be in my cart
    assert not page.locator("text=Sauce Labs Backpack").is_visible()

def test_attempt_to_remove_item_not_in_cart(page):
    # Given I have no items in my cart
    page.goto("https://www.saucedemo.com")
    page.fill("input#user-name", "standard_user")
    page.fill("input#password", "secret_sauce")
    page.click("input[type='submit']")
    
    # When I try to click "Remove" on "Sauce Labs Backpack"
    page.click("#react-burger-menu-btn")
    page.click("a#shopping_cart_container .shopping_cart_link")
    page.click("text=Remove")  # This should not throw an error
    
    # Then I should see a message "Your cart is empty"
    assert page.locator("text=Your cart is empty").is_visible()
    
    # And the cart badge should show "0"
    assert page.locator(".shopping_cart_badge").inner_text() == "0"

def test_successfully_add_product_to_shopping_cart(page):
    # Given I am on the products page
    page.goto("https://www.saucedemo.com")
    page.fill("input#user-name", "standard_user")
    page.fill("input#password", "secret_sauce")
    page.click("input[type='submit']")
    
    # When I click "Add to cart" on "Sauce Labs Backpack"
    page.click("#add-to-cart-sauce-labs-backpack")
    
    # Then the cart badge should show "1"
    assert page.locator(".shopping_cart_badge").inner_text() == "1"
    
    # And the button label should change to "Remove"
    assert page.locator("#add-to-cart-sauce-labs-backpack").inner_text() == "Remove"

def test_attempt_to_add_product_when_out_of_stock(page):
    # Given I am on the products page
    page.goto("https://www.saucedemo.com")
    page.fill("input#user-name", "standard_user")
    page.fill("input#password", "secret_sauce")
    page.click("input[type='submit']")
    
    # And "Sauce Labs Bike Light" is out of stock (assumption for test setup)
    
    # When I click "Add to cart" on "Sauce Labs Bike Light"
    page.click("#add-to-cart-sauce-labs-bike-light")
    
    # Then I should see a message "This item is currently out of stock"
    assert page.locator("text=This item is currently out of stock").is_visible()
    
    # And the cart badge should not change
    assert page.locator(".shopping_cart_badge").inner_text() == "0"

def test_successful_login_with_valid_credentials(page):
    # Given I am on the login page
    page.goto("https://www.saucedemo.com")
    
    # When I enter valid username "standard_user"
    page.fill("input#user-name", "standard_user")
    
    # And I enter valid password "secret_sauce"
    page.fill("input#password", "secret_sauce")
    
    # And I click the login button
    page.click("input[type='submit']")
    
    # Then I should be redirected to the products page
    assert page.url == "https://www.saucedemo.com/inventory.html"
    
    # And I should see the product inventory
    assert page.locator(".inventory_list").is_visible()

def test_failed_login_with_invalid_credentials(page):
    # Given I am on the login page
    page.goto("https://www.saucedemo.com")
    
    # When I enter invalid username "wrong_user"
    page.fill("input#user-name", "wrong_user")
    
    # And I enter invalid password "wrong_pass"
    page.fill("input#password", "wrong_pass")
    
    # And I click the login button
    page.click("input[type='submit']")
    
    # Then I should see an error message "Epic sadface: Username and password do not match"
    assert page.locator("text=Epic sadface: Username and password do not match").is_visible()
    
    # And I should remain on the login page
    assert page.url == "https://www.saucedemo.com/"

def test_successful_checkout_with_all_details(page):
    # Given I have items in my cart
    page.goto("https://www.saucedemo.com")
    page.fill("input#user-name", "standard_user")
    page.fill("input#password", "secret_sauce")
    page.click("input[type='submit']")
    page.click("#add-to-cart-sauce-labs-backpack")
    page.click("#react-burger-menu-btn")
    page.click("a#shopping_cart_container .shopping_cart_link")
    
    # When I proceed to checkout
    page.click("text=Checkout")
    
    # And I fill in first name "John"
    page.fill("input#first-name", "John")
    
    # And I fill in last name "Doe"
    page.fill("input#last-name", "Doe")
    
    # And I fill in postal code "12345"
    page.fill("input#postal-code", "12345")
    
    # And I click Continue
    page.click("input[type='submit']")
    
    # Then I should see the order summary
    assert page.locator(".summary_info").is_visible()
    
    # When I click Finish
    page.click("text=Finish")
    
    # Then I should see "Thank you for your order!"
    assert page.locator("text=Thank you for your order!").is_visible()

def test_checkout_with_invalid_postal_code(page):
    # Given I have items in my cart
    page.goto("https://www.saucedemo.com")
    page.fill("input#user-name", "standard_user")
    page.fill("input#password", "secret_sauce")
    page.click("input[type='submit']")
    page.click("#add-to-cart-sauce-labs-backpack")
    page.click("#react-burger-menu-btn")
    page.click("a#shopping_cart_container .shopping_cart_link")
    
    # When I proceed to checkout
    page.click("text=Checkout")
    
    # And I fill in first name "John"
    page.fill("input#first-name", "John")
    
    # And I fill in last name "Doe"
    page.fill("input#last-name", "Doe")
    
    # And I fill in postal code "ABCDE"
    page.fill("input#postal-code", "ABCDE")
    
    # And I click Continue
    page.click("input[type='submit']")
    
    # Then I should see error "Postal Code is invalid"
    assert page.locator("text=Postal Code is invalid").is_visible()
    
    # And I should remain on the checkout information page
    assert page.url == "https://www.saucedemo.com/checkout-step-one.html"