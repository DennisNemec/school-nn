"""Contains methods for augmentation."""
from typing import NamedTuple
from imgaug import augmenters

# See
# https://github.com/aleju/imgaug
# for visual context


class AugmentationOptions(NamedTuple):
    """Which augmentations to turn on or off."""

    channel_shuffle: bool = False
    brightness: bool = False
    gaussian_noise: bool = False
    dropout_boxes: bool = False
    salt_and_pepper: bool = False
    jpeg_artifacts: bool = False
    gaussian_blur: bool = False
    vertical_flip: bool = False
    distortion: bool = False
    rotate: bool = False
    scale_and_translate: bool = False
    color: bool = False

    @classmethod
    def all_activated(cls):
        """Get all activated augmentation options."""
        true_array = [True for _ in range(12)]
        return cls(*true_array)

    def to_dict(self) -> dict:
        """Convert options to dumpable dictionary."""
        return {
            "channel_shuffle": self.channel_shuffle,
            "brightness": self.brightness,
            "gaussian_noise": self.gaussian_noise,
            "dropout_boxes": self.dropout_boxes,
            "salt_and_pepper": self.salt_and_pepper,
            "jpeg_artifacts": self.jpeg_artifacts,
            "vertical_flip": self.vertical_flip,
            "distortion": self.distortion,
            "rotate": self.rotate,
            "scale_and_translate": self.scale_and_translate,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, dictionary: dict):
        """Restore augmentation options from dictionary."""
        return cls(**dictionary)

    def activated_count(self) -> int:
        """Count how many augmentations are activated."""
        return (
            self.channel_shuffle * 1
            + self.brightness * 1
            + self.gaussian_noise * 1
            + self.dropout_boxes * 1
            + self.salt_and_pepper * 1
            + self.jpeg_artifacts * 1
            + self.vertical_flip * 1
            + self.distortion * 1
            + self.rotate * 1
            + self.scale_and_translate * 1
            + self.color * 1
        )

    def _get_channel_shuffle(self) -> augmenters.Augmenter:
        # Shuffle channels in 15% of all images
        if self.channel_shuffle:
            return augmenters.ChannelShuffle(0.15)
        return augmenters.Identity()

    def _get_brightness(self) -> augmenters.Augmenter:
        # Changes brightnes
        if self.brightness:
            return augmenters.Add((-0.35, 0.35))
        return augmenters.Identity()

    def _get_gaussian_noise(self) -> augmenters.Augmenter:
        # Makes image slightly more noisy
        if self.gaussian_noise:
            return augmenters.ChannelShuffle(0.15)
        return augmenters.Identity()

    def _get_dropout_boxes(self) -> augmenters.Augmenter:
        # Renders small black boxes over the image, blocking 3% of the image
        if self.dropout_boxes:
            return augmenters.CoarseDropout(0.03, size_percent=7)
        return augmenters.Identity()

    def _get_salt_and_pepper(self) -> augmenters.Augmenter:
        # Replaces 2% of all pixels with salt and pepper noise
        if self.salt_and_pepper:
            return augmenters.SaltAndPepper(0.02)
        return augmenters.Identity()

    def _get_jpeg_artifacts(self) -> augmenters.Augmenter:
        # Adds JPEG compression arrifacts
        if self.jpeg_artifacts:
            return augmenters.JpegCompression(compression=(80, 95))
        return augmenters.Identity()

    def _get_vertical_flip(self) -> augmenters.Augmenter:
        # Flip vertically by a change of 35%
        if self.vertical_flip:
            return augmenters.Fliplr(0.35)
        return augmenters.Identity()

    def _get_distortion(self) -> augmenters.Augmenter:
        # Slight distortion
        if self.distortion:
            return augmenters.PiecewiseAffine(scale=(0.0, 0.03))
        return augmenters.Identity()

    def _get_scale_and_translate(self) -> augmenters.Augmenter:
        # First scale, then shift the image
        translation_percent = 0.2
        if self.scale_and_translate:
            return augmenters.Affine(
                scale=(0.85, 1.35),
                translate_percent={
                    "x": (-translation_percent, translation_percent),
                    "y": (-translation_percent, translation_percent),
                },
            )
        return augmenters.Identity()

    def _get_rotater(self) -> augmenters.Augmenter:
        # Rotate between -35 and 35 degree
        if self.rotate:
            return augmenters.Rotate((-35, 35))
        return augmenters.Identity()

    def _get_color(self) -> augmenters.Augmenter:
        # Change hue and saturation by -10% to 10%
        if self.color:
            return augmenters.MultiplyHueAndSaturation(
                mul_hue=(0.9, 1.1),
                mul_saturation=(0.5, 1.5),
            )
        return augmenters.Identity()

    def get_augmenter(self) -> augmenters.Augmenter:
        """Compile an augmenter to augment images or batches of images."""
        if self.activated_count() == 0:
            return augmenters.Identity()

        chance_of_augmentation_to_be_applied = 5 / self.activated_count()
        if chance_of_augmentation_to_be_applied > 1:
            chance_of_augmentation_to_be_applied = 1

        augmentations = [
            self._get_channel_shuffle(),
            self._get_brightness(),
            self._get_gaussian_noise(),
            self._get_dropout_boxes(),
            self._get_salt_and_pepper(),
            self._get_jpeg_artifacts(),
            self._get_vertical_flip(),
            self._get_distortion(),
            self._get_scale_and_translate(),
            self._get_rotater(),
            self._get_color(),
        ]

        augmentations = [
            aug
            for aug in augmentations
            if not isinstance(aug, augmenters.Identity)
        ]

        return augmenters.SomeOf((3, 6), augmentations)
