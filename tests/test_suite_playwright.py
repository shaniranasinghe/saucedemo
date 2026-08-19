import pytest
from playwright.sync_api import sync_playwright, Page, expect
import re
import time

# ─────────────────────────────────────────────
# Selectors (from crawled DOM)
# ─────────────────────────────────────────────
SEL_USERNAME = "#user-name"
SEL_PASSWORD = "#password"
SEL_LOGIN_BTN = "#login-button"
SEL_ERROR_MSG = "[data-test='error']"
SEL_PRODUCTS_TITLE = ".title"
SEL_CART_BADGE = ".shopping_cart_badge"
SEL_CART_LINK = ".shopping_cart_link"
SEL_BURGER_MENU = "#react-burger-menu-btn"
SEL_LOGOUT_LINK = "#logout_sidebar_link"
SEL_INVENTORY_LIST = ".inventory_list"

# Add-to-cart buttons
SEL_ADD_BACKPACK = "#add-to-cart-sauce-labs-backpack"
SEL_ADD_BIKE_LIGHT = "#add-to-cart-sauce-labs-bike-light"
SEL_ADD_BOLT_SHIRT = "#add-to-cart-sauce-labs-bolt-t-shirt"
SEL_ADD_FLEECE_JACKET = "#add-to-cart-sauce-labs-fleece-jacket"
SEL_ADD_ONESIE = "#add-to-cart-sauce-labs-onesie"
SEL_ADD_RED_SHIRT = r"#add-to-cart-test\.allthethings\(\)-t-shirt-\(red\)"

# Remove buttons (mirrored naming convention)
SEL_REMOVE_BACKPACK = "#remove-sauce-labs-backpack"
SEL_REMOVE_BIKE_LIGHT = "#remove-sauce-labs-bike-light"
SEL_REMOVE_BOLT_SHIRT = "#remove-sauce-labs-bolt-t-shirt"
SEL_REMOVE_FLEECE_JACKET = "#remove-sauce-labs-fleece-jacket"
SEL_REMOVE_ONESIE = "#remove-sauce-labs-onesie"
SEL_REMOVE_RED_SHIRT = r"#remove-test\.allthethings\(\)-t-shirt-\(red\)"

# Product title links
SEL_LINK_BACKPACK = "#item_4_title_link"
SEL_LINK_BIKE_LIGHT = "#item_0_title_link"
SEL_LINK_BOLT_SHIRT = "#item_1_title_link"
SEL_LINK_FLEECE_JACKET = "#item_5_title_link"
SEL_LINK_ONESIE = "#item_2_title_link"
SEL_LINK_RED_SHIRT = "#item_3_title_link"

# Image links
SEL_IMG_ITEM_0 = "#item_0_img_link"
SEL_IMG_ITEM_1 = "#item_1_img_link"
SEL_IMG_ITEM_2 = "#item_2_img_link"
SEL_IMG_ITEM_3 = "#item_3_img_link"
SEL_IMG_ITEM_4 = "#item_4_img_link"
SEL_IMG_ITEM_5 = "#item_5_img_link"

# Footer social links
SEL_TWITTER = "#page_wrapper > footer > ul > li:nth-of-type(1) > a"
SEL_FACEBOOK = "#page_wrapper > footer > ul > li:nth-of-type(2) > a"
SEL_LINKEDIN = "#page_wrapper > footer > ul > li:nth-of-type(3) > a"

# Sort dropdown
SEL_SORT = "#header_container > div:nth-of-type(2) > div > span > select"

# Checkout selectors
SEL_CHECKOUT_BTN = "#checkout"
SEL_FIRST_NAME = "#first-name"
SEL_LAST_NAME = "#last-name"
SEL_POSTAL_CODE = "#postal-code"
SEL_CONTINUE_BTN = "#continue"
SEL_FINISH_BTN = "#finish"
SEL_CHECKOUT_COMPLETE_HEADER = ".complete-header"
SEL_CHECKOUT_COMPLETE_TEXT = ".complete-text"
SEL_SUMMARY_SUBTOTAL = ".summary_subtotal_label"
SEL_SUMMARY_TAX = ".summary_tax_label"
SEL_SUMMARY_TOTAL = ".summary_total_label"
SEL_CART_ITEM = ".cart_item"
SEL_CART_ITEM_NAME = ".inventory_item_name"
SEL_CONTINUE_SHOPPING = "#continue-shopping"

