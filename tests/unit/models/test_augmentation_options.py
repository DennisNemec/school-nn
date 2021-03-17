"""Test augmentation options object."""
from schoolnn.models import AugmentationOptions
from numpy import array_equal, random


def test_augmentation_options_from_to_dict():
    """Create some object, dump and read them back."""
    keys = [
        "channel_shuffle",
        "brightness",
        "gaussian_noise",
        "dropout_boxes",
        "salt_and_pepper",
        "jpeg_artifacts",
        "vertical_flip",
        "distortion",
        "rotate",
        "scale_and_translate",
        "color",
    ]

    for disabled_option in keys:
        # Activate everything but one option
        kwargs = {}
        for key in keys:
            kwargs[key] = True
        kwargs[disabled_option] = False

        obj = AugmentationOptions(**kwargs)

        assert obj.to_dict() == kwargs
        assert obj.activated_count() == len(keys) - 1


def test_augmentation_options_augmentation():
    """Do some augmentation."""
    aug_options = AugmentationOptions.all_activated()
    full_augmenter = aug_options.get_augmenter()

    batch_size = 32
    image_side = 128
    image_batch = 255 * random.rand(batch_size, image_side, image_side, 3)
    image_batch = image_batch.astype("uint8")

    augmented_batch = full_augmenter(images=image_batch)

    assert augmented_batch.shape == image_batch.shape
    assert not array_equal(image_batch, augmented_batch)
