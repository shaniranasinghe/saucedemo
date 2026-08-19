import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# =============================================================================
# Constants / Selectors
# =============================================================================
BASE_URL = "https://www.saucedemo.com"
INVENTORY_URL = f"{BASE_URL}/inventory.html"
CART_URL = f"{BASE_URL}/cart.html"

# Login selectors
USERNAME_INPUT = "#user-name"
PASSWORD_INPUT = "#password"
LOGIN_BUTTON = "#login-button"
ERROR_MESSAGE = "[data-test='error']"

# Navigation selectors
BURGER_MENU_BTN = "#react-burger-menu-btn"
LOGOUT_LINK = "#logout_sidebar_link"
CART_ICON = ".shopping_cart_link"
CART_BADGE = ".shopping_cart_badge"

# Product page selectors
PAGE_TITLE = ".title"
INVENTORY_LIST = ".inventory_list"
INVENTORY_ITEMS = ".inventory_item"

# Add to cart buttons (from crawled DOM)
ADD_TO_CART_BACKPACK = "#add-to-cart-sauce-labs-backpack"
ADD_TO_CART_BIKE_LIGHT = "#add-to-cart-sauce-labs-bike-light"
ADD_TO_CART_BOLT_TSHIRT = "#add-to-cart-sauce-labs-bolt-t-shirt"
ADD_TO_CART_FLEECE_JACKET = "#add-to-cart-sauce-labs-fleece-jacket"
ADD_TO_CART_ONESIE = "#add-to-cart-sauce-labs-onesie"
ADD_TO_CART_RED_TSHIRT = r"#add-to-cart-test\.allthethings\(\)-t-shirt-\(red\)"

# Remove buttons (dynamic, constructed from product name)
REMOVE_BACKPACK = "#remove-sauce-labs-backpack"
REMOVE_BIKE_LIGHT = "#remove-sauce-labs-bike-light"
REMOVE_BOLT_TSHIRT = "#remove-sauce-labs-bolt-t-shirt"
REMOVE_FLEECE_JACKET = "#remove-sauce-labs-fleece-jacket"
REMOVE_ONESIE = "#remove-sauce-labs-onesie"
REMOVE_RED_TSHIRT = r"#remove-test\.allthethings\(\)-t-shirt-\(red\)"

# Product title links
LINK_BACKPACK = "#item_4_title_link"
LINK_BIKE_LIGHT = "#item_0_title_link"
LINK_BOLT_TSHIRT = "#item_1_title_link"
LINK_FLEECE_JACKET = "#item_5_title_link"
LINK_ONESIE = "#item_2_title_link"
LINK_RED_TSHIRT = "#item_3_title_link"

# Product image links
LINK_ITEM_0_IMG = "#item_0_img_link"
LINK_ITEM_1_IMG = "#item_1_img_link"
LINK_ITEM_2_IMG = "#item_2_img_link"
LINK_ITEM_3_IMG = "#item_3_img_link"
LINK_ITEM_4_IMG = "#item_4_img_link"
LINK_ITEM_5_IMG = "#item_5_img_link"

# Footer links
TWITTER_LINK = "#page_wrapper > footer > ul > li:nth-of-type(1) > a"
FACEBOOK_LINK = "#page_wrapper > footer > ul > li:nth-of-type(2) > a"
LINKEDIN_LINK = "#page_wrapper > footer > ul > li:nth-of-type(3) > a"

# Sort dropdown
SORT_DROPDOWN = "#header_container > div:nth-of-type(2) > div > span > select"

# Checkout selectors
CHECKOUT_BUTTON = "#checkout"
CONTINUE_SHOPPING_BTN = "#continue-shopping"
FIRST_NAME_INPUT = "#first-name"
LAST_NAME_INPUT = "#last-name"
POSTAL_CODE_INPUT = "#postal-code"
CONTINUE_BUTTON = "#continue"
FINISH_BUTTON = "#finish"
CHECKOUT_COMPLETE_HEADER = ".complete-header"
CHECKOUT_COMPLETE_TEXT = ".complete-text"
SUMMARY_SUBTOTAL = ".summary_subtotal_label"
SUMMARY_TAX = ".summary_tax_label"
SUMMARY_TOTAL = ".summary_total_label"
CHECKOUT_ERROR = "[data-test='error']"

