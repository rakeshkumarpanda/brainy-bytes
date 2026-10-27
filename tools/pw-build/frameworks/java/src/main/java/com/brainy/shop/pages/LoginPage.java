package com.brainy.shop.pages;

import com.brainy.shop.data.User;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

public class LoginPage extends BasePage {
  public final Locator email;
  public final Locator password;
  public final Locator signInButton;
  public final Locator error;

  public LoginPage(Page page) {
    super(page, "/login");
    this.email = page.getByLabel("Email");
    this.password = page.getByLabel("Password");
    this.signInButton = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in"));
    this.error = page.getByRole(AriaRole.ALERT);
  }

  public void signIn(User user) {
    email.fill(user.email());
    password.fill(user.password());
    signInButton.click();
  }
}
