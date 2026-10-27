from playwright.sync_api import expect

from framework.data.products import DESK_LAMP, NOTEBOOK
from framework.pages.products_page import ProductsPage


def test_finds_the_lamp_by_name(products_page: ProductsPage):
    products_page.open()
    products_page.search_for("lamp")
    expect(products_page.cards).to_have_count(1)
    expect(products_page.card(DESK_LAMP.name).price).to_have_text(DESK_LAMP.price)


def test_says_so_when_nothing_matches(products_page: ProductsPage):
    products_page.open()
    products_page.search_for("piano")
    expect(products_page.no_results).to_be_visible()


def test_the_notebook_cannot_be_added(products_page: ProductsPage):
    products_page.open()
    expect(products_page.card(NOTEBOOK.name).button).to_be_disabled()
