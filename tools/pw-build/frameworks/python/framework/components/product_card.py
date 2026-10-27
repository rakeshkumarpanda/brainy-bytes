from playwright.sync_api import Locator


# One product card. Every locator starts from the card, so it never finds another product's button.
class ProductCard:
    def __init__(self, root: Locator):
        self.root = root
        self.price = root.locator(".price")
        self.button = root.get_by_role("button")

    def add_to_cart(self):
        self.root.get_by_role("button", name="Add to cart").click()
