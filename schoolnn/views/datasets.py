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
from PIL import Image as PIL_Image, ImageOps
from schoolnn.models import Dataset, Label, Image, ImageLabel


class DatasetCreateForm(forms.ModelForm):
    """TODO."""

    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["zip"])]
    )

    class Meta:
        """TODO."""

        fields = ["file", "name"]
        model = Dataset


class DatasetList(ListView):
    """TODO."""

    queryset = Dataset.objects.order_by("-created_at")
    context_object_name = "datasets"
    template_name = "datasets/list.html"


class DatasetDetail(DetailView):
    """TODO."""

    model = Dataset
    template_name = "datasets/detail.html"


class DatasetCreate(CreateView):
    """Handles TODO."""

    form_class = DatasetCreateForm
    template_name = "datasets/form.html"

    object: Optional[Dataset] = None
    team_dir: Optional[str] = None
    upload_file: Optional[str] = None
    extract_dir: Optional[str] = None

    def form_valid(self, form: DatasetCreateForm):
        """Handle commited dataset create form."""
        self.object = form.save()
        if self.object is None:
            raise ValueError("Failed to parse the dataset create form")
        self.team_dir = "storage/1/"
        self.upload_file = "{}/upload_{}.zip".format(
            self.team_dir, self.object.id
        )
        self.extract_dir = "{}/{}_upload/".format(self.team_dir, self.object.id)

        self.handle_upload(self.request.FILES["file"])
        self.create_tags(self.object)

        shutil.rmtree(self.extract_dir)
        os.remove(self.upload_file)

        return HttpResponseRedirect(self.get_success_url())

    def handle_upload(self, zip_binary):
        """"Unzips uploaded zip."""
        os.makedirs(self.extract_dir, exist_ok=True)

        with open(self.upload_file, "wb+") as destination:
            for chunk in zip_binary.chunks():
                destination.write(chunk)

        with zipfile.ZipFile(self.upload_file, "r") as zip_ref:
            zip_ref.extractall(self.extract_dir)

    def create_tags(self, dataset: Dataset):
        """Create labels."""
        os.makedirs(
            os.path.join(str(self.team_dir), str(dataset.id)), exist_ok=True
        )

        for entry in os.scandir(self.extract_dir):
            if entry.is_dir():
                label = Label.objects.create(name=entry.name, dataset=dataset)
                self.process_images(entry, label, dataset)

    def process_images(self, path: os.DirEntry, label: Label, dataset: Dataset):
        """Save images center cropped."""
        for entry in os.scandir(path):
            image = Image.objects.create(dataset=dataset)
            ImageLabel.objects.create(label=label, image=image)
            image_pil = PIL_Image.open(entry.path)
            image_pil = ImageOps.fit(image_pil, (512, 512), PIL_Image.ANTIALIAS)
            image_pil.save(os.path.join(str(self.team_dir), image.path))


class DatasetUpdate(UpdateView):
    """TODO."""

    model = Dataset
    fields = ["name"]
    template_name = "datasets/form.html"


class DatasetDelete(DeleteView):
    """TODO."""

    model = Dataset
    success_url = reverse_lazy("dataset-list")
    template_name = "datasets/delete.html"
