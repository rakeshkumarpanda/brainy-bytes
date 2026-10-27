from playwright.sync_api import Page

from framework.data.users import User
from framework.pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.email = page.get_by_label("Email")
        self.password = page.get_by_label("Password")
        self.sign_in_button = page.get_by_role("button", name="Sign in")
        self.error = page.get_by_role("alert")

    def sign_in(self, user: User):
        self.email.fill(user.email)
        self.password.fill(user.password)
        self.sign_in_button.click()
