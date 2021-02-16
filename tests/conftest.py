"""First file to be called by pytest."""
from os import environ
from dotenv import load_dotenv
import django

load_dotenv()
environ.setdefault("DJANGO_SETTINGS_MODULE", "schoolnn_app.settings")
django.setup()
