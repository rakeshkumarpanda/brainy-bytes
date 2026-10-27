package com.brainy.shop.data;

// Test accounts. Real projects read passwords from CI secrets, never from the repository.
public final class Users {
  public static final User ASHA = new User("asha@shop.example", secret("ASHA_PASSWORD", "s3cret"), "Asha");
  public static final User RAVI = new User("ravi@shop.example", secret("RAVI_PASSWORD", "admin123"), "Ravi");

  private Users() {}

  private static String secret(String name, String fallback) {
    String value = System.getenv(name);
    return value == null || value.isEmpty() ? fallback : value;
  }
}
