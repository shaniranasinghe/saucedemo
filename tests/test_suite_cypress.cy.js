// cypress/e2e/saucedemo.cy.js

// Helper functions
const login = (username, password) => {
  cy.visit('https://www.saucedemo.com');
  cy.get('#user-name').clear().type(username);
  cy.get('#password').clear().type(password);
  cy.get('#login-button').click();
};

const addToCart = (productId) => {
  cy.get(productId).click();
};

// ============================================================
// FEATURE 1: User Login to Access Product Inventory
// ============================================================

describe('Feature 1: User Login to Access Product Inventory', () => {

  beforeEach(() => {
    cy.visit('https://www.saucedemo.com');
  });

  it('Successful login with valid standard user credentials', () => {
    cy.get('#user-name').type('standard_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.get('.title').should('have.text', 'Products');
    cy.get('.inventory_item').should('have.length.greaterThan', 0);
  });

  it('Successful login with valid problem user credentials', () => {
    cy.get('#user-name').type('problem_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.get('.title').should('have.text', 'Products');
  });

  it('Successful login with valid performance glitch user credentials', () => {
    cy.get('#user-name').type('performance_glitch_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.get('.title').should('have.text', 'Products');
  });

  it('Failed login with invalid username', () => {
    cy.get('#user-name').type('invalid_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.get('[data-test="error"]').should('contain', 'Epic sadface: Username and password do not match any user in this service');
    cy.url().should('eq', 'https://www.saucedemo.com/');
  });

  it('Failed login with invalid password', () => {
    cy.get('#user-name').type('standard_user');
    cy.get('#password').type('wrong_password');
    cy.get('#login-button').click();
    cy.get('[data-test="error"]').should('contain', 'Epic sadface: Username and password do not match any user in this service');
    cy.url().should('eq', 'https://www.saucedemo.com/');
  });

  it('Failed login with empty username', () => {
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.get('[data-test="error"]').should('contain', 'Epic sadface: Username is required');
    cy.url().should('eq', 'https://www.saucedemo.com/');
  });

  it('Failed login with empty password', () => {
    cy.get('#user-name').type('standard_user');
    cy.get('#login-button').click();
    cy.get('[data-test="error"]').should('contain', 'Epic sadface: Password is required');
    cy.url().should('eq', 'https://www.saucedemo.com/');
  });

  it('Failed login with both username and password empty', () => {
    cy.get('#login-button').click();
    cy.get('[data-test="error"]').should('contain', 'Epic sadface: Username is required');
    cy.url().should('eq', 'https://www.saucedemo.com/');
  });

  it('Failed login with locked out user credentials', () => {
    cy.get('#user-name').type('locked_out_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.get('[data-test="error"]').should('contain', 'Epic sadface: Sorry, this user has been locked out.');
    cy.url().should('eq', 'https://www.saucedemo.com/');
  });

  it('Session persists across page refresh after successful login', () => {
    login('standard_user', 'secret_sauce');
    cy.url().should('include', '/inventory.html');
    cy.reload();
    cy.url().should('include', '/inventory.html');
    cy.get('.title').should('have.text', 'Products');
    cy.get('.inventory_item').should('have.length.greaterThan', 0);
  });

  it('User can log out after successful login', () => {
    login('standard_user', 'secret_sauce');
    cy.url().should('include', '/inventory.html');
    cy.get('#react-burger-menu-btn').click();
    // TODO: selector for 'logout_sidebar_link' - using known selector
    cy.get('#logout_sidebar_link').click();
    cy.url().should('eq', 'https://www.saucedemo.com/');
    cy.visit('https://www.saucedemo.com/inventory.html');
    cy.url().should('eq', 'https://www.saucedemo.com/');
  });

  it('Successful login - standard_user (outline)', () => {
    cy.get('#user-name').type('standard_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.get('.title').should('have.text', 'Products');
  });

  it('Successful login - problem_user (outline)', () => {
    cy.get('#user-name').type('problem_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.get('.title').should('have.text', 'Products');
  });

  it('Successful login - performance_glitch_user (outline)', () => {
    cy.get('#user-name').type('performance_glitch_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.get('.title').should('have.text', 'Products');
  });

});

// ============================================================
// FEATURE 2: Remove Product from Shopping Cart
// ============================================================

describe('Feature 2: Remove Product from Shopping Cart', () => {

  beforeEach(() => {
    login('standard_user', 'secret_sauce');
    cy.url().should('include', '/inventory.html');
  });

  it('Successfully remove a single item from the cart via the product listing page', () => {
    // Add Sauce Labs Backpack
    cy.get('#add-to-cart-sauce-labs-backpack').click();
    cy.get('.shopping_cart_badge').should('have.text', '1');

    // Remove from product listing page
    // TODO: selector for 'remove_sauce_labs_backpack' button - using known pattern
    cy.get('#remove-sauce-labs-backpack').click();

    cy.get('.shopping_cart_badge').should('not.exist');
    cy.get('#add-to-cart-sauce-labs-backpack').should('exist');
  });

  it('Successfully remove a single item from the cart via the cart page', () => {
    cy.get('#add-to-cart-sauce-labs-bike-light').click();
    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    // TODO: selector for 'remove_sauce_labs_bike_light' in cart - using known pattern
    cy.get('#remove-sauce-labs-bike-light').click();

    cy.get('.cart_item').should('not.exist');
    cy.get('.shopping_cart_badge').should('not.exist');
  });

  it('Successfully remove one item when multiple items are in the cart', () => {
    cy.get('#add-to-cart-sauce-labs-backpack').click();
    cy.get('#add-to-cart-sauce-labs-bike-light').click();
    cy.get('#add-to-cart-sauce-labs-bolt-t-shirt').click();
    cy.get('.shopping_cart_badge').should('have.text', '3');

    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    cy.get('#remove-sauce-labs-bike-light').click();

    cy.get('.cart_item').should('not.contain', 'Sauce Labs Bike Light');
    cy.get('.cart_item').should('contain', 'Sauce Labs Backpack');
    cy.get('.cart_item').should('contain', 'Sauce Labs Bolt T-Shirt');
    cy.get('.shopping_cart_badge').should('have.text', '2');
  });

  it('Remove all items from the cart one by one', () => {
    cy.get('#add-to-cart-sauce-labs-backpack').click();
    cy.get('#add-to-cart-sauce-labs-bike-light').click();

    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    cy.get('#remove-sauce-labs-backpack').click();
    cy.get('#remove-sauce-labs-bike-light').click();

    cy.get('.cart_item').should('not.exist');
    cy.get('.shopping_cart_badge').should('not.exist');
  });

  it('Attempt to remove an item that is no longer in the cart', () => {
    cy.get('#add-to-cart-sauce-labs-backpack').click();
    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    cy.get('#remove-sauce-labs-backpack').click();
    cy.get('.cart_item').should('not.exist');

    // Attempt to click Remove again - button should not exist
    cy.get('#remove-sauce-labs-backpack').should('not.exist');
    cy.get('[data-test="error"]').should('not.exist');
    cy.get('.cart_item').should('not.exist');
  });

  it('Cart remains empty after removing item and navigating away and back', () => {
    cy.get('#add-to-cart-sauce-labs-fleece-jacket').click();
    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    cy.get('#remove-sauce-labs-fleece-jacket').click();
    cy.get('.cart_item').should('not.exist');

    cy.get('#continue-shopping').click();
    cy.url().should('include', '/inventory.html');

    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    cy.get('.cart_item').should('not.exist');
    cy.get('.shopping_cart_badge').should('not.exist');
  });

  it('Removed item button resets to Add to cart on product detail page', () => {
    cy.get('#add-to-cart-sauce-labs-backpack').click();

    // Navigate to product detail page for Sauce Labs Backpack
    cy.get('#item_4_title_link').click();
    cy.url().should('include', '/inventory-item.html');

    // TODO: selector for 'remove_button_on_product_detail_page' - using known pattern
    cy.get('#remove-sauce-labs-backpack').click();

    cy.get('#add-to-cart-sauce-labs-backpack').should('exist');
    cy.get('.shopping_cart_badge').should('not.exist');
  });

});

// ============================================================
// FEATURE 3: Complete Checkout Process
// ============================================================

describe('Feature 3: Complete Checkout Process', () => {

  beforeEach(() => {
    login('standard_user', 'secret_sauce');
    cy.url().should('include', '/inventory.html');
  });

  const fillCheckoutInfo = (firstName, lastName, postalCode) => {
    if (firstName) {
      cy.get('[data-test="firstName"]').type(firstName);
    }
    if (lastName) {
      cy.get('[data-test="lastName"]').type(lastName);
    }
    if (postalCode) {
      cy.get('[data-test="postalCode"]').type(postalCode);
    }
    cy.get('[data-test="continue"]').click();
  };

  it('Successful checkout with a single item', () => {
    cy.get('#add-to-cart-sauce-labs-backpack').click();
    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    cy.get('[data-test="checkout"]').click();
    cy.url().should('include', '/checkout-step-one.html');

    cy.get('[data-test="firstName"]').type('John');
    cy.get('[data-test="lastName"]').type('Doe');
    cy.get('[data-test="postalCode"]').type('12345');
    cy.get('[data-test="continue"]').click();

    cy.url().should('include', '/checkout-step-two.html');
    cy.get('.cart_item').should('contain', 'Sauce Labs Backpack');

    cy.get('[data-test="finish"]').click();
    cy.url().should('include', '/checkout-complete.html');
    cy.get('.complete-header').should('contain', 'Thank you for your order!');
    cy.get('.complete-text').should('contain', 'Your order has been dispatched');
  });

  it('Successful checkout with multiple items', () => {
    cy.get('#add-to-cart-sauce-labs-backpack').click();
    cy.get('#add-to-cart-sauce-labs-bike-light').click();
    cy.get('#add-to-cart-sauce-labs-bolt-t-shirt').click();

    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    cy.get('[data-test="checkout"]').click();
    cy.url().should('include', '/checkout-step-one.html');

    cy.get('[data-test="firstName"]').type('Jane');
    cy.get('[data-test="lastName"]').type('Smith');
    cy.get('[data-test="postalCode"]').type('67890');
    cy.get('[data-test="continue"]').click();

    cy.url().should('include', '/checkout-step-two.html');
    cy.get('.cart_item').should('contain', 'Sauce Labs Backpack');
    cy.get('.cart_item').should('contain', 'Sauce Labs Bike Light');
    cy.get('.cart_item').should('contain', 'Sauce Labs Bolt T-Shirt');

    cy.get('[data-test="finish"]').click();
    cy.url().should('include', '/checkout-complete.html');
    cy.get('.complete-header').should('contain', 'Thank you for your order!');
  });

  it('Checkout with correct total calculation', () => {
    cy.get('#add-to-cart-sauce-labs-backpack').click();
    cy.get('#add-to-cart-sauce-labs-bike-light').click();

    cy.get('.shopping_cart_link').click();
    cy.url().should('include', '/cart.html');

    cy.get('[data-test="checkout"]').click();
    cy.url().should('include', '/checkout-step-one.html');

    cy.get('[data-test="firstName"]').type('John');
    cy.get('[data-test="lastName"]').type('Doe');
    cy.get('[data-test="postalCode"]').type('12345');
    cy.get('[data-test="continue"]').click();