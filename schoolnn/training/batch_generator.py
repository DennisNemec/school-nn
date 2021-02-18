"""Generate batches for training and validation."""
from random import shuffle, seed, randint
from typing import List, Tuple, Optional
from numpy import array
from keras import utils
from imgaug import augmenters
from PIL import Image as PillowImage
from .one_hot_coding import get_one_hot_encoder
from ..models import (
    TrainingPass,
    Image,
    Dataset,
    AugmentationOptions,
)


def numpy_image_batch_to_x_batch(
    numpy_image_batch: array,
    dimensions: Tuple[int, int],
    augmenter: Optional[augmenters.Augmenter] = None,
) -> array:
    """Augment and resize a batch of images."""
    resize_params = {"height": dimensions[0], "width": dimensions[1]}
    resizer = augmenters.Resize(resize_params)

    if augmenter:
        new_augmenter = augmenters.Sequential([augmenter, resizer])
    else:
        new_augmenter = resizer

    images_augmented = new_augmenter(images=numpy_image_batch)
    images_augmented = numpy_image_batch

    images_augmented = images_augmented.astype("float32")
    images_augmented -= 128.0  # Shift to zero centered
    images_augmented *= 0.01  # Shift to standard deivation of one
    return images_augmented


# Warning: Undefined random behaviour (seed race condition) when
# doing parallel trainings.


class BatchGeneratorTraining(utils.Sequence):
    """Generate batches for model fitting."""

    def __init__(
        self,
        image_list: List[Image],
        training_pass: TrainingPass,
        batch_count: int,
        image_dimensions: Tuple[int, int],
    ):
        """Get a generator for batches of images and labels for training."""
        self.training_pass = training_pass
        self.batch_size = training_pass.training_parameter.batch_size
        self.dataset: Dataset = training_pass.dataset_id
        self.one_hot_encoder = get_one_hot_encoder(dataset=self.dataset)
        self.image_list = image_list[:]
        self.image_list_shuffled = image_list[:]
        self.batch_count = batch_count
        self.image_dimensions = image_dimensions

        seed(self.training_pass.id + self.training_pass.epoche)
        shuffle(self.image_list_shuffled)

        augmentation_options: AugmentationOptions = (
            training_pass.training_parameter.augmentation_options
        )
        self.augmenter = augmentation_options.get_augmenter()

    def _generate_xraw_y(self) -> Optional[Tuple[array, array]]:
        if self.training_pass.epoche_offset >= len(self.image_list_shuffled):
            self.training_pass.epoche += 1
            self.training_pass.epoche_offset = 0

            # copy, to not shuffle original
            self.image_list_shuffled = self.image_list[:]
            seed(self.training_pass.id + self.training_pass.epoche)
            shuffle(self.image_list_shuffled)

        image = self.image_list_shuffled[self.training_pass.epoche_offset]
        if image.label is None:
            self.training_pass.epoche_offset += 1
            return None

        x_raw = array(
            PillowImage.open(image.get_path(self.dataset)).convert("RGB")
        )

        y = self.one_hot_encoder(image.label)
        self.training_pass.epoche_offset += 1

        return x_raw, y

    def on_epoch_end(self):
        self.training_pass.save(update_fields=["epoche", "epoche_offset"])

    def __len__(self) -> int:
        return self.batch_count

    def __getitem__(self, index):
        batch_x_raw = []
        batch_y = []
        while len(batch_y) < self.batch_size:
            x_y_values = self._generate_xraw_y()
            if x_y_values is None:
                # Label was not set
                continue
            x_raw, y = x_y_values
            batch_x_raw.append(x_raw)
            batch_y.append(y)

        batch_x = numpy_image_batch_to_x_batch(
            array(batch_x_raw),
            dimensions=self.image_dimensions,
            augmenter=self.augmenter,
        )

        return array(batch_x), array(batch_y)


class BatchGeneratorValidation(utils.Sequence):
    """Generate batches for model validation."""

    def __init__(
        self,
        image_list: List[Image],
        training_pass: TrainingPass,
        batch_count: int,
        image_dimensions: Tuple[int, int],
    ):
        """Get a generator for batches of images and labels for training."""
        self.training_pass = training_pass
        self.batch_size = training_pass.training_parameter.batch_size
        self.dataset: Dataset = training_pass.dataset_id
        self.one_hot_encoder = get_one_hot_encoder(dataset=self.dataset)
        self.image_list = image_list[:]
        self.image_list_shuffled = image_list[:]
        self.batch_count = batch_count
        self.image_dimensions = image_dimensions
        self.offset = randint(0, len(self.image_list))  # nosec

        seed(self.training_pass.id + self.training_pass.epoche)
        shuffle(self.image_list_shuffled)

    def _generate_xraw_y(self) -> Optional[Tuple[array, array]]:
        image_index = self.offset % len(self.image_list_shuffled)
        image = self.image_list_shuffled[image_index]

        if image.label is None:
            self.offset += 1
            return None

        x_raw = array(
            PillowImage.open(image.get_path(self.dataset)).convert("RGB")
        )

        y = self.one_hot_encoder(image.label)
        self.offset += 1

        return x_raw, y

    def on_epoch_end(self):
        pass

    def __len__(self) -> int:
        return self.batch_count

    def __getitem__(self, index):
        batch_x_raw = []
        batch_y = []
        while len(batch_y) < self.batch_size:
            x_y_values = self._generate_xraw_y()
            if x_y_values is None:
                # Label was not set
                continue
            x_raw, y = x_y_values
            batch_x_raw.append(x_raw)
            batch_y.append(y)

        batch_x = numpy_image_batch_to_x_batch(
            array(batch_x_raw),
            dimensions=self.image_dimensions,
            augmenter=None,
        )

        return array(batch_x), array(batch_y)
