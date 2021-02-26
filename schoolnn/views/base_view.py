"""Basic views for template testing."""
from django.views.generic import TemplateView
from schoolnn.views.mixins import LoginRequiredMixin


class BaseView(LoginRequiredMixin, TemplateView):
    """Basic view for template testing."""

    template_name = "base/base.html"
