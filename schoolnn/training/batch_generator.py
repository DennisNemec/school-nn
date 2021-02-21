"""Generate batches for training and validation."""
from multiprocessing.pool import Pool, AsyncResult
from queue import Queue
from random import shuffle, seed, randint
from io import BytesIO
from typing import List, Tuple, Optional, Union
from numpy import array
from keras import utils
from imgaug import augmenters
from PIL import Image as PillowImage
from PIL.JpegImagePlugin import JpegImageFile
from .one_hot_coding import get_one_hot_encoder
from ..models import (
    TrainingPass,
    Image,
)


def image_to_numpy_array(
    image: Union[str, bytes, BytesIO, JpegImageFile],
    target_dimensions: Tuple[int, int],
) -> array:
    """Get an image as a numpy array."""
    if isinstance(image, (str, BytesIO)):
        image_pil = PillowImage.open(image)
    elif isinstance(image, bytes):
        image_pil = PillowImage.open(BytesIO(image))
    elif isinstance(image, JpegImageFile):
        image_pil = image
    else:
        raise TypeError("Got unknown image type!")

    image_pil_resized = image_pil.resize(target_dimensions)
    return array(image_pil_resized.convert("RGB"))


def numpy_image_batch_to_x_batch(
    numpy_image_batch: array,
    augmenter: Optional[augmenters.Augmenter] = None,
) -> array:
    """Augment and resize a batch of images."""
    if augmenter:
        images_augmented = augmenter(images=numpy_image_batch)
    else:
        images_augmented = numpy_image_batch
    images_augmented = images_augmented.astype("float32")
    images_augmented -= 128.0  # Shift to zero centered
    images_augmented *= 0.01  # Shift to standard deivation of one
    return images_augmented


class BatchTask:
    """Task to calculate one batch, used by process pool"""

    def __init__(self, filepaths: List[str], labels_hotencoded: List[array]):
        """Initialize batch task."""
        self.filepaths = filepaths
        self.labels_hotencoded = labels_hotencoded

    def process(
        self, image_dimensions: Tuple[int, int]
    ) -> Tuple[array, array]:
        """Do the heavy work and get x and y of a batch."""
        images_array = [
            image_to_numpy_array(p, target_dimensions=image_dimensions)
            for p in self.filepaths
        ]
        # augment and make to float array
        x = numpy_image_batch_to_x_batch(array(images_array))
        y = array(self.labels_hotencoded)
        return x, y


class MultiprocessingBatchGenerator(utils.Sequence):
    """Precalculate batches, outsource heavy work to threadpool."""

    def __init__(
        self,
        batch_size: int,
        training_pass: TrainingPass,
        image_dimensions: Tuple[int, int],
        processes_count: int = 4,
        precalculate_batches_count: int = 8,
    ):
        """Initialize batch generator."""
        self.training_pass = training_pass
        self.image_dimensions = image_dimensions
        self.hotencoder = get_one_hot_encoder(dataset=training_pass.dataset_id)
        self.batch_task_queue: "Queue[AsyncResult]" = Queue()
        self.pool = Pool(processes_count)
        self.batch_size = batch_size
        self.batch_count = 0
        self.batches_generated_count = 0
        self.batches_in_queue_not_fetched = 0
        self.precalculate_batches_count = precalculate_batches_count

    def __len__(self) -> int:
        return self.batch_count

    def pop_image(self) -> Image:
        raise NotImplementedError()

    def generate_and_enqueue_batch_task(self):
        """Generate and enqueue a batch task."""
        image_filepaths = []
        labels_hotencoded = []

        while len(image_filepaths) < self.batch_size:
            image = self.pop_image()

            if image.label is None:
                # Skip unlabeled image
                continue

            labels_hotencoded.append(self.hotencoder(image.label))
            image_filepaths.append(image.path)

        batch_task = BatchTask(
            filepaths=image_filepaths,
            labels_hotencoded=labels_hotencoded,
        )
        self.batch_task_queue.put(
            self.pool.apply_async(
                BatchTask.process, (batch_task, self.image_dimensions)
            )
        )
        self.batches_in_queue_not_fetched += 1

    def __getitem__(self, index):
        """Get one batch from queue. Used by keras."""
        if self.batches_generated_count < self.batch_count:
            self.generate_and_enqueue_batch_task()
            self.batches_generated_count += 1
        pool_task = self.batch_task_queue.get()
        batch = pool_task.get()
        self.batches_in_queue_not_fetched -= 1
        return batch

    def reset_batch_count(self, batch_count: int):
        self.batch_count = batch_count
        self.batches_generated_count = 0
        while (
            self.batches_in_queue_not_fetched < self.precalculate_batches_count
        ):
            self.generate_and_enqueue_batch_task()

    def close(self):
        self.pool.close()
        self.pool.join()


class BatchGeneratorTraining(MultiprocessingBatchGenerator):
    """Generate batches for model fitting."""

    def __init__(
        self,
        image_list: List[Image],
        training_pass: TrainingPass,
        image_dimensions: Tuple[int, int],
        processes_count=4,
        precalculate_batches_count=8,
    ):
        """Get a generator for batches of images and labels for training."""
        self.image_list = image_list
        self.training_pass = training_pass
        self.image_list_shuffled = image_list[:]  # copy list

        seed(self.training_pass.id + self.training_pass.epoche)
        shuffle(self.image_list_shuffled)

        super().__init__(
            batch_size=training_pass.training_parameter.batch_size,
            training_pass=training_pass,
            image_dimensions=image_dimensions,
            processes_count=processes_count,
            precalculate_batches_count=precalculate_batches_count,
        )

    def pop_image(self) -> Image:
        """Get an image and increase internal counter."""
        if self.training_pass.epoche_offset >= len(self.image_list_shuffled):
            self.training_pass.epoche += 1
            self.training_pass.epoche_offset = 0

            # copy, to not shuffle original
            self.image_list_shuffled = self.image_list[:]
            seed(self.training_pass.id + self.training_pass.epoche)
            shuffle(self.image_list_shuffled)

        image = self.image_list_shuffled[self.training_pass.epoche_offset]
        self.training_pass.epoche_offset += 1
        return image

    def on_epoch_end(self):
        """Callback for keras."""
        self.training_pass.save(update_fields=["epoche", "epoche_offset"])

    def __del__(self):
        super().close()


class BatchGeneratorValidation(MultiprocessingBatchGenerator):
    def __init__(
        self,
        image_list: List[Image],
        training_pass: TrainingPass,
        image_dimensions: Tuple[int, int],
        processes_count=4,
        precalculate_batches_count=8,
    ):
        """Get a generator for batches of images and labels for validation."""
        self.image_list = image_list
        self.training_pass = training_pass
        self.image_list_shuffled = image_list[:]  # copy list
        self.offset = randint(0, len(self.image_list))  # nosec

        seed(self.training_pass.id + self.training_pass.epoche)
        shuffle(self.image_list_shuffled)

        super().__init__(
            batch_size=training_pass.training_parameter.batch_size,
            training_pass=training_pass,
            image_dimensions=image_dimensions,
            processes_count=processes_count,
            precalculate_batches_count=precalculate_batches_count,
        )

    def pop_image(self) -> Image:
        image_index = self.offset % len(self.image_list_shuffled)
        self.offset += 1
        image = self.image_list_shuffled[image_index]
        return image
