import { test, expect } from '../../src/fixtures/index';
import { products } from '../../src/data/products';

test.describe('product search', () => {
  test('finds the lamp by name', async ({ productsPage }) => {
    await productsPage.open();
    await productsPage.searchFor('lamp');
    await expect(productsPage.cards).toHaveCount(1);
    await expect(productsPage.card(products.deskLamp.name).price).toHaveText(products.deskLamp.price);
  });

  test('says so when nothing matches', async ({ productsPage }) => {
    await productsPage.open();
    await productsPage.searchFor('piano');
    await expect(productsPage.noResults).toBeVisible();
  });

  test('the notebook cannot be added', async ({ productsPage }) => {
    await productsPage.open();
    await expect(productsPage.card(products.notebook.name).button).toBeDisabled();
  });
});
