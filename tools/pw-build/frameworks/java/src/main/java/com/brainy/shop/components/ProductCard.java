package com.brainy.shop.components;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.options.AriaRole;

// One product card. Every locator starts from the card, so it never finds another product's button.
public class ProductCard {
  public final Locator root;
  public final Locator price;
  public final Locator button;

  public ProductCard(Locator root) {
    this.root = root;
    this.price = root.locator(".price");
    this.button = root.getByRole(AriaRole.BUTTON);
  }

  public void addToCart() {
    root.getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Add to cart")).click();
  }
}
