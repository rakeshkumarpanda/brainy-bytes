// The header is on every page, so it is a component that every page object shares
export class Header {
  constructor(page) {
    const root = page.getByRole('banner');
    this.greeting = root.locator('#hello');
    this.cartCount = root.getByTestId('cart-count');
    this.signOut = root.getByRole('link', { name: 'Sign out' });
  }
}
