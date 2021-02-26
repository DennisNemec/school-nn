"""All ORM models."""

import os
from typing import Optional
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from json import loads
from .training import TrainingParameter
from schoolnn.resources.static.layer_list import default_layers
from schoolnn.resources.static.default_training_parameters import (
    default_training_parameters,
)
from django.contrib.auth.models import UserManager


class TimestampedModelMixin(models.Model):
    """Abstract class that manages the created-
    and updated-timestamp for other classes"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Workspace(TimestampedModelMixin):
    """The equivalent of a class room."""

    name = models.CharField(max_length=30)
    settings_json = models.JSONField()

    def __str__(self):
        return "%s" % (self.name)


class User(AbstractUser, TimestampedModelMixin):
    """User account of students, teachers and admins."""

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, null=True
    )
    objects = UserManager()

    def get_absolute_url(self):
        return reverse("user-detail", kwargs={"pk": self.pk})


class Dataset(TimestampedModelMixin):
    """Set of images used for training."""

    name = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    custom = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        """Web link to this dataset."""
        return reverse("dataset-detail", kwargs={"pk": self.pk})

    @property
    def workspace_dir(self) -> str:
        """
        The folder containing all data for the workspace this resource
        belongs to.
        """
        return "storage/1"

    @property
    def extract_dir(self) -> str:
        """ Temporary folder used to extract the uploaded zip. """
        return "{}/{}_upload/".format(self.workspace_dir, self.id)

    @property
    def upload_file(self) -> str:
        """ Location for the temporary stored upload zip. """
        return "{}/{}_upload.zip".format(self.workspace_dir, self.id)

    @property
    def dir(self) -> str:
        """ Location where images from this dataset are stored. """
        return "{}/{}/".format(self.workspace_dir, self.id)


class Label(models.Model):
    """Label existing in a database."""

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)


class Image(models.Model):
    """Image of a dataset used for training."""

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=True)

    @property
    def filename(self) -> str:
        """Get the filename, derived from the id and zero padded."""
        return "{:0>8}.jpg".format(self.id)

    @property
    def path(self) -> str:
        """Get the path of this image in the workspace storage folder."""
        return self.get_path(self.dataset)

    def get_path(self, dataset: Dataset) -> str:
        """Get the path of this image in the workspace storage folder."""
        return os.path.join(dataset.dir, self.filename)


class Architecture(TimestampedModelMixin):
    """One sequential neural network architecture."""

    name = models.CharField(max_length=15, null=True)
    custom = models.BooleanField(default=False)
    architecture_json = models.JSONField(default=default_layers)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("architecture-detail", kwargs={"pk": self.pk})


class Project(TimestampedModelMixin):
    """One project a user/student works on."""

    name = models.CharField(max_length=15)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    custom = models.BooleanField(default=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True)
    architecture = models.ForeignKey(
        Architecture, on_delete=models.CASCADE, null=True
    )
    training_parameter_json = models.JSONField(
        null=True, default=default_training_parameters
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Direct URL to this project"""
        return reverse("project-details", kwargs={"pk": self.pk})

    @property
    def training_parameter(self) -> Optional[TrainingParameter]:
        """Get training parameter object from json representation."""
        if self.training_parameter_json is None:
            return None
        return TrainingParameter.from_json(self.training_parameter_json)

    @training_parameter.setter
    def training_parameter(self, training_parameter: TrainingParameter):
        """Assign training parameter object and save json representation."""
        self.training_parameter_json = training_parameter.to_json()


class TrainingPass(models.Model):
    """One training pass of a project."""

    name = models.CharField(max_length=15)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    training_parameter_json = models.JSONField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    architecture = models.ForeignKey(Architecture, on_delete=models.CASCADE)
    model_weights = models.BinaryField()
    status = models.CharField(max_length=15)
    epoche = models.IntegerField(default=0)
    epoche_offset = models.IntegerField(default=0)

    @property
    def training_parameter(self) -> TrainingParameter:
        """Get training parameter object from json representation."""
        return TrainingParameter.from_json(self.training_parameter_json)

    @training_parameter.setter
    def training_parameter(self, training_parameter: TrainingParameter):
        """Assign training parameter object and save json representation."""
        self.training_parameter_json = training_parameter.to_json()

    @property
    def duration_human_readable(self) -> str:
        """Get training duration readable for humans."""
        duration = self.end_datetime - self.start_datetime
        result = ""
        if duration.days:
            result += "{} {} ".format(duration.days, "Tage")
        result += "{:02}:{:02}:{:02}h".format(
            int(duration.seconds / 3600),
            int(duration.seconds / 60) % 60,
            int(duration.seconds) % 60,
        )
        return result

    @property
    def latest_training_step_metrics(self) -> Optional["TrainingStepMetrics"]:
        """Get latest training step of this training pass."""
        last = TrainingStepMetrics.objects.filter(training_pass=self).order_by(
            "-id"
        )[:1]
        # last is array
        if last:
            return last[0]
        return None


class TrainingStepMetrics(models.Model):
    """Training and validation metrics of a training block/step."""

    training_pass = models.ForeignKey(TrainingPass, on_delete=models.CASCADE)
    metrics_json = models.JSONField()

    @property
    def metrics_dict(self) -> dict:
        """Obtain metrics as dictionary."""
        return loads(self.metrics_json)


class Note(TimestampedModelMixin):
    """Note of an object."""

    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_type = GenericForeignKey("content_type", "object_id")


class Visiblity(TimestampedModelMixin):
    """Defines who can see or edit an object."""

    permissions = models.JSONField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_type = GenericForeignKey("content_type", "object_id")
