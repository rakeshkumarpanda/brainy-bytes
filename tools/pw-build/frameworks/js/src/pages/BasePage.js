import { Header } from '../components/Header.js';

// What every page shares: the browser page, its address and the header
export class BasePage {
  constructor(page, path) {
    this.page = page;
    this.path = path;
    this.header = new Header(page);
  }

  async open() {
    await this.page.goto(this.path);
  }
}
