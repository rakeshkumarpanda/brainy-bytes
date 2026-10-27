package com.brainy.shop.tests.cart;

import com.brainy.shop.base.BaseTest;
import com.brainy.shop.data.Product;
import org.testng.annotations.Test;

import java.util.regex.Pattern;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@Test(groups = {"cart", "smoke"})
public class CheckoutTest extends BaseTest {
  @Test
  public void placesAnOrderForACartFilledThroughTheApi() {
    String token = signInThroughApi();
    api.addToCart(token, Product.WATER_BOTTLE.id, 2);   // arrange through the API, test the UI
    cartPage.open();
    assertThat(cartPage.total).hasText("₹698");

    cartPage.placeOrder();
    assertThat(cartPage.status).hasText(Pattern.compile("Order #\\d+ placed"));
    assertThat(cartPage.header.cartCount).hasText("0");
  }
}
