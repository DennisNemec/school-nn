"""Generate training and validation image lists."""
from typing import List, Tuple
from ..models import TrainingPass, Image
from random import seed, shuffle


def get_training_and_validation_images(
    training_pass: TrainingPass,
) -> Tuple[List[Image], List[Image]]:
    """Load image entities from dataset."""
    image_list = list(
        Image.objects.filter(dataset_id=training_pass.dataset_id).order_by(
            "id"
        )
    )

    validation_split: float = training_pass.training_parameter.validation_split

    validation_items_count = max(1, int(len(image_list) * validation_split))

    seed(training_pass.id)
    shuffle(image_list)

    training_list = image_list[:-validation_items_count]
    validation_list = image_list[-validation_items_count:]

    return training_list, validation_list
