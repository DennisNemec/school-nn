from tests.integration.integration_test_case import (
    BrowserIntegrationTestCase,
    make_sync,
)


class TestArchitecture(BrowserIntegrationTestCase):
    @make_sync
    async def test_create_architecture(self):
        await self.login(self.user.username, self.password)

        await self.goto("architectures/")
        await self.submitXpath('//a[text()="Architektur erstellen"]')

        assert "architectures/add" in self.page.url

        await self.page.type("#id_name", "Test")

        await self.submitXpath('//input[@value="Architektur erstellen"]')
        content = await self.page.content()

        assert "architectures/1" in self.page.url
        assert "Test" in content

        await self.submitXpath('//a[text()="Editor"]')
        assert "architectures/1/editor" in self.page.url

        await self.submitXpath('//button[text()="Speichern"]')
        assert "architectures/1" in self.page.url

        await self.submitXpath('//a[text()="Architektureinstellungen"]')
        assert "architectures/1/edit" in self.page.url

        await self.page.type("#id_name", "Test 2")

        await self.submitXpath('//input[@value="Speichern"]')
        content = await self.page.content()
        assert "Test 2" in content

        await self.submitXpath('//a[text()="Architektur löschen"]')
        content = await self.page.content()
        assert "wirklich löschen" in content

        await self.submitXpath('//input[@value="Architektur löschen"]')
        assert "architectures/" in self.page.url

        content = await self.page.content()
        assert "erfolgreich gelöscht" in content

        await self.page.reload()
        content = await self.page.content()
        assert "Test 2" not in content
