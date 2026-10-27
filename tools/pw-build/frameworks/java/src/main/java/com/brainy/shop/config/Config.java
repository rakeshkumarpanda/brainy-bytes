package com.brainy.shop.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

// Settings that change between machines (a laptop, CI, staging) live here and nowhere else.
// Order: -DbaseUrl=..., then the BASE_URL environment variable, then config.properties.
public final class Config {
  private static final Properties FILE = new Properties();

  static {
    try (InputStream in = Config.class.getResourceAsStream("/config.properties")) {
      if (in != null) FILE.load(in);
    } catch (IOException e) {
      throw new IllegalStateException("Cannot read config.properties", e);
    }
  }

  private Config() {}

  public static String get(String key, String envName) {
    String value = System.getProperty(key);
    if (value == null) value = System.getenv(envName);
    if (value == null) value = FILE.getProperty(key);
    return value;
  }

  public static String baseUrl() {
    return get("baseUrl", "BASE_URL");
  }

  public static boolean headless() {
    return Boolean.parseBoolean(get("headless", "HEADLESS"));
  }
}
