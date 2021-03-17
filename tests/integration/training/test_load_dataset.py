"""Test schoolnn.training.load_dataset."""
from django.test import TestCase
from schoolnn.training.load_dataset import get_training_and_validation_images
from ..sample_models import (
    get_test_training_pass,
    VALIDATION_SPLIT,
)


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
        training_pass = get_test_training_pass()
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
        training_pass = get_test_training_pass()
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
