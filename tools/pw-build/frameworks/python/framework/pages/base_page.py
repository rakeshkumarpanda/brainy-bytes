from playwright.sync_api import Page

from framework.components.header import Header


# What every page shares: the browser page, its address and the header
class BasePage:
    path = "/"

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)

    def open(self):
        self.page.goto(self.path)
