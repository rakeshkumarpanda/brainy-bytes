import { test as base, expect } from '@playwright/test';
import { ShopApi } from '../api/ShopApi';
import { users } from '../data/users';
import type { User } from '../data/users';
import { CartPage } from '../pages/CartPage';
import { LoginPage } from '../pages/LoginPage';
import { ProductsPage } from '../pages/ProductsPage';

type Session = { user: User; token: string };

type Fixtures = {
  api: ShopApi;
  session: Session;
  loginPage: LoginPage;
  productsPage: ProductsPage;
  cartPage: CartPage;
};

// Every test file imports test and expect from here instead of from @playwright/test
export const test = base.extend<Fixtures>({
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
