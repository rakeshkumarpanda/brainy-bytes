package com.brainy.shop.tests.cart;

import com.brainy.shop.base.BaseTest;
import com.brainy.shop.data.Product;
import org.testng.annotations.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@Test(groups = "cart")
public class AddToCartTest extends BaseTest {
  @Test
  public void addsTwoProductsFromTheirCards() {
    signInThroughApi();
    productsPage.open();
    assertThat(productsPage.header.greeting).hasText("Hello, Asha");
    productsPage.card(Product.DESK_LAMP.label).addToCart();
    productsPage.card(Product.COFFEE_MUG.label).addToCart();
    assertThat(productsPage.header.cartCount).hasText("2");

    cartPage.open();
    assertThat(cartPage.items).hasCount(2);
    assertThat(cartPage.total).hasText("₹1,498");
  }
}
