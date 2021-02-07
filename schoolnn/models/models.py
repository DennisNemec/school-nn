"""All ORM models."""
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .training import TrainingParameter


class Workspace(models.Model):
    """The equivalent of a class room."""

    name = models.CharField(max_length=30)
    settings_json = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class User(models.Model):
    """User account of students, teachers and admins."""

    password = models.CharField(max_length=50)
    last_login = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    username = models.CharField(max_length=15)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    is_superadmin = models.BooleanField(default=False)
    is_workspaceadmin = models.BooleanField(default=False)
    workspace_id = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Dataset(models.Model):
    """Set of images used for training."""

    name = models.CharField(max_length=15)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    custom = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Image(models.Model):
    """Image of a dataset used for training."""

    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    filename = models.FilePathField()


class Label(models.Model):
    """Label existing in a database."""

    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)


class ImageLabel(models.Model):
    """Link between one image and one label."""

    label_id = models.ForeignKey(Label, on_delete=models.CASCADE)
    image_id = models.ForeignKey(Image, on_delete=models.CASCADE)


class Architecture(models.Model):
    """One sequential neural network architecure."""

    name = models.CharField(max_length=15)
    custom = models.BooleanField(default=False)
    architecture_json = models.JSONField
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Project(models.Model):
    """One project a user/student works on."""

    name = models.CharField(max_length=15)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    custom = models.BooleanField(default=False)
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    architecture_id = models.ForeignKey(Architecture, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class TrainingPass(models.Model):
    """One training pass of a project."""

    name = models.CharField(max_length=15)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    training_parameter_json = models.JSONField()
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    architecture_id = models.ForeignKey(Architecture, on_delete=models.CASCADE)
    model_weight = models.BinaryField()
    status = models.CharField(max_length=15)

    @property
    def training_parameter(self) -> TrainingParameter:
        """Get training parameter object from json representation."""
        return TrainingParameter.from_json(self.training_parameter_json)

    @training_parameter.setter
    def training_parameter(self, training_parameter: TrainingParameter):
        """Assign training parameter object and save json representation."""
        self.training_parameter_json = training_parameter.to_json()


class TrainingStepMetrics(models.Model):
    """Training and validation metrics of a training block/step."""

    traning_pass_id = models.ForeignKey(TrainingPass, on_delete=models.CASCADE)
    metrics_json = models.JSONField()


class Note(models.Model):
    """Note of an object."""

    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_type = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Visiblity(models.Model):
    """Defines who can see or edit an object."""

    permissions = models.JSONField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_type = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