# Cart selectors
CART_ITEM = ".cart_item"
CART_ITEM_NAME = ".inventory_item_name"

# =============================================================================
# Helper Maps
# =============================================================================
PRODUCT_ADD_TO_CART_MAP = {
    "Sauce Labs Backpack": ADD_TO_CART_BACKPACK,
    "Sauce Labs Bike Light": ADD_TO_CART_BIKE_LIGHT,
    "Sauce Labs Bolt T-Shirt": ADD_TO_CART_BOLT_TSHIRT,
    "Sauce Labs Fleece Jacket": ADD_TO_CART_FLEECE_JACKET,
    "Sauce Labs Onesie": ADD_TO_CART_ONESIE,
    "Test.allTheThings() T-Shirt (Red)": ADD_TO_CART_RED_TSHIRT,
}

PRODUCT_REMOVE_MAP = {
    "Sauce Labs Backpack": REMOVE_BACKPACK,
    "Sauce Labs Bike Light": REMOVE_BIKE_LIGHT,
    "Sauce Labs Bolt T-Shirt": REMOVE_BOLT_TSHIRT,
    "Sauce Labs Fleece Jacket": REMOVE_FLEECE_JACKET,
    "Sauce Labs Onesie": REMOVE_ONESIE,
    "Test.allTheThings() T-Shirt (Red)": REMOVE_RED_TSHIRT,
}

PRODUCT_TITLE_LINK_MAP = {
    "Sauce Labs Backpack": LINK_BACKPACK,
    "Sauce Labs Bike Light": LINK_BIKE_LIGHT,
    "Sauce Labs Bolt T-Shirt": LINK_BOLT_TSHIRT,
    "Sauce Labs Fleece Jacket": LINK_FLEECE_JACKET,
    "Sauce Labs Onesie": LINK_ONESIE,
    "Test.allTheThings() T-Shirt (Red)": LINK_RED_TSHIRT,
}

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """Driver fixture that starts with a logged-in session as standard_user."""
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_INPUT)))
    driver.find_element(By.CSS_SELECTOR, USERNAME_INPUT).send_keys("standard_user")
    driver.find_element(By.CSS_SELECTOR, PASSWORD_INPUT).send_keys("secret_sauce")
    driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()
    wait.until(EC.url_contains("inventory"))
    return driver


# =============================================================================
# Helper Functions
# =============================================================================

def login(driver, username, password):
    wait = WebDriverWait(driver, 15)
    driver.get(BASE_URL)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_INPUT)))
    username_field = driver.find_element(By.CSS_SELECTOR, USERNAME_INPUT)
    username_field.clear()
    username_field.send_keys(username)
    password_field = driver.find_element(By.CSS_SELECTOR, PASSWORD_INPUT)
    password_field.clear()
    password_field.send_keys(password)
    driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()


def click_add_to_cart(driver, product_name):
    wait = WebDriverWait(driver, 15)
    selector = PRODUCT_ADD_TO_CART_MAP.get(product_name)
    if not selector:
        raise ValueError(f"No add-to-cart selector found for product: {product_name}")
    btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    btn.click()


def click_remove(driver, product_name):
    wait = WebDriverWait(driver, 15)
    selector = PRODUCT_REMOVE_MAP.get(product_name)
    if not selector:
        raise ValueError(f"No remove selector found for product: {product_name}")
    btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    btn.click()


def get_cart_badge_count(driver):
    """Returns integer cart badge count, or 0 if badge not visible."""
    try:
        badge = driver.find_element(By.CSS_SELECTOR, CART_BADGE)
        if badge.is_displayed():
            return int(badge.text)
    except NoSuchElementException:
        pass
    return 0


def is_cart_badge_visible(driver):
    try:
        badge = driver.find_element(By.CSS_SELECTOR, CART_BADGE)
        return badge.is_displayed()
    except NoSuchElementException:
        return False


