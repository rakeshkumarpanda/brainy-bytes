import type { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class CartPage extends BasePage {
  readonly items: Locator;
  readonly total: Locator;
  readonly placeOrderButton: Locator;
  readonly status: Locator;

  constructor(page: Page) {
    super(page, '/cart');
    this.items = page.getByRole('table', { name: 'Cart items' }).locator('tbody tr');
    this.total = page.getByTestId('total');
    this.placeOrderButton = page.getByRole('button', { name: 'Place order' });
    this.status = page.getByRole('status');
  }

  async placeOrder() {
    this.page.once('dialog', dialog => dialog.accept());   // the shop asks to confirm the order
    await this.placeOrderButton.click();
  }
}
