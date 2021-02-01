import zipfile
from django import forms
from django.core.validators import FileExtensionValidator
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from schoolnn.models import Dataset


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

    def form_valid(self, form):
        self.handle_upload(self.request.FILES["file"])

        form.instance.user_id = 1
        return super().form_valid(form)

    def handle_upload(self, f):
        with open("storage/upload.zip", "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        with zipfile.ZipFile("storage/upload.zip", "r") as zip_ref:
            zip_ref.extractall("storage/data")


class DatasetUpdate(UpdateView):
    model = Dataset
    fields = []
