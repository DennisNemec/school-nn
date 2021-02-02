"""Manages TODO."""
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Workspace(models.Model):
    name = models.CharField(max_length=30)
    settings_json = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class User(models.Model):
    password =models.CharField(max_length=50)
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
    name = models.CharField(max_length=15)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    custom = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Image(models.Model):
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    filename = models.FilePathField()


class Label(models.Model):
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)

class Image_Label(models.Model):
    label_id = models.ForeignKey(Label, on_delete=models.CASCADE)
    image_id = models.ForeignKey(Image, on_delete=models.CASCADE)

class Architecture(models.Model):
    name = models.CharField(max_length=15)
    custom = models.BooleanField(default=False)
    architecture_json = models.JSONField
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def get_absolute_url(self):
        return reverse('architecture-detail', kwargs={'pk': self.pk})


class Project(models.Model):
    name = models.CharField(max_length=15)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    custom = models.BooleanField(default=False)
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    architecture_id = models.ForeignKey(Architecture, on_delete=models.CASCADE)
    traning_pass_id = models.ForeignKey(Training_Pass, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


class Training_Pass(models.Model):
    name = models.CharField(max_length=15)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    training_parameter_json = models.JSONField()
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    architecture_id = models.ForeignKey(Architecture, on_delete=models.CASCADE)
    model_weight = models.BinaryField()
    status = models.CharField(max_length=15)

class Training_Step_Metrics(models.Model):
    traning_pass_id = models.ForeignKey(Training_Pass, on_delete=models.CASCADE)
    metrics_json = models.JSONField()

class Note(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_type = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

class Visiblity(models.Model):
    permissions = models.JSONField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_type = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()


