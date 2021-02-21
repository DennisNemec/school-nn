from django.views import View
from django.shortcuts import render
from schoolnn.models import (
    Project,
    TrainingPass,
    TrainingStepMetrics,
)


class TrainingDetailView(View):
    """Get an overview over a training."""

    template_name = "training/training_details.html"

    def get(self, request, project_pk, training_pk):
        """Get an overview over a training."""
        project = Project.objects.get(id=project_pk)
        training_pass = TrainingPass.objects.get(id=training_pk)

        y_values_loss_training = []
        y_values_loss_validation = []
        y_values_accuracy_training = []
        y_values_accuracy_validation = []
        traing_step_metrics = TrainingStepMetrics.objects.filter(
            training_pass=training_pass
        )
        for traing_step_metric in traing_step_metrics:
            metrics = traing_step_metric.metrics_dict
            y_values_loss_training.append(metrics["training"]["loss"])
            y_values_loss_validation.append(metrics["validation"]["loss"])
            y_values_accuracy_training.append(metrics["training"]["accuracy"])
            y_values_accuracy_validation.append(
                metrics["validation"]["accuracy"]
            )
        x_values = list(range(len(y_values_loss_training)))

        context = {
            "project": project,
            "training_pass": training_pass,
            "x_values": x_values,
            "y_values_loss_training": y_values_loss_training,
            "y_values_loss_validation": y_values_loss_validation,
            "y_values_accuracy_training": y_values_accuracy_training,
            "y_values_accuracy_validation": y_values_accuracy_validation,
        }
        return render(request, self.template_name, context)
