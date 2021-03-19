"""Test augmentation options object."""
from schoolnn.models import AugmentationOptions
from numpy import array_equal, random


_KEYS = [
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


def test_augmentation_options_from_to_dict():
    """Create some options, dump and read them back."""
    for disabled_option in _KEYS:
        # Activate everything but one option
        kwargs = {}
        for key in _KEYS:
            kwargs[key] = True
        kwargs[disabled_option] = False

        opt = AugmentationOptions(**kwargs)
        assert opt.get_augmenter()  # Don't fail

        assert opt.to_dict() == kwargs
        assert opt.activated_count() == len(_KEYS) - 1


def test_augmentation_options_from_to_dict2():
    """Create some options, dump and read them back."""
    for enabled_option in _KEYS:
        # Activate nothing but one option
        kwargs = {}
        for key in _KEYS:
            kwargs[key] = False
        kwargs[enabled_option] = True

        opt = AugmentationOptions(**kwargs)
        assert opt.get_augmenter()  # Don't fail

        assert opt.to_dict() == kwargs
        assert opt.activated_count() == 1


def test_augmentation_options_identity():
    """Check if identity applies when no option is enabled."""
    kwargs = {}
    for key in _KEYS:
        kwargs[key] = False

    opt = AugmentationOptions(**kwargs)
    assert opt.to_dict() == kwargs
    assert opt.activated_count() == 0

    random_image_array = 255 * random.rand(28, 28, 3)
    random_image_array = random_image_array.astype("uint8")

    augmented_image = opt.get_augmenter()(image=random_image_array)

    assert array_equal(augmented_image, random_image_array)


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
