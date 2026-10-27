import { test as base, expect } from '@playwright/test';
import { ShopApi } from '../api/ShopApi.js';
import { users } from '../data/users.js';
import { CartPage } from '../pages/CartPage.js';
import { LoginPage } from '../pages/LoginPage.js';
import { ProductsPage } from '../pages/ProductsPage.js';

// Every test file imports test and expect from here instead of from @playwright/test
export const test = base.extend({
  api: async ({ request }, use) => {
    await use(new ShopApi(request));
  },
  // A fresh session made through the API: fast, and no two tests share a cart
  session: async ({ api, page }, use) => {
    const token = await api.signIn(users.asha);
    await page.addInitScript(value => window.localStorage.setItem('token', value), token);
    await use({ user: users.asha, token });
  },
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  productsPage: async ({ page }, use) => {
    await use(new ProductsPage(page));
  },
  cartPage: async ({ page }, use) => {
    await use(new CartPage(page));
  },
});

export { expect };
