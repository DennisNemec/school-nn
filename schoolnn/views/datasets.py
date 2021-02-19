"""Contains all HTTP handling having to do with datasets."""
import os
import shutil
import zipfile
from typing import Optional

from django import forms
from django.core.validators import FileExtensionValidator
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.db import transaction
from PIL import Image as PIL_Image, ImageOps
from schoolnn.models import Dataset, Label, Image


class DatasetCreateForm(forms.ModelForm):
    """Dataset form that contains an additional file field."""

    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["zip"])]
    )

    class Meta:
        """Django meta information."""

        fields = ["file", "name"]
        model = Dataset


class DatasetList(ListView):
    """Lists datasets."""

    queryset = Dataset.objects.order_by("-created_at")
    context_object_name = "datasets"
    template_name = "datasets/list.html"


class DatasetDetail(DetailView):
    """Show dataset details."""

    model = Dataset
    template_name = "datasets/detail.html"


class DatasetCreate(CreateView):
    """Handles creation of datasets."""

    form_class = DatasetCreateForm
    template_name = "datasets/form.html"

    object: Optional[Dataset] = None

    def form_valid(self, form: DatasetCreateForm):
        """Handle committed dataset create form."""
        self.object = form.save()
        if self.object is None:
            raise ValueError("Failed to parse the dataset create form")

        self.handle_upload(self.request.FILES["file"])
        self.create_tags(self.object)

        shutil.rmtree(self.object.extract_dir)
        os.remove(self.object.upload_file)

        return HttpResponseRedirect(self.get_success_url())

    def handle_upload(self, zip_binary):
        """"Unzips uploaded zip."""
        os.makedirs(self.object.extract_dir, exist_ok=True)

        with open(self.object.upload_file, "wb+") as destination:
            for chunk in zip_binary.chunks():
                destination.write(chunk)

        with zipfile.ZipFile(self.object.upload_file, "r") as zip_ref:
            zip_ref.extractall(self.object.extract_dir)

    def create_tags(self, dataset: Dataset):
        """Create labels."""
        os.makedirs(os.path.join(dataset.dir), exist_ok=True)

        for entry in os.scandir(dataset.extract_dir):
            if entry.is_dir():
                label = Label.objects.create(name=entry.name, dataset=dataset)
                self.process_images(entry, label, dataset)

    @transaction.atomic
    def process_images(
        self, path: os.DirEntry, label: Label, dataset: Dataset
    ):
        """Save images center cropped."""
        for entry in os.scandir(path):
            image = Image.objects.create(dataset=dataset, label=label)
            image_pil = PIL_Image.open(entry.path)
            width, height = image_pil.size
            target_size = min([width, height, 512])
            image_pil = ImageOps.fit(
                image_pil, (target_size, target_size), PIL_Image.ANTIALIAS
            )
            image_pil.save(image.path)


class DatasetUpdate(UpdateView):
    """Update an existing dataset."""

    model = Dataset
    fields = ["name"]
    template_name = "datasets/form.html"


class DatasetDelete(DeleteView):
    """Delete an existing dataset."""

    model = Dataset
    success_url = reverse_lazy("dataset-list")
    template_name = "datasets/delete.html"

    def delete(self, request, *args, **kwargs):
        dataset = self.get_object()
        shutil.rmtree(dataset.dir)

        return super().delete(request, args, kwargs)
