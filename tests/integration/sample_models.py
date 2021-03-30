"""Get sample objects for testing."""
from typing import List
from uuid import uuid4
from tensorflow.keras import Model, layers, Sequential
from os import makedirs
from numpy import array, random
from PIL import Image as PillowImage
from schoolnn.training import WrappedArchitecture
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
        img_dimension = random.randint(4) + 8  # 8 to 12
        arr = random.rand(img_dimension, img_dimension, 3)
        arr *= 255
        arr = arr.astype("uint8")
        pil_img = PillowImage.fromarray(arr)
        pil_img.save(img.path)


def get_sample_model() -> Model:
    m = Sequential(
        [
            layers.Input(shape=(8, 8, 3)),
            layers.Conv2D(filters=8, kernel_size=(4, 4)),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dense(3, activation="softmax"),
        ]
    )

    m.compile(loss="crossentropy", optimizer="adam")
    return m


_wrapped_arch = WrappedArchitecture.from_keras_model(get_sample_model())


def get_test_project(make_images_existing=False) -> Project:
    user = User.objects.create(
        username=uuid4().hex,
    )

    architecture = Architecture.objects.create(
        name=uuid4().hex,
        architecture_json=_wrapped_arch.json_representation,
        user=user,
    )

    dataset = Dataset.objects.create(name=uuid4().hex)
    label0 = Label.objects.create(dataset=dataset, name=LABEL_0_NAME)
    label1 = Label.objects.create(dataset=dataset, name=LABEL_1_NAME)
    label2 = Label.objects.create(dataset=dataset, name=LABEL_2_NAME)
    for _ in range(123):
        for lab in [label0, label1, label2]:
            Image.objects.create(dataset=dataset, label=label0)

    project = Project.objects.create(
        name=uuid4().hex,
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
        name=uuid4().hex,
        dataset_id=project.dataset,
        project=project,
        architecture=project.architecture,
        training_parameter_json=training_parameter.to_dict(),
    )
    return training_pass
