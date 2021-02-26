"""Infere with a (partially) trained model."""
from typing import List
from io import BytesIO
from numpy import array
from base64 import b64encode
from PIL import Image as PillowImage
from schoolnn.models import Label
from .do_training_block import bytes_to_keras_model
from .batch_generator import numpy_image_batch_to_x_batch, image_to_numpy_array
from .one_hot_coding import get_one_hot_decoder
from .grad_cam import get_submodels, grad_cam


class ClassificationResult:
    """Information about how an images has been classified."""

    def __init__(
        self,
        label: Label,
        confidence: float,
        image_for_neural_net_bytes: bytes,
        image_bytes: bytes,
        image_with_heatmap_bytes: bytes,
    ):
        """Create a classification result."""
        self.label = label
        self.confidence = confidence
        self.image_for_neural_net_bytes = image_for_neural_net_bytes
        self.image_bytes = image_bytes
        self.image_with_heatmap_bytes = image_with_heatmap_bytes

    def __str__(self) -> str:
        """Human readable output of classification."""
        return "{} ({:.4}%)".format(
            self.label.name,
            self.confidence * 100,
        )

    @property
    def image_for_neural_net_b64(self):
        return b64encode(self.image_for_neural_net_bytes).decode()

    @property
    def image_b64(self):
        return b64encode(self.image_bytes).decode()

    @property
    def image_with_heatmap_b64(self):
        return b64encode(self.image_with_heatmap_bytes).decode()

    @property
    def confidence_percent(self):
        return self.confidence * 100


def infere_images(
    training_pass,
    images: List[BytesIO],
) -> List[ClassificationResult]:
    """Classify images."""
    model = bytes_to_keras_model(training_pass.model_weights)
    image_dimensions = model.input_shape[1:-1]
    hot_decoder = get_one_hot_decoder(dataset=training_pass.dataset_id)

    image_batch = array(
        [
            image_to_numpy_array(image, target_dimensions=image_dimensions)
            for image in images
        ]
    )

    x_batch = numpy_image_batch_to_x_batch(
        numpy_image_batch=image_batch,
        augmenter=None,
    )

    # Keep batch size small to not use much (GPU) RAM.
    # A training could be running.
    predictions = model.predict(x=x_batch, batch_size=4, verbose=False)

    grad_cam_a, grad_cam_b = get_submodels(model)

    result = []
    for i in range(len(predictions)):
        images[i].seek(0)
        image_bytes = images[i].read()

        image_as_seen_by_nn = PillowImage.fromarray(image_batch[i])
        bio = BytesIO()
        bio.name = "file_extension.jpeg"
        image_as_seen_by_nn.save(bio)
        bio.seek(0)

        heatmap = grad_cam(
            last_conv_layer_model=grad_cam_a,
            classifier_model=grad_cam_b,
            image=x_batch[i],
            original_image=image_batch[i],
        )
        heatmap_pillow = PillowImage.fromarray(heatmap)
        bio2 = BytesIO()
        bio2.name = "file_extension.jpeg"
        heatmap_pillow.save(bio2)
        bio2.seek(0)

        result.append(
            ClassificationResult(
                label=hot_decoder(predictions[i]),
                confidence=max(predictions[i]),
                image_for_neural_net_bytes=bio.read(),
                image_bytes=image_bytes,
                image_with_heatmap_bytes=bio2.read(),
            )
        )

    return result
