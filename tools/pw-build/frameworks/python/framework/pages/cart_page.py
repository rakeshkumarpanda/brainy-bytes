from playwright.sync_api import Page

from framework.pages.base_page import BasePage


class CartPage(BasePage):
    path = "/cart"

    def __init__(self, page: Page):
        super().__init__(page)
        self.items = page.get_by_role("table", name="Cart items").locator("tbody tr")
        self.total = page.get_by_test_id("total")
        self.place_order_button = page.get_by_role("button", name="Place order")
        self.status = page.get_by_role("status")

    def place_order(self):
        self.page.once("dialog", lambda dialog: dialog.accept())   # the shop asks to confirm the order
        self.place_order_button.click()
