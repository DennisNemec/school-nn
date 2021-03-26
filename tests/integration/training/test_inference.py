"""Contains tests for schoolnn.trining.inference.py."""
from io import BytesIO
from random import shuffle
from schoolnn.models import (
    Image,
    Label,
)
from schoolnn.training.inference import infere_images
from schoolnn.training.training_management import _initialize_training_pass
from ..sample_models import get_test_project


def test_infere_images():
    project = get_test_project(make_images_existing=True)
    training_pass = _initialize_training_pass(
        project=project,
        training_pass_name="",
    )

    labels = list(Label.objects.filter(dataset=training_pass.dataset_id))
    images = list(Image.objects.filter(dataset=training_pass.dataset_id))
    shuffle(images)
    random_chosen_images = images[:100]

    images_binary = [
        BytesIO(open(f.path, "rb").read()) for f in random_chosen_images
    ]

    inference_result = infere_images(
        training_pass=training_pass,
        images=images_binary,
    )

    assert len(inference_result) == len(images_binary)
    for single_inferece_result in inference_result:
        assert single_inferece_result.label in labels
        assert single_inferece_result.confidence > 0.0
        assert single_inferece_result.confidence < 1.0
        assert single_inferece_result.confidence_percent > 0.0
        assert single_inferece_result.confidence_percent < 100.0

        # Test if methods return anything
        assert single_inferece_result.image_for_neural_net_b64
        assert single_inferece_result.image_b64
        assert single_inferece_result.image_with_heatmap_b64
