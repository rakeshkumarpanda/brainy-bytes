from dataclasses import dataclass
from typing import Generator

import pytest
from playwright.sync_api import Page, Playwright

from framework import config
from framework.api.shop_api import ShopApi
from framework.data.users import ASHA, User
from framework.pages.cart_page import CartPage
from framework.pages.login_page import LoginPage
from framework.pages.products_page import ProductsPage


@dataclass
class Session:
    user: User
    token: str


@pytest.fixture(scope="session")
def base_url() -> str:
    return config.BASE_URL                      # pytest-playwright uses it for page.goto("/login")


@pytest.fixture
def api(playwright: Playwright, base_url: str) -> Generator[ShopApi, None, None]:
    request = playwright.request.new_context(base_url=base_url)
    yield ShopApi(request)
    request.dispose()


# A fresh session made through the API: fast, and no two tests share a cart
@pytest.fixture
def session(api: ShopApi, page: Page) -> Session:
    token = api.sign_in(ASHA)
    page.add_init_script(f"window.localStorage.setItem('token', '{token}')")
    return Session(ASHA, token)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def products_page(page: Page) -> ProductsPage:
    return ProductsPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)
