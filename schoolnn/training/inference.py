"""Infere with a (partially) trained model."""
from typing import List
from io import BytesIO
from numpy import array
from schoolnn.models import Label
from .do_training_block import bytes_to_keras_model
from .batch_generator import (
    numpy_image_batch_to_x_batch,
    image_to_numpy_array,
)
from .one_hot_coding import get_one_hot_decoder


class ClassificationResult:
    """Information about how an images has been classified."""

    def __init__(self, label: Label, confidence: float):
        """Create a classification result."""
        self.label = label
        self.confidence = confidence

    def __str__(self) -> str:
        """Human readable output of classification."""
        return "{} ({:.4}%)".format(
            self.label.name,
            self.confidence * 100,
        )


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

    return [
        ClassificationResult(label=hot_decoder(pred), confidence=max(pred))
        for pred in predictions
    ]
