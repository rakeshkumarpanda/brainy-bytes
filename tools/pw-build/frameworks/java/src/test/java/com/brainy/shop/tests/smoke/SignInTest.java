package com.brainy.shop.tests.smoke;

import com.brainy.shop.base.BaseTest;
import com.brainy.shop.data.Users;
import org.testng.annotations.Test;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@Test(groups = "smoke")
public class SignInTest extends BaseTest {
  @Test
  public void ashaSignsInWithTheRightPassword() {
    loginPage.open();
    loginPage.signIn(Users.ASHA);
    assertThat(productsPage.header.greeting).hasText("Hello, Asha");
  }

  @Test
  public void aWrongPasswordShowsAnError() {
    loginPage.open();
    loginPage.signIn(Users.ASHA.withPassword("wrong"));
    assertThat(loginPage.error).hasText("Wrong email or password");
  }
}
