import { test, expect } from '../../src/fixtures/index.js';
import { products } from '../../src/data/products.js';

test.describe('cart', { tag: '@cart' }, () => {
  test('adds two products from their cards', async ({ session, productsPage, cartPage }) => {
    await productsPage.open();
    await expect(productsPage.header.greeting).toHaveText(`Hello, ${session.user.name}`);
    await productsPage.card(products.deskLamp.name).addToCart();
    await productsPage.card(products.coffeeMug.name).addToCart();
    await expect(productsPage.header.cartCount).toHaveText('2');

    await cartPage.open();
    await expect(cartPage.items).toHaveCount(2);
    await expect(cartPage.total).toHaveText('₹1,498');
  });
});
