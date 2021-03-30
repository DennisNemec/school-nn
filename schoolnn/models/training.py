"""Models used for domain logic / training."""
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

    @property
    def human_readable(self):
        """Get human readable text of status."""
        lookup_dict = {
            self.START_REQUESTED: "In der Warteschlange...",
            self.RUNNING: "Läuft",
            self.PAUSE_REQUESTED: "Wird pausiert...",
            self.PAUSED: "Pausiert",
            self.RESUME_REQUESTED: "In der Warteschlange...",
            self.COMPLETED: "Fertig",
            self.STOP_REQUESTED: "Wird gestoppt...",
            self.STOPPED: "Gestoppt",
        }
        return lookup_dict[self]


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
        self, seconds: Optional[int] = None, epochs: Optional[int] = None
    ):
        """Provide multiple conditions, stop learning if one is met."""
        self.seconds = seconds
        self.epochs = epochs

    def to_dict(self) -> dict:
        """Dump object to a dictionary."""
        return {"seconds": self.seconds, "epochs": self.epochs}

    @classmethod
    def from_dict(cls, dictionary: dict):
        """Load object from a dictionary."""
        return cls(seconds=dictionary["seconds"], epochs=dictionary["epochs"])

    @property
    def time_human_readable(self) -> str:
        """Get seconds as human readable string."""
        if self.seconds is None:
            return "∞"  # infinity
        result = ""
        if self.seconds > 24 * 3600:
            result += "{} {} ".format(int(self.seconds / 24 / 3600), "Tage")
        result += "{:02}:{:02}:{:02}h".format(
            int(self.seconds / 3600),
            int(self.seconds / 60) % 60,
            int(self.seconds) % 60,
        )
        return result

    def termination_criteria_fulfilled(
        self, running_for_seconds: float, epoche: int
    ) -> bool:
        """Check whether training should terminate."""
        if self.seconds:
            if running_for_seconds >= self.seconds:
                return True

        if self.epochs:
            if epoche >= self.epochs:
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
    def from_dict(cls, dictionary: dict):
        """Load from a dictionary."""
        return cls(
            validation_split=dictionary["validation_split"],
            learning_rate=dictionary["learning_rate"],
            termination_condition=TerminationCondition.from_dict(
                dictionary["termination_condition"],
            ),
            batch_size=dictionary["batch_size"],
            loss_function=LossFunction(dictionary["loss_function"]),
            optimizer=Optimizer(dictionary["optimizer"]),
            augmentation_options=AugmentationOptions.from_dict(
                dictionary["augmentation_options"],
            ),
        )

    def to_dict(self) -> dict:
        """Dump to a dictionary."""
        return {
            "validation_split": self.validation_split,
            "learning_rate": self.learning_rate,
            "termination_condition": self.termination_condition.to_dict(),
            "batch_size": self.batch_size,
            "loss_function": self.loss_function.value,
            "optimizer": self.optimizer.value,
            "augmentation_options": self.augmentation_options.to_dict(),
        }
