"""Basic views for template testing."""
from django.views.generic import TemplateView
from schoolnn.views.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):
    """Basic view for template testing."""

    template_name = "base/home.html"
