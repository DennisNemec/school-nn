"""Test schoolnn.training.one_hot_coding."""
from django.test import TestCase
from schoolnn.training.batch_generator import (
    BatchGeneratorTraining,
    BatchGeneratorValidation,
)
from schoolnn.training.load_dataset import (
    get_training_and_validation_images,
)
from ..sample_models import (
    BATCH_SIZE,
    LABEL_COUNT,
    get_test_training_pass,
)


class BatchGenerationTestCase(TestCase):
    """Test one hot coding methods."""

    def setUp(self):
        # project has three labels
        self.training_pass = get_test_training_pass(make_images_existing=True)
        self.project = self.training_pass.project

    def test_batch_generation_training(self):
        imgs_trainig, _ = get_training_and_validation_images(
            self.training_pass
        )

        generator_training = BatchGeneratorTraining(
            image_list=imgs_trainig,
            training_pass=self.training_pass,
            image_dimensions=(44, 44),
            processes_count=2,
            precalculate_batches_count=4,
        )

        # Frist round
        batch_count = 4
        generator_training.reset_batch_count(batch_count)
        # Now 4 batches should be generated in the background
        actual_batch_count = 0
        for batch in generator_training:
            x, y = batch
            actual_batch_count += 1
            assert x.shape == (BATCH_SIZE, 44, 44, 3)
            assert y.shape == (BATCH_SIZE, LABEL_COUNT)
        assert actual_batch_count == batch_count
        assert generator_training.batches_in_queue_not_fetched == 0
        assert self.training_pass.epoche_offset == batch_count * BATCH_SIZE
        offset_after_first_round = self.training_pass.epoche_offset

        # Second round
        actual_batch_count1 = 0
        batch_count1 = 16
        generator_training.reset_batch_count(batch_count1)
        # 16 batches should be generates in the background
        for batch in generator_training:
            x, y = batch
            actual_batch_count1 += 1
            assert x.shape == (BATCH_SIZE, 44, 44, 3)
            assert y.shape == (BATCH_SIZE, LABEL_COUNT)
        assert actual_batch_count1 == batch_count1
        assert generator_training.batches_in_queue_not_fetched == 0
        expected_offset = offset_after_first_round + batch_count1 * BATCH_SIZE
        assert self.training_pass.epoche_offset == expected_offset

    def test_batch_generation_validation(self):
        _, imgs_validation = get_training_and_validation_images(
            self.training_pass
        )
        generator_validation = BatchGeneratorValidation(
            image_list=imgs_validation,
            training_pass=self.training_pass,
            image_dimensions=(44, 44),
            processes_count=2,
            precalculate_batches_count=4,
        )

        expected_batch_count = 8
        generator_validation.reset_batch_count(expected_batch_count)
        assert len(generator_validation) == expected_batch_count
        actual_batch_count = 0
        for batch in generator_validation:
            x, y = batch
            actual_batch_count += 1
            assert x.shape == (BATCH_SIZE, 44, 44, 3)
            assert y.shape == (BATCH_SIZE, LABEL_COUNT)

        assert actual_batch_count == expected_batch_count
        assert generator_validation.batches_in_queue_not_fetched == 0
