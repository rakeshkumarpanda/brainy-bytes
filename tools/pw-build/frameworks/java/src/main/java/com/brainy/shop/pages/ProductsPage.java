package com.brainy.shop.pages;

import com.brainy.shop.components.ProductCard;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

public class ProductsPage extends BasePage {
  public final Locator search;
  public final Locator cards;
  public final Locator noResults;

  public ProductsPage(Page page) {
    super(page, "/products");
    this.search = page.getByPlaceholder("Search products");
    this.cards = page.getByRole(AriaRole.LIST, new Page.GetByRoleOptions().setName("Products")).getByRole(AriaRole.LISTITEM);
    this.noResults = page.getByText("No products match your search");
  }

  public ProductCard card(String name) {
    return new ProductCard(cards.filter(new Locator.FilterOptions()
        .setHas(page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setName(name)))));
  }

  public void searchFor(String text) {
    search.fill(text);
  }
}
