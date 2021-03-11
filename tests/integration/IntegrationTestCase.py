import asyncio
import os
from typing import Coroutine, Any

from django.contrib.auth.hashers import make_password
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page

from schoolnn.models import User


class IntegrationTestCase(StaticLiveServerTestCase):
    browser: Browser
    page: Page
    user: User
    password: str

    def setUp(self) -> None:
        self.password = "super_secure"
        self.user = User.objects.create(
            username="peter", password=make_password(self.password)
        )

    @staticmethod
    def get_browser() -> Coroutine[Any, Any, Browser]:
        return launch(
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            args=["--no-sandbox"],
            headless=os.environ.get("HEADLESS_TESTS", True) is True,
        )

    async def asyncSetUp(self):
        self.browser = await self.get_browser()
        self.page = await self.browser.newPage()

    async def asyncTearDown(self):
        await self.browser.close()

    async def login(self, username, password):
        await self.page.goto("{}{}".format(self.live_server_url, "/login/"))

        await self.page.type("#id_username", username)
        await self.page.type("#id_password", password)

        await asyncio.wait(
            [self.page.click("[type=submit]"), self.page.waitForNavigation()]
        )
