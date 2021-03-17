"""Contains all HTTP handling having to do with datasets."""
from django import forms
from django.core.validators import FileExtensionValidator
from django.http import HttpResponseRedirect
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    FormView,
    DeleteView,
)
from django.contrib.messages.views import SuccessMessageMixin
from schoolnn.models import Dataset, Label, Image
from django.urls import reverse, reverse_lazy
from django.contrib import messages


class LabelEditForm(forms.ModelForm):
    """Label form for editing a label."""

    class Meta:
        """Django meta information."""

        fields = ["name"]
        model = Label


class LabelCreateForm(forms.ModelForm):
    """Label form for creating a label."""

    class Meta:
        fields = ["name", "dataset"]
        model = Label


class LabelDeletionForm(forms.ModelForm):
    """Label form for deletion of an image of a given label."""

    image_id_list = forms.ModelMultipleChoiceField(
        required=True,
        queryset=Image.objects.none(),
        label="",
    )

    class Meta:
        model = Label
        fields = ["id"]

    def __init__(self, dataset_id=None, pk=None, *args, **kwargs):
        super(LabelDeletionForm, self).__init__(*args, **kwargs)
        self.fields["image_id_list"].queryset = Image.objects.filter(label=pk)


class LabelCreateImageForm(forms.ModelForm):
    """ Label add image form with additional file field. """

    file = forms.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpeg", "gif", "png", "jpg"]
            )
        ],
        label="Bild",
    )

    class Meta:
        model = Image
        exclude = ["label", "dataset"]


class LabelDetailView(UpdateView):
    """ Standard view of a label """

    model = Label
    template_name = "datasets/label/label_details.html"
    form_class = LabelDeletionForm

    def get_form_kwargs(self):
        kwargs = super(LabelDetailView, self).get_form_kwargs()
        kwargs.update(self.kwargs)
        return kwargs

    def remove_label(self, image_id):
        """ Removes a label of a given image. """

        Image.objects.filter(pk=image_id).update(label=None)

    def form_valid(self, form):
        """
        Used for label deletion.
        """

        image_ids = form.data.getlist("image_id_list")

        for image in image_ids:
            self.remove_label(image)

        count = len(image_ids)
        image_word = "Bild" if count == 1 else "Bilder"

        messages.success(
            self.request,
            f"{count} {image_word} erfolgreich aus der Klasse entfernt.",
        )

        return HttpResponseRedirect(
            reverse("dataset-label-details", kwargs=self.kwargs)
        )


class LabelCreateView(SuccessMessageMixin, CreateView):
    """ Label creation view with a form. """

    model = Label
    form_class = LabelCreateForm
    template_name = "datasets/label/create_label.html"
    success_message = "Klasse erfolgreich erstellt."

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("dataset-details", kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        """ Retrieve required information for template """
        context = super().get_context_data(**kwargs)
        context["dataset"] = Dataset.objects.get(pk=self.kwargs["pk"])

        return context


class LabelUpdateView(SuccessMessageMixin, UpdateView):
    """Update an existing label."""

    model = Label
    form_class = LabelEditForm
    template_name = "datasets/label/edit_label.html"

    success_message = "Klasse erfolgreich bearbeitet."

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("dataset-label-details", kwargs=self.kwargs)


class LabelCreateImageView(FormView):
    """ Adds an image to a given label """

    form_class = LabelCreateImageForm
    model = Image
    template_name = "datasets/label/add_image.html"

    def get_context_data(self, **kwargs):
        """ Retrieve required information for template """
        context = super().get_context_data(**kwargs)

        if "pk" not in self.kwargs or "dataset_id" not in self.kwargs:
            raise ValueError("Kein Datensatz oder Label angegeben")

        context["label"] = Label.objects.get(pk=self.kwargs["pk"])
        context["dataset"] = Dataset.objects.get(pk=self.kwargs["dataset_id"])

        return context

    def copy_file(self, image_binary, path):
        """ Copy uploaded image to specified folder """

        with open(path, "wb+") as destination:
            for chunk in image_binary.chunks():
                destination.write(chunk)

    def create_image_entry(self, label, dataset):
        """ Insert an Image object into the database """

        image_obj = Image(label=label, dataset=dataset)
        image_obj.save()

        return image_obj

    def form_invalid(self, form: LabelCreateImageForm):
        """ Return to the label page if the form is invalid """

        messages.error(
            self.request, "Das Bild konnte nicht hochgeladen werden."
        )

        return HttpResponseRedirect(
            reverse(
                "dataset-label-details",
                kwargs={
                    "pk": self.get_context_data()["label"].id,
                    "dataset_id": self.get_context_data()["dataset"].id,
                },
            )
        )

    def form_valid(self, form: LabelCreateImageForm):
        """ validate the form and create a new image """

        label = Label.objects.get(pk=form.data["label"])
        dataset = Dataset.objects.get(pk=form.data["dataset"])
        image = self.create_image_entry(label, dataset)
        self.copy_file(self.request.FILES["file"], image.path)

        messages.success(self.request, "Bild erfolgreich hochgeladen.")

        return HttpResponseRedirect(
            reverse(
                "dataset-label-details",
                kwargs={
                    "pk": self.get_context_data()["label"].id,
                    "dataset_id": self.get_context_data()["dataset"].id,
                },
            )
        )


class LabelDeleteView(DeleteView):
    model = Label
    template_name = "datasets/label/delete_label.html"

    def delete(self, request, *args, **kwargs):
        label = self.get_object()
        self.success_url = reverse_lazy(
            "dataset-edit", kwargs={"pk": label.dataset.id}
        )

        messages.success(self.request, "Klasse erfolgreich gelöscht.")

        return super().delete(request, args, kwargs)