BASE_URL = "https://www.saucedemo.com"
INVENTORY_URL = f"{BASE_URL}/inventory.html"
CART_URL = f"{BASE_URL}/cart.html"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

PRODUCT_ADD_SELECTORS = {
    "Sauce Labs Backpack": SEL_ADD_BACKPACK,
    "Sauce Labs Bike Light": SEL_ADD_BIKE_LIGHT,
    "Sauce Labs Bolt T-Shirt": SEL_ADD_BOLT_SHIRT,
    "Sauce Labs Fleece Jacket": SEL_ADD_FLEECE_JACKET,
    "Sauce Labs Onesie": SEL_ADD_ONESIE,
    "Test.allTheThings() T-Shirt (Red)": SEL_ADD_RED_SHIRT,
}

PRODUCT_REMOVE_SELECTORS = {
    "Sauce Labs Backpack": SEL_REMOVE_BACKPACK,
    "Sauce Labs Bike Light": SEL_REMOVE_BIKE_LIGHT,
    "Sauce Labs Bolt T-Shirt": SEL_REMOVE_BOLT_SHIRT,
    "Sauce Labs Fleece Jacket": SEL_REMOVE_FLEECE_JACKET,
    "Sauce Labs Onesie": SEL_REMOVE_ONESIE,
    "Test.allTheThings() T-Shirt (Red)": SEL_REMOVE_RED_SHIRT,
}

PRODUCT_TITLE_SELECTORS = {
    "Sauce Labs Backpack": SEL_LINK_BACKPACK,
    "Sauce Labs Bike Light": SEL_LINK_BIKE_LIGHT,
    "Sauce Labs Bolt T-Shirt": SEL_LINK_BOLT_SHIRT,
    "Sauce Labs Fleece Jacket": SEL_LINK_FLEECE_JACKET,
    "Sauce Labs Onesie": SEL_LINK_ONESIE,
    "Test.allTheThings() T-Shirt (Red)": SEL_LINK_RED_SHIRT,
}


def do_login(page: Page, username: str, password: str):
    page.goto(BASE_URL)
    page.fill(SEL_USERNAME, username)
    page.fill(SEL_PASSWORD, password)
    page.click(SEL_LOGIN_BTN)


def get_cart_badge_count(page: Page):
    badge = page.locator(SEL_CART_BADGE)
    if badge.count() == 0:
        return 0
    return int(badge.text_content())


def cart_badge_visible(page: Page) -> bool:
    return page.locator(SEL_CART_BADGE).count() > 0


def get_cart_item_names(page: Page):
    items = page.locator(SEL_CART_ITEM_NAME).all()
    return [item.text_content().strip() for item in items]


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser_instance):
    context = browser_instance.new_context()
    pg = context.new_page()
    yield pg
    context.close()


@pytest.fixture
def logged_in_page(page: Page):
    """Returns a page already logged in as standard_user on inventory."""
    do_login(page, "standard_user", "secret_sauce")
    page.wait_for_url(f"{BASE_URL}/inventory.html")
    return page


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 1: User Login to Access Product Inventory
# ─────────────────────────────────────────────────────────────────────────────

