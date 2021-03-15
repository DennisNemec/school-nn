"""First file to be called by pytest."""
from .django_setup import setup, teardown

# Run setup before importing other tests
setup()  # required for importing models


def pytest_sessionstart(session):
    """Run once before testing begins."""


def pytest_sessionfinish(session):
    """Run once after all testing is done."""
    teardown()
