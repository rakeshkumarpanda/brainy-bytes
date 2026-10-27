import { ProductCard } from '../components/ProductCard.js';
import { BasePage } from './BasePage.js';

export class ProductsPage extends BasePage {
  constructor(page) {
    super(page, '/products');
    this.search = page.getByPlaceholder('Search products');
    this.cards = page.getByRole('list', { name: 'Products' }).getByRole('listitem');
    this.noResults = page.getByText('No products match your search');
  }

  card(name) {
    return new ProductCard(this.cards.filter({ has: this.page.getByRole('heading', { name }) }));
  }

  async searchFor(text) {
    await this.search.fill(text);
  }
}
