from typing import List
from io import BytesIO
import zipfile
from base64 import b64encode
from django import forms
from django.views import View
from django.shortcuts import render
from django.core.validators import FileExtensionValidator
from django.http import HttpResponse
from schoolnn.models import TrainingPass
from ..training import ClassificationResult, infere_images


class InferenceForm(forms.Form):
    """Form to infere with model."""

    file = forms.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "zip",  # "jpg", "jpeg", "png",
                ]
            )
        ]
    )


class InferenceView(View):
    """Test the trained model by doing inference."""

    def _handle_valid_form(
        self,
        form: InferenceForm,
        training_pass: TrainingPass,
    ) -> List[ClassificationResult]:

        images_binary = []
        images_filename = []

        images_zipped = zipfile.ZipFile(form.cleaned_data["file"])
        for filename in images_zipped.namelist():
            images_filename.append(filename)
            images_binary.append(BytesIO(images_zipped.read(filename)))

        predictions = infere_images(
            training_pass=training_pass, images=images_binary
        )
        return predictions

        result = []
        for binary_data, prediction in zip(images_binary, predictions):
            binary_data.seek(0)
            result.append((b64encode(binary_data.read()).decode(), prediction))

        return result

    def get(self, request, project_pk: int = 0, training_pk: int = 0):
        """Get site to start interference."""
        context = {
            "form": InferenceForm(),
            "training_pass": TrainingPass.objects.get(pk=training_pk),
        }
        return render(request, "inference/inference.html", context)

    def post(self, request, project_pk: int = 0, training_pk: int = 0):
        """Get everything classified."""

        form = InferenceForm(request.POST, request.FILES)

        if form.is_valid():
            training_pass = TrainingPass.objects.get(pk=training_pk)
            image_predictions = self._handle_valid_form(form, training_pass)
            context = {
                "request": request,
                "training_pass": training_pass,
                "image_predictions": image_predictions,
            }
            return render(request, "inference/inference_result.html", context)
        return HttpResponse("SAD: INVALID")
