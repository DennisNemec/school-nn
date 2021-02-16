"""Runs one block of training for a few seconds."""
from typing import List, Tuple
from io import BytesIO
from keras import models
from django.db import transaction
from schoolnn_app.settings import (
    TRAINING_BLOCK_BATCH_COUNT,
)
from .batch_generator import (
    BatchGeneratorTraining,
    BatchGeneratorValidation,
)
from ..models import TrainingPass, Image, TrainingStepMetrics
import tempfile
from os import path
from json import dumps


def keras_model_to_bytes(keras_model: models.Model) -> bytes:
    """Get keras model as binary."""
    weights_binary = BytesIO()
    with tempfile.TemporaryDirectory() as tmp:
        filepath = path.join(tmp, "model.keras")
        keras_model.save(filepath, save_format="tf")
        with open(filepath, "rb") as f:
            weights_binary.write(f.read())
    weights_binary.seek(0)
    return weights_binary.read()


def bytes_to_keras_model(b: bytes) -> models.Model:
    """Get keras model from binary."""
    with tempfile.TemporaryDirectory() as tmp:
        filepath = path.join(tmp, "model.keras")
        with open(filepath, "wb") as f:
            f.write(b)
        model = models.load_model(filepath)
        return model


def do_training_block(
    training_pass_to_continue: TrainingPass,
    training_validation_images: Tuple[List[Image], List[Image]],
    verbose: bool = False,
):
    """Continue a training pass, train the model and save metrics."""
    model = bytes_to_keras_model(training_pass_to_continue.model_weights)

    # Get shape without batch size and rgb = 3
    image_dimensions = model.input_shape[1:-1]

    validation_split = (
        training_pass_to_continue.training_parameter.validation_split
    )
    validation_batch_count = (
        int(validation_split * TRAINING_BLOCK_BATCH_COUNT) + 1
    )
    training_batch_count = (
        int((1 - validation_split) * TRAINING_BLOCK_BATCH_COUNT) + 1
    )

    progress_bar_printing = verbose * 1
    # Training
    training_generator = BatchGeneratorTraining(
        image_list=training_validation_images[0],
        training_pass=training_pass_to_continue,
        batch_count=training_batch_count,
        image_dimensions=image_dimensions,
    )
    training_metrics = model.fit(
        training_generator,
        verbose=progress_bar_printing,
    )

    # Validation
    validation_generator = BatchGeneratorValidation(
        image_list=training_validation_images[1],
        training_pass=training_pass_to_continue,
        batch_count=validation_batch_count,
        image_dimensions=image_dimensions,
    )
    validation_metrics = model.evaluate(
        validation_generator,
        verbose=progress_bar_printing,
    )

    # Saving metrics
    training_loss = training_metrics.history["loss"][0]
    training_accuracy = training_metrics.history["categorical_crossentropy"][0]
    validation_loss = validation_metrics[0]
    validation_accuray = validation_metrics[1]

    metrics = {
        "training": {
            "loss": training_loss,
            "accuracy": training_accuracy,
        },
        "validation": {
            "loss": validation_loss,
            "accuracy": validation_accuray,
        },
    }

    with transaction.atomic():
        # Saving new weights
        training_pass_to_continue.model_weights = keras_model_to_bytes(model)
        training_pass_to_continue.save(update_fields=["model_weights"])

        TrainingStepMetrics.objects.create(
            training_pass=training_pass_to_continue,
            metrics_json=dumps(metrics),
        )

    if verbose:
        print(
            "Block done. Report:\n"
            "Training loss {}, accuracy {}\n"
            "Validation loss {}, accuracy {}".format(
                training_loss,
                training_accuracy,
                validation_loss,
                validation_accuray,
            )
        )
