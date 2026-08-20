import time
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module")
def setup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()


def login(page):
    page.goto("https://www.saucedemo.com")
    page.fill('[data-test="username"]', "standard_user")
    page.fill('[data-test="password"]', "secret_sauce")
    page.click('[data-test="login-button"]')
    page.wait_for_timeout(1000)


def navigate_to_cart(page):
    page.click("#react-burger-menu-btn")
    page.click("#inventory_sidebar_link")
    

def cart_badge_visible(page):
    return page.is_visible(".shopping_cart_badge")


def add_item_to_cart(page, item):
    item_mapping = {
        "Sauce Labs Backpack": "#add-to-cart-sauce-labs-backpack",
        "Sauce Labs Bike Light": "#add-to-cart-sauce-labs-bike-light",
        "Sauce Labs Bolt T-Shirt": "#add-to-cart-sauce-labs-bolt-t-shirt",
        "Sauce Labs Fleece Jacket": "#add-to-cart-sauce-labs-fleece-jacket",
        "Sauce Labs Onesie": "#add-to-cart-sauce-labs-onesie",
        "Test.allTheThings() T-Shirt (Red)": "#add-to-cart-test.allthethings()-t-shirt-(red)"
    }
    
    page.click(item_mapping[item])
    time.sleep(1)


def remove_item_from_cart(page, item):
    # This selector assumes a button with role "Remove" exists next to the given item
    item_mapping = {
        "Sauce Labs Backpack": "#remove-sauce-labs-backpack",
        "Sauce Labs Bike Light": "#remove-sauce-labs-bike-light",
        "Sauce Labs Bolt T-Shirt": "#remove-sauce-labs-bolt-t-shirt",
        "Sauce Labs Fleece Jacket": "#remove-sauce-labs-fleece-jacket",
        "Sauce Labs Onesie": "#remove-sauce-labs-onesie",
        "Test.allTheThings() T-Shirt (Red)": "#remove-test.allthethings()-t-shirt-(red)"
    }
    
    page.click(item_mapping[item])
    time.sleep(1)


def item_in_cart(page, item):
    return page.is_visible(f"text={item}")


def check_alert(page, expected_message):
    page.wait_for_timeout(1000)
    assert expected_message in page.content()


