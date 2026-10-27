import type { Page } from '@playwright/test';
import { Header } from '../components/Header';

// What every page shares: the browser page, its address and the header
export class BasePage {
  readonly page: Page;
  readonly path: string;
  readonly header: Header;

  constructor(page: Page, path: string) {
    this.page = page;
    this.path = path;
    this.header = new Header(page);
  }

  async open() {
    await this.page.goto(this.path);
  }
}
