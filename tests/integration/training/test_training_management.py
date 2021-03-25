"""Test schoolnn.training.training_magement."""
from schoolnn.models import (
    Architecture,
    TrainingParameter,
    TerminationCondition,
    LossFunction,
    Optimizer,
    AugmentationOptions,
)
from ..sample_models import (
    get_test_project,
)

from schoolnn.training.training_management import (
    _initialize_training_pass,
    run_job_until_done_or_terminated,
)

MINIMAL_ARCH = [
    {"type": "Input", "shape": [16, 16, 3]},
    {
        "type": "Conv2D",
        "activation": "relu",
        "filters": 256,
        "strides": [1, 1],
        "kernel_size": [2, 2],
        "padding": "valid",
    },
    {"type": "MaxPooling2D", "pool_size": [2, 2], "strides": [2, 2]},
    {"type": "BatchNormalization"},
    {"type": "Flatten"},
    {"type": "Dense", "activation": "relu", "units": 128},
    {"type": "Dense", "activation": "softmax", "units": 3},
]


def _get_training_pass_id_existing_in_db() -> int:
    project = get_test_project(make_images_existing=True)
    project.training_parameter = TrainingParameter(
        validation_split=0.1,
        learning_rate=0.1,
        termination_condition=TerminationCondition(seconds=10),
        batch_size=4,
        loss_function=LossFunction.CATEGORICAL_CROSSENTROPY,
        optimizer=Optimizer.SGD,
        augmentation_options=AugmentationOptions.all_activated(),
    )
    project.architecture = Architecture.objects.create(
        name="Arch1",
        custom="True",
        architecture_json=MINIMAL_ARCH,
        user=project.user,
    )
    project.save()

    training_pass = _initialize_training_pass(
        project=project,
        training_pass_name="TrainingPassTest",
    )
    return training_pass


def test_run_job_until_done_or_terminated():
    training_pass = _get_training_pass_id_existing_in_db()
    run_job_until_done_or_terminated(
        training_pass=training_pass,
        verbose=True,
    )


"""
class RunJobTestCase(TestCase):
#@pytest.mark.django_db
    def setUp(self):
        self.training_pass = _get_training_pass_id_existing_in_db()

    def test_run_job_until_done_or_terminated(self):
        #training_pass_id = _get_training_pass_id_existing_in_db()
        run_job_until_done_or_terminated(
            training_pass=self.training_pass,
            verbose=True,
        )
"""