class TestUserLogin:

    def test_successful_login_standard_user(self, page: Page):
        """Successful login with valid standard user credentials"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "standard_user")
        page.fill(SEL_PASSWORD, "secret_sauce")
        page.click(SEL_LOGIN_BTN)
        page.wait_for_url(INVENTORY_URL)
        assert page.url == INVENTORY_URL
        title = page.locator(SEL_PRODUCTS_TITLE)
        expect(title).to_have_text("Products")
        expect(page.locator(SEL_INVENTORY_LIST)).to_be_visible()

    def test_successful_login_problem_user(self, page: Page):
        """Successful login with valid problem user credentials"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "problem_user")
        page.fill(SEL_PASSWORD, "secret_sauce")
        page.click(SEL_LOGIN_BTN)
        page.wait_for_url(INVENTORY_URL)
        assert page.url == INVENTORY_URL
        expect(page.locator(SEL_PRODUCTS_TITLE)).to_have_text("Products")

    def test_successful_login_performance_glitch_user(self, page: Page):
        """Successful login with valid performance glitch user credentials"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "performance_glitch_user")
        page.fill(SEL_PASSWORD, "secret_sauce")
        page.click(SEL_LOGIN_BTN)
        page.wait_for_url(INVENTORY_URL, timeout=15000)
        assert page.url == INVENTORY_URL
        expect(page.locator(SEL_PRODUCTS_TITLE)).to_have_text("Products")

    def test_failed_login_invalid_username(self, page: Page):
        """Failed login with invalid username"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "invalid_user")
        page.fill(SEL_PASSWORD, "secret_sauce")
        page.click(SEL_LOGIN_BTN)
        error = page.locator(SEL_ERROR_MSG)
        expect(error).to_be_visible()
        assert "Epic sadface: Username and password do not match any user in this service" in error.text_content()
        assert page.url == BASE_URL + "/"

    def test_failed_login_invalid_password(self, page: Page):
        """Failed login with invalid password"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "standard_user")
        page.fill(SEL_PASSWORD, "wrong_password")
        page.click(SEL_LOGIN_BTN)
        error = page.locator(SEL_ERROR_MSG)
        expect(error).to_be_visible()
        assert "Epic sadface: Username and password do not match any user in this service" in error.text_content()
        assert page.url == BASE_URL + "/"

    def test_failed_login_empty_username(self, page: Page):
        """Failed login with empty username"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "")
        page.fill(SEL_PASSWORD, "secret_sauce")
        page.click(SEL_LOGIN_BTN)
        error = page.locator(SEL_ERROR_MSG)
        expect(error).to_be_visible()
        assert "Epic sadface: Username is required" in error.text_content()
        assert page.url == BASE_URL + "/"

    def test_failed_login_empty_password(self, page: Page):
        """Failed login with empty password"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "standard_user")
        page.fill(SEL_PASSWORD, "")
        page.click(SEL_LOGIN_BTN)
        error = page.locator(SEL_ERROR_MSG)
        expect(error).to_be_visible()
        assert "Epic sadface: Password is required" in error.text_content()
        assert page.url == BASE_URL + "/"

    def test_failed_login_both_empty(self, page: Page):
        """Failed login with both username and password empty"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "")
        page.fill(SEL_PASSWORD, "")
        page.click(SEL_LOGIN_BTN)
        error = page.locator(SEL_ERROR_MSG)
        expect(error).to_be_visible()
        assert "Epic sadface: Username is required" in error.text_content()
        assert page.url == BASE_URL + "/"

    def test_failed_login_locked_out_user(self, page: Page):
        """Failed login with locked out user credentials"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, "locked_out_user")
        page.fill(SEL_PASSWORD, "secret_sauce")
        page.click(SEL_LOGIN_BTN)
        error = page.locator(SEL_ERROR_MSG)
        expect(error).to_be_visible()
        assert "Epic sadface: Sorry, this user has been locked out." in error.text_content()
        assert page.url == BASE_URL + "/"

    def test_session_persists_after_refresh(self, page: Page):
        """Session persists across page refresh after successful login"""
        do_login(page, "standard_user", "secret_sauce")
        page.wait_for_url(INVENTORY_URL)
        page.reload()
        page.wait_for_url(INVENTORY_URL)
        assert page.url == INVENTORY_URL
        expect(page.locator(SEL_PRODUCTS_TITLE)).to_have_text("Products")
        expect(page.locator(SEL_INVENTORY_LIST)).to_be_visible()

    def test_user_can_logout(self, page: Page):
        """User can log out after successful login"""
        do_login(page, "standard_user", "secret_sauce")
        page.wait_for_url(INVENTORY_URL)
        page.click(SEL_BURGER_MENU)
        page.wait_for_selector(SEL_LOGOUT_LINK, state="visible")
        page.click(SEL_LOGOUT_LINK)
        page.wait_for_url(BASE_URL + "/")
        assert page.url.rstrip("/") == BASE_URL.rstrip("/")
        # Attempt to access inventory without login
        page.goto(INVENTORY_URL)
        # Should be redirected back to login
        assert page.url.rstrip("/") != INVENTORY_URL.rstrip("/") or \
               page.locator(SEL_ERROR_MSG).count() > 0 or \
               page.locator(SEL_LOGIN_BTN).count() > 0

    @pytest.mark.parametrize("username,password", [
        ("standard_user", "secret_sauce"),
        ("problem_user", "secret_sauce"),
        ("performance_glitch_user", "secret_sauce"),
    ])
    def test_successful_login_multiple_users(self, page: Page, username: str, password: str):
        """Successful login with multiple valid user accounts"""
        page.goto(BASE_URL)
        page.fill(SEL_USERNAME, username)
        page.fill(SEL_PASSWORD, password)
        page.click(SEL_LOGIN_BTN)
        page.wait_for_