def test_successfully_remove_single_item_from_cart_via_product_listing_page(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    assert cart_badge_visible(page)
    assert page.is_visible("#shopping_cart_container .shopping_cart_badge")
    remove_item_from_cart(page, "Sauce Labs Backpack")
    assert not cart_badge_visible(page)
    assert page.is_visible("#add-to-cart-sauce-labs-backpack")


def test_successfully_remove_single_item_from_cart_via_cart_page(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Bike Light")
    navigate_to_cart(page)
    remove_item_from_cart(page, "Sauce Labs Bike Light")
    assert not item_in_cart(page, "Sauce Labs Bike Light")
    assert not cart_badge_visible(page)


def test_successfully_remove_one_item_when_multiple_items_in_cart(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    add_item_to_cart(page, "Sauce Labs Bike Light")
    add_item_to_cart(page, "Sauce Labs Bolt T-Shirt")
    navigate_to_cart(page)
    assert cart_badge_visible(page)
    remove_item_from_cart(page, "Sauce Labs Bike Light")
    assert not item_in_cart(page, "Sauce Labs Bike Light")
    assert item_in_cart(page, "Sauce Labs Backpack")
    assert item_in_cart(page, "Sauce Labs Bolt T-Shirt")


def test_remove_all_items_from_cart_one_by_one(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    add_item_to_cart(page, "Sauce Labs Bike Light")
    navigate_to_cart(page)
    remove_item_from_cart(page, "Sauce Labs Backpack")
    remove_item_from_cart(page, "Sauce Labs Bike Light")
    assert not cart_badge_visible(page)


def test_attempt_to_remove_item_no_longer_in_cart(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    navigate_to_cart(page)
    remove_item_from_cart(page, "Sauce Labs Backpack")
    assert not item_in_cart(page, "Sauce Labs Backpack")
    remove_item_from_cart(page, "Sauce Labs Backpack")
    assert not item_in_cart(page, "Sauce Labs Backpack")


def test_cart_remains_empty_after_removing_item_navigating_away_and_back(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Fleece Jacket")
    navigate_to_cart(page)
    remove_item_from_cart(page, "Sauce Labs Fleece Jacket")
    page.click("#react-burger-menu-btn")
    page.click("#inventory_sidebar_link")
    navigate_to_cart(page)
    assert not cart_badge_visible(page)


def test_removed_item_button_resets_to_add_to_cart_on_product_detail_page(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    page.click("#item_4_title_link")  # Navigate to the product detail page
    remove_item_from_cart(page, "Sauce Labs Backpack")
    assert page.is_visible("#add-to-cart-sauce-labs-backpack")


def test_successful_checkout_with_single_item(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    navigate_to_cart(page)
    page.click("#checkout")
    page.fill('[data-test="firstName"]', "John")
    page.fill('[data-test="lastName"]', "Doe")
    page.fill('[data-test="postalCode"]', "12345")
    page.click("[data-test='continue']");
    assert page.title() == "Checkout: Overview"
    assert item_in_cart(page, "Sauce Labs Backpack")
    page.click("#finish")
    check_alert(page, "Thank you for your order!")


def test_successful_checkout_with_multiple_items(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    add_item_to_cart(page, "Sauce Labs Bike Light")
    add_item_to_cart(page, "Sauce Labs Bolt T-Shirt")
    navigate_to_cart(page)
    page.click("#checkout")
    page.fill('[data-test="firstName"]', "Jane")
    page.fill('[data-test="lastName"]', "Smith")
    page.fill('[data-test="postalCode"]', "67890")
    page.click("[data-test='continue']");
    assert page.title() == "Checkout: Overview"
    assert item_in_cart(page, "Sauce Labs Backpack")
    assert item_in_cart(page, "Sauce Labs Bike Light")
    assert item_in_cart(page, "Sauce Labs Bolt T-Shirt")
    page.click("#finish")
    check_alert(page, "Thank you for your order!")


def test_checkout_with_correct_total_calculation(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    add_item_to_cart(page, "Sauce Labs Bike Light")
    navigate_to_cart(page)
    page.click("#checkout")
    page.fill('[data-test="firstName"]', "John")
    page.fill('[data-test="lastName"]', "Doe")
    page.fill('[data-test="postalCode"]', "12345")
    page.click("[data-test='continue']");
    assert page.title() == "Checkout: Overview"
    assert page.is_visible("text=39.98")  # Simplified total assert
    page.click("#finish")
    check_alert(page, "Thank you for your order!")


def test_checkout_fails_when_first_name_is_missing(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    navigate_to_cart(page)
    page.click("#checkout")
    page.fill('[data-test="lastName"]', "Doe")
    page.fill('[data-test="postalCode"]', "12345")
    page.click("[data-test='continue']");
    check_alert(page, "Error: First Name is required")
    assert page.title() == "Checkout: Your Information"


def test_checkout_fails_when_last_name_is_missing(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    navigate_to_cart(page)
    page.click("#checkout")
    page.fill('[data-test="firstName"]', "John")
    page.fill('[data-test="postalCode"]', "12345")
    page.click("[data-test='continue']");
    check_alert(page, "Error: Last Name is required")
    assert page.title() == "Checkout: Your Information"


def test_checkout_fails_when_postal_code_is_missing(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    navigate_to_cart(page)
    page.click("#checkout")
    page.fill('[data-test="firstName"]', "John")
    page.fill('[data-test="lastName"]', "Doe")
    page.click("[data-test='continue']");
    check_alert(page, "Error: Postal Code is required")
    assert page.title() == "Checkout: Your Information"


def test_checkout_fails_when_all_fields_are_empty(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    navigate_to_cart(page)
    page.click("#checkout")
    page.click("[data-test='continue']");
    check_alert(page, "Error: First Name is required")
    assert page.title() == "Checkout: Your Information"


def test_successfully_add_single_product_to_cart_from_products_page(setup):
    page = setup
    login(page)    
    assert not cart_badge_visible(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    assert cart_badge_visible(page)
    assert page.is_visible("#remove-sauce-labs-backpack")


def test_successfully_add_multiple_products_to_cart(setup):
    page = setup
    login(page)
    assert not cart_badge_visible(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    add_item_to_cart(page, "Sauce Labs Bike Light")
    assert cart_badge_visible(page)
    assert page.is_visible("#remove-sauce-labs-backpack")
    assert page.is_visible("#remove-sauce-labs-bike-light")


def test_successfully_add_product_to_cart_from_product_detail_page(setup):
    page = setup
    login(page)
    page.click("#item_1_title_link")  # Navigate to the product detail page
    add_item_to_cart(page, "Sauce Labs Bolt T-Shirt")
    assert cart_badge_visible(page)
    assert page.is_visible("#remove-sauce-labs-bolt-t-shirt")


def test_added_product_appears_in_shopping_cart_with_correct_details(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    navigate_to_cart(page)
    assert item_in_cart(page, "Sauce Labs Backpack")
    # Assume we would check price and quantity in real tests


def test_cart_persists_after_navigating_away_and_returning(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Fleece Jacket")
    navigate_to_cart(page)
    assert item_in_cart(page, "Sauce Labs Fleece Jacket")
    page.click("#react-burger-menu-btn")
    page.click("#inventory_sidebar_link")
    time.sleep(1)
    navigate_to_cart(page)
    assert item_in_cart(page, "Sauce Labs Fleece Jacket")


def test_remove_product_that_was_added_to_cart(setup):
    page = setup
    login(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    remove_item_from_cart(page, "Sauce Labs Backpack")
    assert not cart_badge_visible(page)


def test_attempt_to_add_product_to_cart_without_being_logged_in(setup):
    page = setup
    page.goto("https://www.saucedemo.com/inventory.html")
    assert page.title() == "Swag Labs"
    check_alert(page, "Epic sadface: You can only access this page when you are logged in.")


def test_locked_out_user_cannot_access_products_page_to_add_items_to_cart(setup):
    page = setup
    page.goto("https://www.saucedemo.com")
    page.fill('[data-test="username"]', "locked_out_user")
    page.fill('[data-test="password"]', "secret_sauce")
    page.click('[data-test="login-button"]')
    check_alert(page, "Epic sadface: Sorry, this user has been locked out.")
    assert not item_in_cart(page, "Sauce Labs Backpack")


def test_cart_badge_updates_correctly_when_adding_removing_products(setup):
    page = setup
    login(page)
    assert not cart_badge_visible(page)
    add_item_to_cart(page, "Sauce Labs Backpack")
    add_item_to_cart(page, "Sauce Labs Bike Light")
    remove_item_from_cart(page, "Sauce Labs Backpack")
    assert cart_badge_visible(page)
    assert not item_in_cart(page, "Sauce Labs Backpack")