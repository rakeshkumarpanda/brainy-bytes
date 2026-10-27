package com.brainy.shop.components;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

// The header is on every page, so it is a component that every page object shares
public class Header {
  public final Locator greeting;
  public final Locator cartCount;
  public final Locator signOut;

  public Header(Page page) {
    Locator root = page.getByRole(AriaRole.BANNER);
    this.greeting = root.locator("#hello");
    this.cartCount = root.getByTestId("cart-count");
    this.signOut = root.getByRole(AriaRole.LINK, new Locator.GetByRoleOptions().setName("Sign out"));
  }
}
