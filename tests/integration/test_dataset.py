import os

from tests.integration.integration_test_case import (
    BrowserIntegrationTestCase,
    make_sync,
)


class TestDataset(BrowserIntegrationTestCase):
    @make_sync
    async def test_create_dataset(self):
        await self.login(self.user.username, self.password)

        await self.goto("dataset/")
        await self.submitXpath('//a[text()="Datensatz hinzufügen"]')

        assert "dataset/create" in self.page.url

        await self.page.type("#id_name", "Test Dataset")
        file_input = await self.page.J("#id_file")

        script_location = os.path.dirname(os.path.realpath(__file__))
        await file_input.uploadFile(
            script_location + "/../fixtures/images.zip"
        )

        await self.submitXpath('//input[@value="Datensatz hinzufügen"]')
        content = await self.page.content()

        assert "dataset/1" in self.page.url
        assert "Test Dataset" in content

        await self.submitXpath('//a[text()="Klasse bearbeiten"]')

        assert "label/1" in self.page.url

        await self.submitXpath('//a[text()="Klasseneinstellungen"]')
        await self.page.type("#name", "testlabel")
        await self.submitXpath('//input[@value="Speichern"]')

        content = await self.page.content()

        assert "label/1" in self.page.url
        assert "testlabel" in content

        await (await self.page.Jx("(//label/img)[1]"))[0].click()
        await self.submitXpath('//input[@value="Zuordnung löschen"]')

        await self.goto("dataset/1/labeleditor")

        content = await self.page.content()
        assert "alle Bilder sind klassifiziert" not in content

        await (await self.page.Jx("(//label/img)[1]"))[0].click()
        await self.submitXpath('//input[@value="Klasse zuordnen"]')

        content = await self.page.content()
        assert "alle Bilder sind klassifiziert" in content

        await self.goto("dataset/1/label/1")

        await self.submitXpath('//a[text()="Bild hinzufügen"]')
        file_input = await self.page.J("#id_file")
        await file_input.uploadFile(script_location + "/../fixtures/cat-1.jpg")

        await self.submitXpath('//input[@value="Bild hochladen"]')

        await self.submitXpath('//a[text()="Klasse löschen"]')
        content = await self.page.content()

        assert "wirklich löschen" in content

        await self.submitXpath('//input[@value="Klasse löschen"]')
        content = await self.page.content()
        assert "testlabel" not in content

        await self.goto("dataset/")
        content = await self.page.content()
        assert "Test Dataset" in content

        await self.goto("dataset/1")
        await self.submitXpath('//a[text()="Datensatz löschen"]')

        content = await self.page.content()
        assert "wirklich löschen" in content

        await self.submitXpath('//input[@value="Datensatz löschen"]')

        content = await self.page.content()
        assert "erfolgreich gelöscht" in content
