"""Models used for domain logic / training."""
from json import loads, dumps
from enum import Enum
from typing import Optional
from .augmentation_options import AugmentationOptions


class TrainingPassState(Enum):
    """State of the training pass."""

    START_REQUESTED = "start_requested"
    RUNNING = "running"
    PAUSE_REQUESTED = "pause_requested"
    PAUSED = "paused"
    RESUME_REQUESTED = "resume_requested"
    COMPLETED = "completed"
    STOP_REQUESTED = "stop_requested"
    STOPPED = "stopped"


class LossFunction(Enum):
    """Enumeration of the loss function."""

    CATEGORICAL_CROSSENTROPY = "categorical_crossentropy"

    @classmethod
    def to_array(cls):
        return [e.value for e in cls]


class Optimizer(Enum):
    """Enumeration of the optimizer."""

    SGD = "sgd"
    RMSPROP = "rmsprop"
    ADAM = "adam"
    NADAM = "nadam"
    ADADELTA = "adadelta"
    ADAMAX = "adamax"

    @classmethod
    def to_array(cls):
        return [e.value for e in cls]


class TerminationCondition:
    """Combination of conditions, when to stop training."""

    def __init__(
        self,
        seconds: Optional[int] = None,
        epochs: Optional[int] = None,
        validation_loss_raising: bool = False,
    ):
        """Provide multiple conditions, stop learning if one is met."""
        self.seconds = seconds
        self.epochs = epochs
        self.validation_loss_raising = validation_loss_raising
        self.optimum_validation_loss: Optional[float] = None

    def to_dict(self) -> dict:
        """Dump object to a dictionary."""
        return {
            "seconds": self.seconds,
            "epochs": self.epochs,
            "validation_loss_raising": self.validation_loss_raising,
        }

    @classmethod
    def from_dict(cls, dictionary: dict):
        """Load object from a dictionary."""
        return cls(
            seconds=dictionary["seconds"],
            epochs=dictionary["epochs"],
            validation_loss_raising=dictionary["validation_loss_raising"],
        )

    def termination_criteria_fulfilled(
        self,
        running_for_seconds: float,
        epoche: int,
        validation_loss: float,
    ) -> bool:
        """Check whether training should terminate."""
        if self.seconds:
            if running_for_seconds >= self.seconds:
                return True
        if self.epochs:
            if epoche >= self.epochs:
                return True
        if self.optimum_validation_loss is None:
            self.optimum_validation_loss = validation_loss
        if validation_loss < self.optimum_validation_loss:
            self.optimum_validation_loss = validation_loss
        if validation_loss > 1.1 * self.optimum_validation_loss:
            return True
        return False


class TrainingParameter:
    """Parameter used for training models."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        validation_split: float,
        learning_rate: float,
        termination_condition: TerminationCondition,
        batch_size: int,
        loss_function: LossFunction,
        optimizer: Optimizer,
        augmentation_options: AugmentationOptions,
    ):
        """Create a training parameter object."""
        self.validation_split = validation_split
        self.learning_rate = learning_rate
        self.termination_condition = termination_condition
        self.batch_size = batch_size
        self.loss_function = loss_function
        self.optimizer = optimizer
        self.augmentation_options = augmentation_options

    @classmethod
    def from_json(cls, json: str):
        """Load from a json string."""
        tp_dict: dict = loads(json)
        return cls(
            validation_split=tp_dict["validation_split"],
            learning_rate=tp_dict["learning_rate"],
            termination_condition=TerminationCondition.from_dict(
                tp_dict["termination_condition"],
            ),
            batch_size=tp_dict["batch_size"],
            loss_function=LossFunction(tp_dict["loss_function"]),
            optimizer=Optimizer(tp_dict["optimizer"]),
            augmentation_options=AugmentationOptions.from_dict(
                tp_dict["augmentation_options"],
            ),
        )

    def to_json(self) -> str:
        """Dump to a json string."""

        if self.is_empty():
            return "{}"

        return dumps(
            {
                "validation_split": self.validation_split,
                "learning_rate": self.learning_rate,
                "termination_condition": self.termination_condition.to_dict(),
                "batch_size": self.batch_size,
                "loss_function": self.loss_function.value,
                "optimizer": self.optimizer.value,
                "augmentation_options": self.augmentation_options.to_dict(),
            }
        )

    def is_empty(self):
        return any(
            value is None
            for value in [
                self.validation_split,
                self.learning_rate,
                self.termination_condition,
                self.batch_size,
                self.loss_function,
                self.optimizer,
                self.augmentation_options,
            ]
        )
