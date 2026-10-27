import { test, expect } from '../../src/fixtures/index';
import { users } from '../../src/data/users';

test.describe('sign in', { tag: '@smoke' }, () => {
  test('Asha signs in with the right password', async ({ loginPage, productsPage }) => {
    await loginPage.open();
    await loginPage.signIn(users.asha);
    await expect(productsPage.header.greeting).toHaveText('Hello, Asha');
  });

  test('a wrong password shows an error', async ({ loginPage }) => {
    await loginPage.open();
    await loginPage.signIn({ ...users.asha, password: 'wrong' });
    await expect(loginPage.error).toHaveText('Wrong email or password');
  });
});
