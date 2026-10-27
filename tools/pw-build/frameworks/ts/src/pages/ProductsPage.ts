import type { Page, Locator } from '@playwright/test';
import { ProductCard } from '../components/ProductCard';
import { BasePage } from './BasePage';

export class ProductsPage extends BasePage {
  readonly search: Locator;
  readonly cards: Locator;
  readonly noResults: Locator;

  constructor(page: Page) {
    super(page, '/products');
    this.search = page.getByPlaceholder('Search products');
    this.cards = page.getByRole('list', { name: 'Products' }).getByRole('listitem');
    this.noResults = page.getByText('No products match your search');
  }

  card(name: string) {
    return new ProductCard(this.cards.filter({ has: this.page.getByRole('heading', { name }) }));
  }

  async searchFor(text: string) {
    await this.search.fill(text);
  }
}
