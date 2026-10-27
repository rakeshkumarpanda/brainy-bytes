package com.brainy.shop.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

public class CartPage extends BasePage {
  public final Locator items;
  public final Locator total;
  public final Locator placeOrderButton;
  public final Locator status;

  public CartPage(Page page) {
    super(page, "/cart");
    this.items = page.getByRole(AriaRole.TABLE, new Page.GetByRoleOptions().setName("Cart items")).locator("tbody tr");
    this.total = page.getByTestId("total");
    this.placeOrderButton = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Place order"));
    this.status = page.getByRole(AriaRole.STATUS);
  }

  public void placeOrder() {
    page.onceDialog(dialog -> dialog.accept());   // the shop asks to confirm the order
    placeOrderButton.click();
  }
}
