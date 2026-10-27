import type { Page, Locator } from '@playwright/test';
import type { User } from '../data/users';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  readonly email: Locator;
  readonly password: Locator;
  readonly signInButton: Locator;
  readonly error: Locator;

  constructor(page: Page) {
    super(page, '/login');
    this.email = page.getByLabel('Email');
    this.password = page.getByLabel('Password');
    this.signInButton = page.getByRole('button', { name: 'Sign in' });
    this.error = page.getByRole('alert');
  }

  async signIn(user: User) {
    await this.email.fill(user.email);
    await this.password.fill(user.password);
    await this.signInButton.click();
  }
}
