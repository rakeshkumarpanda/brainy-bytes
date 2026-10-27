import { test, expect } from '../../src/fixtures/index';
import { products } from '../../src/data/products';

test.describe('checkout', { tag: ['@cart', '@smoke'] }, () => {
  test('places an order for a cart filled through the API', async ({ session, api, cartPage }) => {
    await api.addToCart(session.token, products.waterBottle.id, 2);   // arrange through the API, test the UI
    await cartPage.open();
    await expect(cartPage.total).toHaveText('₹698');

    await cartPage.placeOrder();
    await expect(cartPage.status).toHaveText(/Order #\d+ placed/);
    await expect(cartPage.header.cartCount).toHaveText('0');
  });
});
