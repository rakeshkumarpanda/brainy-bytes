package com.brainy.shop.base;

import com.brainy.shop.api.ShopApi;
import com.brainy.shop.config.Config;
import com.brainy.shop.data.User;
import com.brainy.shop.data.Users;
import com.brainy.shop.pages.CartPage;
import com.brainy.shop.pages.LoginPage;
import com.brainy.shop.pages.ProductsPage;
import com.microsoft.playwright.APIRequest;
import com.microsoft.playwright.APIRequestContext;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.Tracing;
import org.testng.ITestResult;
import org.testng.annotations.AfterClass;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.BeforeMethod;

import java.nio.file.Paths;

// Every test class extends BaseTest. TestNG runs classes in parallel, and each class has its own
// Playwright and browser, so nothing is shared between threads.
public abstract class BaseTest {
  private Playwright playwright;
  private Browser browser;
  private APIRequestContext request;
  private BrowserContext context;
  protected Page page;
  protected ShopApi api;
  protected LoginPage loginPage;
  protected ProductsPage productsPage;
  protected CartPage cartPage;

  @BeforeClass(alwaysRun = true)        // alwaysRun: also when a group such as smoke is chosen
  public void launchBrowser() {
    playwright = Playwright.create();
    browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(Config.headless()));
    request = playwright.request().newContext(new APIRequest.NewContextOptions().setBaseURL(Config.baseUrl()));
    api = new ShopApi(request);
  }

  @BeforeMethod(alwaysRun = true)
  public void openPage() {
    context = browser.newContext(new Browser.NewContextOptions().setBaseURL(Config.baseUrl()));
    context.tracing().start(new Tracing.StartOptions().setScreenshots(true).setSnapshots(true));
    page = context.newPage();
    loginPage = new LoginPage(page);
    productsPage = new ProductsPage(page);
    cartPage = new CartPage(page);
  }

  // A fresh session made through the API: fast, and no two tests share a cart
  protected String signInThroughApi(User user) {
    String token = api.signIn(user);
    context.addInitScript("window.localStorage.setItem('token', '" + token + "')");
    return token;
  }

  protected String signInThroughApi() {
    return signInThroughApi(Users.ASHA);
  }

  // Report listeners call this when a test fails. TestNG calls them before closePage(), so the page is still open.
  public byte[] screenshot() {
    return page.screenshot();
  }

  @AfterMethod(alwaysRun = true)
  public void closePage(ITestResult result) {
    if (result.isSuccess()) {
      context.tracing().stop();
    } else {                                      // keep a trace only for a failed test
      String name = getClass().getSimpleName() + "." + result.getMethod().getMethodName();
      context.tracing().stop(new Tracing.StopOptions().setPath(Paths.get("traces", name + ".zip")));
    }
    context.close();
  }

  @AfterClass(alwaysRun = true)
  public void closeBrowser() {
    request.dispose();
    playwright.close();
  }
}
