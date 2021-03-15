"""Test schoolnn.training.load_dataset."""
from datetime import datetime
from django.test import TestCase
from schoolnn.training.load_dataset import get_training_and_validation_images
from schoolnn.models import (
    TrainingParameter,
    TerminationCondition,
    LossFunction,
    Optimizer,
    AugmentationOptions,
    TrainingPass,
    Dataset,
    Label,
    Image,
    Architecture,
    User,
    Project,
)

VALIDATION_SPLIT = 0.1


def _get_test_training_pass() -> TrainingPass:
    dataset = Dataset.objects.create(name="")
    label0 = Label.objects.create(dataset=dataset, name="L0")
    label1 = Label.objects.create(dataset=dataset, name="L1")
    for _ in range(1000):
        Image.objects.create(dataset=dataset, label=label0)
    for _ in range(1000):
        Image.objects.create(dataset=dataset, label=label1)

    user = User.objects.create()

    architecture = Architecture.objects.create(
        name="",
        architecture_json={},
        user=user,
    )

    project = Project.objects.create(
        name="",
        user=user,
        architecture=architecture,
    )

    training_parameter = TrainingParameter(
        validation_split=VALIDATION_SPLIT,
        learning_rate=0.1,
        termination_condition=TerminationCondition(),
        batch_size=32,
        loss_function=LossFunction.CATEGORICAL_CROSSENTROPY,
        optimizer=Optimizer.ADADELTA,
        augmentation_options=AugmentationOptions.all_activated(),
    )

    training_pass = TrainingPass.objects.create(
        name="",
        dataset_id=dataset,
        project=project,
        architecture=architecture,
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
        training_parameter_json=training_parameter.to_dict(),
    )
    return training_pass


class LoadDatasetTestCase(TestCase):
    """Test load_dataset with DB rollback."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # do stuff

    @classmethod
    def tearDownClass(cls):
        # do stuff
        super().tearDownClass()

    def test_validation_split(self):
        training_pass = _get_test_training_pass()
        training_imgs, validation_imgs = get_training_and_validation_images(
            training_pass
        )

        img_count_tra = len(training_imgs)
        img_count_val = len(validation_imgs)

        validation_split_calced = img_count_val / (
            img_count_val + img_count_tra
        )

        assert abs(validation_split_calced - VALIDATION_SPLIT) < 0.001

    def test_label_distribution(self):
        training_pass = _get_test_training_pass()
        training_imgs, validation_imgs = get_training_and_validation_images(
            training_pass
        )

        label_counts_val = {}
        for img in validation_imgs:
            label = img.label.name
            label_counts_val[label] = label_counts_val.get(label, 0) + 1

        label_counts_tra = {}
        for img in training_imgs:
            label = img.label.name
            label_counts_tra[label] = label_counts_tra.get(label, 0) + 1

        assert label_counts_tra.keys() == label_counts_val.keys()
