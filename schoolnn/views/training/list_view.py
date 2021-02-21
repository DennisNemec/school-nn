"""List all executed trainins."""
from django.views.generic import ListView
from django.db.models.query import QuerySet
from schoolnn.models import TrainingPass


class TrainingListView(ListView):
    """Get a list of all done training passes."""

    template_name = "training/training_overview.html"

    def dispatch(self, request, *args, **kwargs):
        self.project_pk = kwargs.get("project_pk")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return TrainingPass.objects.filter(project_id=self.project_pk)
