"""Convert from keras to a simple dictionary/json format and vice versa."""
from tensorflow.keras import layers
from typing import Union, Any, Callable
from json import dumps
import tensorflow.keras as keras


SupportedLayers = Union[
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


def _layer_to_dict(keras_layer: Any) -> dict:
    if isinstance(keras_layer, layers.MaxPooling2D):
        return {
            "type": "MaxPooling2D",
            "pool_size": keras_layer.pool_size,
            "strides": keras_layer.strides,
        }
    if isinstance(keras_layer, layers.Conv2D):
        return {
            "type": "Conv2D",
            "activation": _activation_to_keyword(keras_layer.activation),
            "filters": keras_layer.filters,
            "strides": keras_layer.strides,
            "kernel_size": keras_layer.kernel_size,
            "padding": keras_layer.padding,
        }
    if isinstance(keras_layer, layers.Dense):
        return {
            "type": "Dense",
            "activation": _activation_to_keyword(keras_layer.activation),
            "units": keras_layer.units,
        }
    if isinstance(keras_layer, layers.Dropout):
        return {
            "type": "Dropout",
            "rate": keras_layer.rate,
        }
    if isinstance(keras_layer, layers.Flatten):
        return {"type": "Flatten"}
    if isinstance(keras_layer, layers.BatchNormalization):
        return {"type": "BatchNormalization"}
    raise ModelNotSupportedException(keras_layer.__class__.__name__)


def _dict_to_layer(layer_dict: dict) -> SupportedLayers:
    layer_type = layer_dict["type"]
    if layer_type == "Input":
        keras_layer = layers.Input(shape=layer_dict["shape"])
    elif layer_type == "MaxPooling2D":
        keras_layer = layers.MaxPooling2D(
            pool_size=layer_dict["pool_size"],
            strides=layer_dict["strides"],
        )
    elif layer_type == "Conv2D":
        keras_layer = layers.Conv2D(
            filters=layer_dict["filters"],
            kernel_size=layer_dict["kernel_size"],
            strides=layer_dict["strides"],
            padding=layer_dict["padding"],
            activation=layer_dict["activation"],
        )
    elif layer_type == "Flatten":
        keras_layer = layers.Flatten()
    elif layer_type == "Dropout":
        keras_layer = layers.Dropout(rate=layer_dict["rate"])
    elif layer_type == "BatchNormalization":
        keras_layer = layers.BatchNormalization()
    elif layer_type == "Dense":
        keras_layer = layers.Dense(
            units=layer_dict["units"], activation=layer_dict["activation"]
        )
    else:
        err_msg = "Unsupported layer: {}".format(layer_type)
        raise DictionaryRepresentationException(err_msg)

    return keras_layer


class WrappedArchitecture:
    """Wrapper around the dictionary representation of a nn architecture."""

    def __init__(self, dictionary_representation: dict):
        """Create a wrapped object and validates for syntax errors."""
        self.dictionary_representation = dictionary_representation
        self.to_keras_model()  # Raises exception for invalid dictionary

    @classmethod
    def from_keras_model(cls, keras_model: keras.Model):
        """Generate architecture representation from a keras model."""
        arch_layers = []
        arch_layers.append(
            # [1:] Drop Batch Dimension
            {"type": "Input", "shape": keras_model.input_shape[1:]}
        )

        for keras_layer in keras_model.layers:
            arch_layers.append(_layer_to_dict(keras_layer))

        architecture_dict = {"layers": arch_layers}
        return cls(architecture_dict)

    def to_json_indent(self) -> str:
        """Get the architecture as humand readable json string."""
        return dumps(self.dictionary_representation, indent=4)

    def to_keras_model(self) -> keras.Model:
        """Get the architecture as keras model."""
        keras_model = keras.Sequential()

        for dict_layer in self.dictionary_representation:
            keras_model.add(_dict_to_layer(dict_layer))

        keras_model.compile()
        return keras_model
