from playwright.sync_api import Page


# The header is on every page, so it is a component that every page object shares
class Header:
    def __init__(self, page: Page):
        root = page.get_by_role("banner")
        self.greeting = root.locator("#hello")
        self.cart_count = root.get_by_test_id("cart-count")
        self.sign_out = root.get_by_role("link", name="Sign out")
