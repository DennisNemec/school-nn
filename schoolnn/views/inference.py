from typing import List
from io import BytesIO
import zipfile
from django import forms
from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.validators import FileExtensionValidator
from schoolnn.models import TrainingPass
from ..training import ClassificationResult, infere_images
from PIL import Image as ImagePillow, UnidentifiedImageError


class InferenceForm(forms.Form):
    """Form to infere with model."""

    file = forms.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "zip",
                    "jpg",
                    "jpeg",
                    "png",
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

        uploaded_file = form.cleaned_data["file"]

        uploaded_file_binary = BytesIO(uploaded_file.read())
        try:
            # Single images
            ImagePillow.open(uploaded_file_binary)
            uploaded_file_binary.seek(0)
            images_binary.append(uploaded_file_binary)
        except UnidentifiedImageError:
            # Multiple images in zip
            images_zipped = zipfile.ZipFile(uploaded_file_binary)
            for filename in images_zipped.namelist():
                images_filename.append(filename)
                images_binary.append(BytesIO(images_zipped.read(filename)))

        predictions = infere_images(
            training_pass=training_pass, images=images_binary
        )
        return predictions

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
            try:
                image_predictions = self._handle_valid_form(
                    form,
                    training_pass,
                )
            except zipfile.BadZipFile:
                messages.error(
                    request,
                    "Invalide Eingabedatei.\n"
                    "Die Eingabedatei ist keine valide Zipdatei",
                )
                return redirect(
                    "inference", project_pk=project_pk, training_pk=training_pk
                )

            context = {
                "request": request,
                "training_pass": training_pass,
                "image_predictions": image_predictions,
            }
            return render(request, "inference/inference_result.html", context)

        messages.error(
            request,
            "Invalide Eingabedatei.\n"
            "Bitte wöhle ein einzelnes Bild oder Bilder in einer Zipdatei.\n"
            "Erwartete Dateiendungen: zip, jpg, jpeg, png",
        )
        return redirect(
            "inference", project_pk=project_pk, training_pk=training_pk
        )
