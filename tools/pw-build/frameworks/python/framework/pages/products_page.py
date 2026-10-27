from playwright.sync_api import Page

from framework.components.product_card import ProductCard
from framework.pages.base_page import BasePage


class ProductsPage(BasePage):
    path = "/products"

    def __init__(self, page: Page):
        super().__init__(page)
        self.search = page.get_by_placeholder("Search products")
        self.cards = page.get_by_role("list", name="Products").get_by_role("listitem")
        self.no_results = page.get_by_text("No products match your search")

    def card(self, name: str) -> ProductCard:
        return ProductCard(self.cards.filter(has=self.page.get_by_role("heading", name=name)))

    def search_for(self, text: str):
        self.search.fill(text)
