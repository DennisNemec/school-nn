import asyncio
import os

from django.contrib.auth.hashers import make_password
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page

from schoolnn.models import User


def make_sync(old_f):
    """Make IntegrationTestCase async method sync."""

    def new_f(self, *args, **kwargs):
        assert hasattr(self, "_event_loop")
        loop = self._event_loop
        return loop.run_until_complete(old_f(self, *args, **kwargs))

    # new_f.__name__ == old_f.__name__

    return new_f


class BrowserIntegrationTestCase(StaticLiveServerTestCase):
    browser: Browser
    page: Page
    user: User
    password: str

    def setUp(self) -> None:
        self.password = "super_secure"
        self.user = User.objects.create(
            username="peter", password=make_password(self.password)
        )
        self._event_loop = asyncio.get_event_loop()
        self._event_loop.run_until_complete(self.asyncSetUp())

    def tearDown(self):
        self._event_loop.run_until_complete(self.asyncTearDown())
        self._event_loop.close()

    async def asyncSetUp(self):
        self.browser = await launch(
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            args=["--no-sandbox"],
            headless=os.environ.get("HEADLESS_TESTS", True) is True,
        )
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
