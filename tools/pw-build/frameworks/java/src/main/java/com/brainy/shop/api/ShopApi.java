package com.brainy.shop.api;

import com.brainy.shop.data.User;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.APIResponse;
import com.microsoft.playwright.options.RequestOptions;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

// Fast set up through the API, so UI tests only click what they are testing
public class ShopApi {
  private final APIRequestContext request;

  public ShopApi(APIRequestContext request) {
    this.request = request;
  }

  public String signIn(User user) {
    APIResponse response = request.post("/api/login",
        RequestOptions.create().setData(Map.of("email", user.email(), "password", user.password())));
    if (!response.ok()) throw new IllegalStateException("Sign in failed for " + user.email() + ": " + response.status());
    Matcher token = Pattern.compile("\"token\":\"(\\w+)\"").matcher(response.text());
    if (!token.find()) throw new IllegalStateException("No token in " + response.text());
    return token.group(1);
  }

  public void addToCart(String token, int productId, int qty) {
    APIResponse response = request.post("/api/cart", RequestOptions.create()
        .setData(Map.of("productId", productId, "qty", qty))
        .setHeader("Authorization", "Bearer " + token));
    if (!response.ok()) throw new IllegalStateException("Could not add product " + productId + ": " + response.status());
  }
}
