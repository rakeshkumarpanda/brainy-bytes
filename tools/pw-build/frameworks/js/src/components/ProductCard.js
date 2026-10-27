// One product card. Every locator starts from the card, so it never finds another product's button.
export class ProductCard {
  constructor(root) {
    this.root = root;
    this.price = root.locator('.price');
    this.button = root.getByRole('button');
  }

  async addToCart() {
    await this.root.getByRole('button', { name: 'Add to cart' }).click();
  }
}
