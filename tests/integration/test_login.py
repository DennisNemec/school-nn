import asyncio
from tests.integration.integration_test_case import (
    BrowserIntegrationTestCase,
    make_sync,
)


class LoginTests(BrowserIntegrationTestCase):
    @make_sync
    async def test_login(self):
        await self.login(self.user.username, "wrong")
        content = await self.page.content()
        assert "Please enter a correct username" in content

        await self.login(self.user.username, self.password)
        content = await self.page.content()
        assert "Was ist SchoolNN?" in content

        logout_button = await self.page.Jx('//a[text()="Abmelden"]')
        await asyncio.wait(
            [logout_button[0].click(), self.page.waitForNavigation()]
        )

        assert "login" in self.page.url
