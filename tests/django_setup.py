"""Do the nasty import setup work of Django."""
import shutil
import django
from dotenv import load_dotenv
from os import environ, remove, makedirs
from uuid import uuid4
from django.core.management import call_command

TEST_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/schoolnn-testing-{}.sqlite3".format(uuid4().hex),
    }
}
TEST_STORAGE = "/tmp/schoolnnstorage-{}".format(uuid4().hex)
load_dotenv()
environ.setdefault("DJANGO_SETTINGS_MODULE", "schoolnn_app.settings")
environ.setdefault("STORAGE", TEST_STORAGE)
import schoolnn_app.settings  # noqa: 402

schoolnn_app.settings.DATABASES = TEST_DATABASES


def setup():
    django.setup()
    call_command("migrate", "schoolnn")
    makedirs(TEST_STORAGE, exist_ok=True)


def teardown():
    remove(schoolnn_app.settings.DATABASES["default"]["NAME"])
    shutil.rmtree(TEST_STORAGE)
