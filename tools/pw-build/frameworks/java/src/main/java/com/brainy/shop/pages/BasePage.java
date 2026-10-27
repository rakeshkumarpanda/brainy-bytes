package com.brainy.shop.pages;

import com.brainy.shop.components.Header;
import com.microsoft.playwright.Page;

// What every page shares: the browser page, its address and the header
public abstract class BasePage {
  protected final Page page;
  private final String path;
  public final Header header;

  protected BasePage(Page page, String path) {
    this.page = page;
    this.path = path;
    this.header = new Header(page);
  }

  public void open() {
    page.navigate(path);
  }
}
