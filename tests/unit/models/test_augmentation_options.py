"""Test augmentation options object."""
from schoolnn.models import AugmentationOptions


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
