import pytest
from playwright.sync_api import expect

from framework.data.products import COFFEE_MUG, DESK_LAMP
from framework.pages.cart_page import CartPage
from framework.pages.products_page import ProductsPage

pytestmark = pytest.mark.cart


def test_adds_two_products_from_their_cards(session, products_page: ProductsPage, cart_page: CartPage):
    products_page.open()
    expect(products_page.header.greeting).to_have_text(f"Hello, {session.user.name}")
    products_page.card(DESK_LAMP.name).add_to_cart()
    products_page.card(COFFEE_MUG.name).add_to_cart()
    expect(products_page.header.cart_count).to_have_text("2")

    cart_page.open()
    expect(cart_page.items).to_have_count(2)
    expect(cart_page.total).to_have_text("₹1,498")
