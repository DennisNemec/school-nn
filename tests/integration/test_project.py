from tests.integration.integration_test_case import (
    IntegrationTestCase,
    make_sync,
)


class TestProject(IntegrationTestCase):
    @make_sync
    async def test_create_project(self):
        await self.login(self.user.username, self.password)

        await self.goto("project/")
        await self.submitXpath('//a[text()="Projekt erstellen"]')

        assert "project/create" in self.page.url

        await self.page.type("#id_name", "Test Projekt")

        await self.submitXpath('//input[@value="Projekt erstellen"]')
        content = await self.page.content()

        assert "project/1" in self.page.url
        assert "Test Projekt" in content

        await self.submitXpath('//a[text()="Projekteinstellungen"]')

        assert "project/1/edit" in self.page.url
        await self.page.type("#name", "Test 2")
        await self.submitXpath('//input[@value="Speichern"]')

        content = await self.page.content()
        assert "Test 2" in content

        await self.submitXpath('//a[text()="Modellarchitektur bearbeiten"]')
        assert "project/1/edit/architecture/" in self.page.url

        await self.submitXpath('//button[text()="Speichern"]')
        content = await self.page.content()
        assert "erfolgreich gespeichert" in content

        await self.submitXpath('//a[text()="← Zurück"]')

        await self.submitXpath('//a[text()="Trainingsparameter bearbeiten"]')
        assert "project/1/edit/parameters/" in self.page.url

        await self.submitXpath('//input[@value="Parameter speichern"]')
        content = await self.page.content()
        assert "erfolgreich gespeichert" in content

        await self.submitXpath('//a[text()="← Zurück"]')

        await self.submitXpath('//a[text()="Trainingsdurchläufe verwalten"]')
        assert "project/1/training" in self.page.url

        await self.submitXpath('//a[text()="Training starten"]')
        await self.page.type("#id_name", "Test Training")

        # await self.submitXpath('//a[text()="Starten"]')

        await self.goto("project/1")

        await self.submitXpath('//a[text()="Projekt löschen"]')
        content = await self.page.content()
        assert "wirklich löschen" in content

        await self.submitXpath('//input[@value="Projekt löschen"]')
        content = await self.page.content()
        assert "erfolgreich gelöscht" in content
