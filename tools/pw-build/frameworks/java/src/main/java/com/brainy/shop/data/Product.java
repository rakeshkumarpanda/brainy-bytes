package com.brainy.shop.data;

// The products the tests use, with the ids the API expects
public enum Product {
  GEL_PEN(1, "Gel pen", "₹20"),
  COFFEE_MUG(2, "Coffee mug", "₹199"),
  DESK_LAMP(3, "Desk lamp", "₹1,299"),
  NOTEBOOK(4, "Notebook", "₹60"),
  WATER_BOTTLE(5, "Water bottle", "₹349");

  public final int id;
  public final String label;
  public final String price;

  Product(int id, String label, String price) {
    this.id = id;
    this.label = label;
    this.price = price;
  }
}