def navigate_to_cart(driver):
    driver.find_element(By.CSS_SELECTOR, CART_ICON).click()
    WebDriverWait(driver, 15).until(EC.url_contains("cart"))


def get_cart_item_names(driver):
    """Returns list of product names currently in the cart."""
    try:
        items = driver.find_elements(By.CSS_SELECTOR, CART_ITEM_NAME)
        return [item.text for item in items]
    except NoSuchElementException:
        return []


def is_item_in_cart(driver, product_name):
    names = get_cart_item_names(driver)
    return product_name in names


def get_remove_button_in_cart(driver, product_name):
    """
    Finds the remove button inside the cart for a given product name.
    """
    cart_items = driver.find_elements(By.CSS_SELECTOR, CART_ITEM)
    for item in cart_items:
        try:
            name_el = item.find_element(By.CSS_SELECTOR, CART_ITEM_NAME)
            if name_el.text == product_name:
                remove_btn = item.find_element(By.CSS_SELECTOR, "button")
                return remove_btn
        except NoSuchElementException:
            continue
    return None


# =============================================================================
# Feature 1: User Login Tests
# =============================================================================

class TestUserLogin:

    def test_successful_login_standard_user(self, driver):
        """Successful login with valid standard user credentials."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_INPUT)))

        driver.find_element(By.CSS_SELECTOR, USERNAME_INPUT).send_keys("standard_user")
        driver.find_element(By.CSS_SELECTOR, PASSWORD_INPUT).send_keys("secret_sauce")
        driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()

        # Then I should be redirected to the products inventory page
        wait.until(EC.url_contains("inventory"))
        assert "inventory" in driver.current_url

        # And I should see the page title "Products"
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PAGE_TITLE)))
        assert title.text == "Products"

        # And I should see a list of available products
        items = driver.find_elements(By.CSS_SELECTOR, INVENTORY_ITEMS)
        assert len(items) > 0

    def test_successful_login_problem_user(self, driver):
        """Successful login with valid problem user credentials."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_INPUT)))

        driver.find_element(By.CSS_SELECTOR, USERNAME_INPUT).send_keys("problem_user")
        driver.find_element(By.CSS_SELECTOR, PASSWORD_INPUT).send_keys("secret_sauce")
        driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()

        wait.until(EC.url_contains("inventory"))
        assert "inventory" in driver.current_url

        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PAGE_TITLE)))
        assert title.text == "Products"

    def test_successful_login_performance_glitch_user(self, driver):
        """Successful login with valid performance glitch user credentials."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_INPUT)))

        driver.find_element(By.CSS_SELECTOR, USERNAME_INPUT).send_keys("performance_glitch_user")
        driver.find_element(By.CSS_SELECTOR, PASSWORD_INPUT).send_keys("secret_sauce")
        driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()

        # performance_glitch_user may be slow, use longer wait
        wait.until(EC.url_contains("inventory"))
        assert "inventory" in driver.current_url

        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PAGE_TITLE)))
        assert title.text == "Products"

    def test_failed_login_invalid_username(self, driver):
        """Failed login with invalid username."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_INPUT)))

        driver.find_element(By.CSS_SELECTOR, USERNAME_INPUT).send_keys("invalid_user")
        driver.find_element(By.CSS_SELECTOR, PASSWORD_INPUT).send_keys("secret_sauce")
        driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()

        error_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ERROR_MESSAGE)))
        assert "Epic sadface: Username and password do not match any user in this service" in error_el.text
        assert "inventory" not in driver.current_url

    def test_failed_login_invalid_password(self, driver):
        """Failed login with invalid password."""
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, USERNAME_INPUT)))

        driver.find_element(By.CSS_SELECTOR, USERNAME_INPUT).send_keys("standard_user")
        driver.find_element(By.CSS_SELECTOR, PASSWORD_INPUT).send_keys("wrong_password")
        driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()

        error_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ERROR_MESSAGE)))
        assert "Epic sadface: Username and password do not match any