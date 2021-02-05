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
from schoolnn.models import Dataset, Label, Image, ImageLabel
from PIL import Image as PIL_Image, ImageOps


class DatasetCreateForm(forms.ModelForm):
    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["zip"])]
    )

    class Meta:
        fields = ["file", "name"]
        model = Dataset


class DatasetList(ListView):
    queryset = Dataset.objects.order_by("-created_at")
    context_object_name = "datasets"
    template_name = "datasets/list.html"


class DatasetDetail(DetailView):
    model = Dataset
    template_name = "datasets/detail.html"


class DatasetCreate(CreateView):
    form_class = DatasetCreateForm
    template_name = "datasets/form.html"

    object: Optional[Dataset] = None
    team_dir: Optional[str] = None
    upload_file: Optional[str] = None
    extract_dir: Optional[str] = None

    def form_valid(self, form: DatasetCreateForm):
        self.object = form.save()
        self.team_dir = "storage/1/"
        self.upload_file = "{}/upload_{}.zip".format(self.team_dir,
                                                     self.object.id)
        self.extract_dir = "{}/{}_upload/".format(self.team_dir,
                                                  self.object.id)

        self.handle_upload(self.request.FILES["file"])
        self.create_tags(self.object)

        shutil.rmtree(self.extract_dir)
        os.remove(self.upload_file)

        return HttpResponseRedirect(self.get_success_url())

    def handle_upload(self, f):
        os.makedirs(self.extract_dir, exist_ok=True)

        with open(self.upload_file, "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        with zipfile.ZipFile(self.upload_file, "r") as zip_ref:
            zip_ref.extractall(self.extract_dir)

    def create_tags(self, dataset: Dataset):
        os.makedirs(os.path.join(str(self.team_dir), str(dataset.id)),
                    exist_ok=True)

        for entry in os.scandir(self.extract_dir):
            if entry.is_dir():
                label = Label.objects.create(name=entry.name,
                                             dataset=dataset)
                self.process_images(entry, label, dataset)

    def process_images(self, path: os.DirEntry, label: Label,
                       dataset: Dataset):
        for entry in os.scandir(path):
            image = Image.objects.create(dataset=dataset)
            ImageLabel.objects.create(label=label, image=image)
            im = PIL_Image.open(entry.path)
            im = ImageOps.fit(im, (512, 512), PIL_Image.ANTIALIAS)
            im.save(os.path.join(str(self.team_dir), image.path))


class DatasetUpdate(UpdateView):
    model = Dataset
    fields = ['name']
    template_name = "datasets/form.html"


class DatasetDelete(DeleteView):
    model = Dataset
    success_url = reverse_lazy('dataset-list')
    template_name = "datasets/delete.html"
