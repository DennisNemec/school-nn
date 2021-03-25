"""Do the nasty import setup work of Django."""
import shutil
import django
from dotenv import load_dotenv
from os import environ, remove, makedirs
from uuid import uuid4
from django.core.management import call_command

TEST_STORAGE = "/tmp/schoolnnstorage-{}".format(uuid4().hex)
TEST_DATABASE = "/tmp/schoolnn-testing-{}.sqlite3".format(uuid4().hex)
environ.setdefault("DJANGO_SETTINGS_MODULE", "schoolnn_app.settings")
environ.setdefault("STORAGE", TEST_STORAGE)
environ.setdefault("DATABASE", TEST_DATABASE)
load_dotenv()
import schoolnn_app.settings  # noqa: 402


def setup():
    django.setup()
    call_command("migrate")
    makedirs(TEST_STORAGE, exist_ok=True)


def teardown():
    remove(TEST_DATABASE)
    shutil.rmtree(TEST_STORAGE)
