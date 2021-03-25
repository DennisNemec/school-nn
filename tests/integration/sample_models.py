"""Get sample objects for testing."""
from typing import List
from datetime import datetime
from os import makedirs
from numpy import array, random
from PIL import Image as PillowImage
from schoolnn.models import (
    TrainingParameter,
    TerminationCondition,
    LossFunction,
    Optimizer,
    AugmentationOptions,
    TrainingPass,
    Dataset,
    Label,
    Image,
    Architecture,
    User,
    Project,
)


LABEL_COUNT = 3
LABEL_0_NAME = "L0"
LABEL_1_NAME = "L1"
LABEL_2_NAME = "L2"
VALIDATION_SPLIT = 0.1
BATCH_SIZE = 16


def _generate_random_images(image_list: List[Image]) -> array:
    dataset_dir = image_list[0].dataset.dir
    makedirs(dataset_dir, exist_ok=True)

    for img in image_list:
        img_dimension = random.randint(20) + 10  # 10 - 30
        arr = random.rand(img_dimension, img_dimension, 3)
        arr *= 255
        arr = arr.astype("uint8")
        pil_img = PillowImage.fromarray(arr)
        pil_img.save(img.path)


def get_test_project(make_images_existing=False) -> Project:
    user = User.objects.create()

    architecture = Architecture.objects.create(
        name="",
        architecture_json={},
        user=user,
    )

    dataset = Dataset.objects.create(name="")
    label0 = Label.objects.create(dataset=dataset, name=LABEL_0_NAME)
    label1 = Label.objects.create(dataset=dataset, name=LABEL_1_NAME)
    label2 = Label.objects.create(dataset=dataset, name=LABEL_2_NAME)
    for _ in range(234):
        for lab in [label0, label1, label2]:
            Image.objects.create(dataset=dataset, label=label0)

    project = Project.objects.create(
        name="",
        dataset=dataset,
        user=user,
        architecture=architecture,
    )

    if make_images_existing:
        _generate_random_images(
            image_list=Image.objects.filter(dataset=dataset)
        )

    return project


def get_test_training_pass(make_images_existing=False) -> TrainingPass:

    project = get_test_project(make_images_existing=make_images_existing)

    training_parameter = TrainingParameter(
        validation_split=VALIDATION_SPLIT,
        learning_rate=0.1,
        termination_condition=TerminationCondition(),
        batch_size=BATCH_SIZE,
        loss_function=LossFunction.CATEGORICAL_CROSSENTROPY,
        optimizer=Optimizer.ADADELTA,
        augmentation_options=AugmentationOptions.all_activated(),
    )

    training_pass = TrainingPass.objects.create(
        name="",
        dataset_id=project.dataset,
        project=project,
        architecture=project.architecture,
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
        training_parameter_json=training_parameter.to_dict(),
    )
    return training_pass
