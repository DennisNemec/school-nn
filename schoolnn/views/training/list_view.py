"""List all executed trainins."""
from django.views.generic import ListView
from django.db.models.query import QuerySet
from schoolnn.models import TrainingPass, Project
from schoolnn.views.mixins import UserIsProjectOwnerMixin


class TrainingListView(UserIsProjectOwnerMixin, ListView):
    """Get a list of all done training passes."""

    template_name = "training/training_overview.html"
    ordering = "-pk"
    model = TrainingPass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = Project.objects.get(pk=self.kwargs["project_pk"])
        return context

    def get_queryset(self) -> QuerySet:
        return (
            super().get_queryset().filter(project_id=self.kwargs["project_pk"])
        )
