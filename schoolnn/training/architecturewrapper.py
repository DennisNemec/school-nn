"""Convert from Keras to a simple dictionary/json format and vice versa."""
import keras
from keras import layers
from typing import Union, Any, Callable
from json import dumps


_supported_layers = Union[
    layers.Input,
    layers.Conv2D,
    layers.MaxPooling2D,
    layers.Flatten,
    layers.BatchNormalization,
    layers.Dropout,
]


class ModelNotSupportedException(Exception):
    """Exception to be raised if Keras model uses layers we don't support."""


class DictionaryRepresentationException(Exception):
    """Architecture representation createable from a model or a dictionary."""


def _activation_to_keyword(activation: Callable) -> str:
    # TODO: find less hacky way
    return activation.__name__


def _layer_to_dict(kl: Any) -> dict:
    if isinstance(kl, layers.MaxPooling2D):
        return {
            "type": "MaxPooling2D",
            "pool_size": kl.pool_size,
            "strides": kl.strides,
        }
    if isinstance(kl, layers.Conv2D):
        return {
            "type": "Conv2D",
            "activation": _activation_to_keyword(kl.activation),
            "filters": kl.filters,
            "strides": kl.strides,
            "kernel_size": kl.kernel_size,
            "padding": kl.padding,
        }
    if isinstance(kl, layers.Dense):
        return {
            "type": "Dense",
            "activation": _activation_to_keyword(kl.activation),
            "units": kl.units,
        }
    if isinstance(kl, layers.Dropout):
        return {
            "type": "Dropout",
            "rate": kl.rate,
        }
    if isinstance(kl, layers.Flatten):
        return {"type": "Flatten"}
    if isinstance(kl, layers.BatchNormalization):
        return {"type": "BatchNormalization"}
    raise ModelNotSupportedException(kl.__class__.__name__)


def _dict_to_layer(d: dict) -> _supported_layers:
    layer_type = d["type"]
    if layer_type == "Input":
        return layers.Input(shape=d["shape"])
    if layer_type == "MaxPooling2D":
        return layers.MaxPooling2D(
            pool_size=d["pool_size"],
            strides=d["strides"],
        )
    if layer_type == "Conv2D":
        return layers.Conv2D(
            filters=d["filters"],
            kernel_size=d["kernel_size"],
            strides=d["strides"],
            padding=d["padding"],
            activation=d["activation"],
        )
    if layer_type == "Flatten":
        return layers.Flatten()
    if layer_type == "Dropout":
        return layers.Dropout(rate=d["rate"])
    if layer_type == "BatchNormalization":
        return layers.BatchNormalization()
    if layer_type == "Dense":
        return layers.Dense(units=d["units"], activation=d["activation"])
    e = "Unsupported layer: {}".format(d)
    raise DictionaryRepresentationException(e)


class WrappedArchitecture:
    """Wrapper around the dictionary representation of a nn architecture."""

    def __init__(self, dictionary_representation: dict):
        """Create a wrapped object and validates for syntax errors."""
        self.dictionary_representation = dictionary_representation
        self.to_keras_model()  # Raises exception for invalid dictionary

    @classmethod
    def from_keras_model(cls, m: keras.Model):
        """Generate architecture representation from a keras model."""
        layers = []
        layers.append(
            {
                "type": "Input",
                "shape": m.input_shape[1:],
            }  # Drop Batch Dimension
        )

        for keras_layer in m.layers:
            layers.append(_layer_to_dict(keras_layer))

        d = {"layers": layers}
        return cls(d)

    def to_json(self) -> str:
        """Get the architecture as json string."""
        return dumps(self.dictionary_representation)

    def to_json_indent(self) -> str:
        """Get the architecture as humand readable json string."""
        return dumps(self.dictionary_representation, indent=4)

    def to_keras_model(self) -> keras.Model:
        """Get the architecture as keras model."""
        m = keras.Sequential()

        for dict_layer in self.dictionary_representation["layers"]:
            m.add(_dict_to_layer(dict_layer))

        m.compile()
        return m
