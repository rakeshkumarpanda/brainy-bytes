package com.brainy.shop.data;

public record User(String email, String password, String name) {
  public User withPassword(String other) {
    return new User(email, other, name);
  }
}
