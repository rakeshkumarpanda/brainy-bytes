from dataclasses import replace

import pytest
from playwright.sync_api import expect

from framework.data.users import ASHA
from framework.pages.login_page import LoginPage
from framework.pages.products_page import ProductsPage

pytestmark = pytest.mark.smoke


def test_asha_signs_in_with_the_right_password(login_page: LoginPage, products_page: ProductsPage):
    login_page.open()
    login_page.sign_in(ASHA)
    expect(products_page.header.greeting).to_have_text("Hello, Asha")


def test_a_wrong_password_shows_an_error(login_page: LoginPage):
    login_page.open()
    login_page.sign_in(replace(ASHA, password="wrong"))
    expect(login_page.error).to_have_text("Wrong email or password")
