import re

import pytest
from playwright.sync_api import expect

from framework.api.shop_api import ShopApi
from framework.data.products import WATER_BOTTLE
from framework.pages.cart_page import CartPage


@pytest.mark.cart
@pytest.mark.smoke
def test_places_an_order_for_a_cart_filled_through_the_api(session, api: ShopApi, cart_page: CartPage):
    api.add_to_cart(session.token, WATER_BOTTLE.id, 2)   # arrange through the API, test the UI
    cart_page.open()
    expect(cart_page.total).to_have_text("₹698")

    cart_page.place_order()
    expect(cart_page.status).to_have_text(re.compile(r"Order #\d+ placed"))
    expect(cart_page.header.cart_count).to_have_text("0")
