package com.brainy.shop.tests.products;

import com.brainy.shop.base.BaseTest;
import com.brainy.shop.data.Product;
import org.testng.annotations.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class SearchTest extends BaseTest {
  @Test
  public void findsTheLampByName() {
    productsPage.open();
    productsPage.searchFor("lamp");
    assertThat(productsPage.cards).hasCount(1);
    assertThat(productsPage.card(Product.DESK_LAMP.label).price).hasText(Product.DESK_LAMP.price);
  }

  @Test
  public void saysSoWhenNothingMatches() {
    productsPage.open();
    productsPage.searchFor("piano");
    assertThat(productsPage.noResults).isVisible();
  }

  @Test
  public void theNotebookCannotBeAdded() {
    productsPage.open();
    assertThat(productsPage.card(Product.NOTEBOOK.label).button).isDisabled();
  }
}
