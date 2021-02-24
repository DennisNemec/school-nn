from collections import namedtuple
from typing import List
from django.views import View
from django.shortcuts import render
from schoolnn.models import (
    Project,
    TrainingPass,
    TrainingStepMetrics,
)


TrainingPassGraphDetails = namedtuple(
    "TrainingPassGraphDetails",
    [
        "training_pass",
        "x_values",
        "y_values_training_loss",
        "y_values_training_accuracy",
        "y_values_validation_loss",
        "y_values_validation_accuracy",
    ],
)

# https://coolors.co/0892a5-06908f-0ca4a5-dbb68f-bb7e5d
_COLORLIST = [
    "rgb(8, 146, 165)",
    "rgb(6, 144, 143)",
    "rgb(12, 164, 165)",
    "rgb(219, 182, 143)",
    "rgb(187, 126, 93)",
]


def _training_pass_to_training_pass_graph_details(
    training_pass: TrainingPass,
) -> TrainingPassGraphDetails:
    training_metrics = TrainingStepMetrics.objects.filter(
        training_pass=training_pass
    )
    y_values_training_loss = []
    y_values_training_accuracy = []
    y_values_validation_loss = []
    y_values_validation_accuracy = []

    for metrics_item in training_metrics:
        metrics = metrics_item.metrics_dict
        y_values_training_loss.append(metrics["training"]["loss"])
        y_values_validation_loss.append(metrics["validation"]["loss"])
        y_values_training_accuracy.append(metrics["training"]["accuracy"])
        y_values_validation_accuracy.append(metrics["validation"]["accuracy"])

    return TrainingPassGraphDetails(
        training_pass=training_pass,
        x_values=list(range(len(y_values_training_loss))),
        y_values_training_loss=y_values_training_loss,
        y_values_validation_loss=y_values_validation_loss,
        y_values_training_accuracy=y_values_training_accuracy,
        y_values_validation_accuracy=y_values_validation_accuracy,
    )


class TrainingCompareView(View):
    """Get a comparison over all trainings passed."""

    def get(self, request, project_pk: int):
        """Get HTTP."""
        training_passes = TrainingPass.objects.filter(project_id=project_pk)

        training_pass_graph_details = [
            _training_pass_to_training_pass_graph_details(training_pass)
            for training_pass in training_passes
        ]

        longest_x_values: List[int] = []
        for graph_details in training_pass_graph_details:
            if len(graph_details.x_values) > len(longest_x_values):
                longest_x_values = graph_details.x_values

        training_pass_details_and_colors = []
        for i in range(len(training_pass_graph_details)):
            training_pass_details_and_colors.append(
                (
                    training_pass_graph_details[i],
                    _COLORLIST[i % len(_COLORLIST)],
                )
            )

        context = {
            "request": request,
            "project": Project.objects.get(id=project_pk),
            "training_pass_details_and_colors": training_pass_details_and_colors,
            "x_values": longest_x_values,
        }

        return render(
            request, "training/training_compare.html", context=context
        )
