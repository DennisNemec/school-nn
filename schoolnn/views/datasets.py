import os
import shutil
import zipfile
from django import forms
from django.core.validators import FileExtensionValidator
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from schoolnn.models import Dataset, Label, Image, Image_Label


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

    def form_valid(self, form: DatasetCreateForm):
        print(form.data)
        self.object = form.save()
        self.upload_file = "storage/1/upload_{}.zip".format(self.object.id)
        self.extract_dir = "storage/1/{}_upload/".format(self.object.id)
        self.store_dir = "storage/1/{}/".format(self.object.id)

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
        os.makedirs(self.store_dir, exist_ok=True)

        for entry in os.scandir(self.extract_dir):
            if entry.is_dir():
                label = Label.objects.create(name=entry.name, dataset=dataset)
                self.process_images(entry, label, dataset)

    def process_images(self, path: os.DirEntry, label: Label, dataset: Dataset):
        for entry in os.scandir(path):
            image = Image.objects.create(dataset=dataset)
            Image_Label.objects.create(label=label, image=image)
            os.rename(entry.path, os.path.join(self.store_dir, str(image.id)))


class DatasetUpdate(UpdateView):
    model = Dataset
    fields = []
