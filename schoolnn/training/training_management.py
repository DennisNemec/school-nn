"""Manages the executions of training jobs in the background."""
from typing import Optional
from ..models import (
    TrainingPassState,
    TrainingPass,
    Project,
)
from .do_training_block import (
    do_training_block,
    keras_model_to_bytes,
    bytes_to_keras_model,
)
from .load_dataset import get_training_and_validation_images
from .architecturewrapper import WrappedArchitecture
from .batch_generator import BatchGeneratorTraining, BatchGeneratorValidation
from tensorflow.keras import metrics
from schoolnn_app.settings import DEBUG
from multiprocessing import Process, Queue
from datetime import datetime
from io import BytesIO


def run_job_until_done_or_terminated(
    training_pass: TrainingPass, verbose: bool = False
):
    """Run/continue a training pass until it is done or requested to stop."""
    # Training preparation
    training_validation_images = get_training_and_validation_images(
        training_pass=training_pass
    )

    termination_condition = (
        training_pass.training_parameter.termination_condition
    )
    training_pass.status = TrainingPassState.RUNNING.value
    training_pass.start_datetime = datetime.now()
    training_pass.end_datetime = datetime.now()
    training_pass.save(
        update_fields=["status", "start_datetime", "end_datetime"]
    )

    model = bytes_to_keras_model(training_pass.model_weights)
    image_dimensions = model.input_shape[1:-1]

    # Generate generators
    training_generator = BatchGeneratorTraining(
        image_list=training_validation_images[0],
        training_pass=training_pass,
        image_dimensions=image_dimensions,
    )
    validation_generator = BatchGeneratorValidation(
        image_list=training_validation_images[1],
        training_pass=training_pass,
        image_dimensions=image_dimensions,
    )

    # Run
    while True:
        training_pass.refresh_from_db()
        training_pass_status = TrainingPassState(training_pass.status)
        if training_pass_status == TrainingPassState.PAUSE_REQUESTED:
            training_pass.status = TrainingPassState.PAUSED.value
            training_pass.save()
            break
        if training_pass_status == TrainingPassState.STOP_REQUESTED:
            training_pass.status = TrainingPassState.STOPPED.value
            training_pass.save()
            break
        if training_pass_status == TrainingPassState.COMPLETED:
            break

        running_for_seconds = (
            datetime.now().timestamp()
            - training_pass.start_datetime.timestamp()
        )
        if termination_condition.termination_criteria_fulfilled(
            running_for_seconds=running_for_seconds,
            epoche=training_pass.epoche,
        ):
            training_pass.status = TrainingPassState.COMPLETED.value
            training_pass.save()
            break

        do_training_block(
            training_pass_to_continue=training_pass,
            training_generator=training_generator,
            validation_generator=validation_generator,
            verbose=verbose,
        )
    training_generator.close()
    validation_generator.close()
    training_pass.end_datetime = datetime.now()
    training_pass.save(update_fields=["end_datetime"])


def _initialize_training_pass(
    project: Project, training_pass_name: str
) -> TrainingPass:
    wrapped_architecture = WrappedArchitecture(
        dictionary_representation=project.architecture.architecture_json
    )

    keras_model = wrapped_architecture.to_keras_model()
    keras_model.compile(
        optimizer=project.training_parameter.optimizer.value,
        loss=project.training_parameter.loss_function.value,
        metrics=[metrics.Precision()],
    )

    weights_binary = BytesIO(keras_model_to_bytes(keras_model))

    return TrainingPass.objects.create(
        name=training_pass_name,
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
        dataset_id=project.dataset,
        training_parameter_json=project.training_parameter_json,
        project=project,
        architecture=project.architecture,
        model_weights=weights_binary.read(),
        status=TrainingPassState.START_REQUESTED.value,
    )


def _worker(q: Queue):
    while True:
        training_pass = q.get()
        if not isinstance(training_pass, TrainingPass):
            raise ValueError("Wrong type in queue, expected TraininPass")
        if DEBUG:
            print("Running training pass", training_pass)
        run_job_until_done_or_terminated(
            training_pass=training_pass,
            verbose=DEBUG,
        )


# Warning, works only for usage within one Python process!
class TrainingManager:
    """Singleton to manage training."""

    _queue: Optional[Queue] = None
    _process: Optional[Process] = None

    def __init__(self):
        """Initialize the TrainingManager singleton, or existing one."""
        if TrainingManager._queue is not None:
            return

        if DEBUG:
            print("Initialize training manager")

        TrainingManager._queue: Queue = Queue()
        TrainingManager._process = Process(
            target=_worker, args=(TrainingManager._queue,)
        )
        TrainingManager._process.start()
        self._read_back_tasks_from_database()  # Restore tasks from last run

    def apply_job(
        self, project: Project, training_pass_name: str
    ) -> TrainingPass:
        """Create TrainingPass from project and push it into work queue."""
        if TrainingManager._queue is None:
            raise ValueError("TrainingManager singleton not initialized!")
        training_pass = _initialize_training_pass(
            project=project,
            training_pass_name=training_pass_name,
        )
        TrainingManager._queue.put(training_pass)
        return training_pass

    def _read_back_tasks_from_database(self):
        training_passes = TrainingPass.objects.filter(
            status__in=[TrainingPassState.RUNNING.value]
        )
        for training_pass in training_passes:
            TrainingManager._queue.put(training_pass)

        # Warning! Might requeue in different order!
        training_passes = TrainingPass.objects.filter(
            status__in=[
                TrainingPassState.START_REQUESTED.value,
                TrainingPassState.STOP_REQUESTED.value,
                TrainingPassState.PAUSE_REQUESTED.value,
                TrainingPassState.RESUME_REQUESTED.value,
            ]
        )
        for training_pass in training_passes:
            if DEBUG:
                print("Requeue training pass", training_pass.id)
            TrainingManager._queue.put(training_pass)
