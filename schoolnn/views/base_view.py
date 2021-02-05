"""Basic views for template testing."""
from django.views.generic import TemplateView


class BaseView(TemplateView):
    """Basic view for template testing."""

    template_name = "base/base.html"
