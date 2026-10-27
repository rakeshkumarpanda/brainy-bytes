import { BasePage } from './BasePage.js';

export class LoginPage extends BasePage {
  constructor(page) {
    super(page, '/login');
    this.email = page.getByLabel('Email');
    this.password = page.getByLabel('Password');
    this.signInButton = page.getByRole('button', { name: 'Sign in' });
    this.error = page.getByRole('alert');
  }

  async signIn(user) {
    await this.email.fill(user.email);
    await this.password.fill(user.password);
    await this.signInButton.click();
  }
}
