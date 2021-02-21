"""Basic views for template testing."""
from django.views.generic import TemplateView
from schoolnn.views.mixins import AuthMixin


class BaseView(AuthMixin, TemplateView):
    """Basic view for template testing."""

    template_name = "base/base.html"
