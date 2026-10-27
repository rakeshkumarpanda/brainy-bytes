import { BasePage } from './BasePage.js';

export class CartPage extends BasePage {
  constructor(page) {
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
