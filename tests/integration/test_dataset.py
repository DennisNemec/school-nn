import os

from tests.integration.integration_test_case import (
    IntegrationTestCase,
    make_sync,
)


class TestDataset(IntegrationTestCase):
    @make_sync
    async def test_create_dataset(self):
        await self.login(self.user.username, self.password)

        await self.goto("datasets/")
        await self.submitXpath('//a[text()="Datensatz hinzufügen"]')

        assert "datasets/add" in self.page.url

        await self.page.type("#id_name", "Test Dataset")
        file_input = await self.page.J("#id_file")

        script_location = os.path.dirname(os.path.realpath(__file__))
        await file_input.uploadFile(
            script_location + "/../fixtures/images.zip"
        )

        await self.submitXpath('//input[@value="Datensatz hinzufügen"]')
        content = await self.page.content()

        assert "datasets/1" in self.page.url
        assert "Test Dataset" in content
