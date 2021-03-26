"""Contains tests for ArchitectureWrapper."""
from typing import List
from tensorflow.keras import Model, Sequential, layers
from schoolnn.training.architecturewrapper import (
    # ModelNotSupportedException,
    # DictionaryRepresentationException,
    WrappedArchitecture,
)


def _get_example_list() -> List[dict]:
    return [
        {
            "type": "Input",
            "shape": [12, 12, 3],
        },
        {
            "type": "Conv2D",
            "activation": "relu",
            "filters": 4,
            "strides": [4, 4],
            "kernel_size": [4, 4],
            "padding": "same",
        },
        {
            "type": "BatchNormalization",
        },
        {"type": "MaxPooling2D", "pool_size": [3, 3], "strides": [2, 2]},
        {
            "type": "Flatten",
        },
        {
            "type": "Dense",
            "activation": "elu",
            "units": 5,
        },
    ]


def test_dict_to_model():
    """Test dict to model conversion."""
    d = _get_example_list()
    wrapped = WrappedArchitecture(d)
    keras_model: Model = wrapped.to_keras_model()
    keras_model.compile("adam", loss="mse")

    assert keras_model.input_shape == (None, 12, 12, 3)
    assert isinstance(keras_model.layers[0], layers.Conv2D)
    assert keras_model.layers[0].activation.__name__ == "relu"
    assert keras_model.layers[0].padding == "same"

    assert isinstance(keras_model.layers[1], layers.BatchNormalization)
    assert isinstance(keras_model.layers[2], layers.MaxPooling2D)
    assert isinstance(keras_model.layers[3], layers.Flatten)

    assert isinstance(keras_model.layers[4], layers.Dense)
    assert keras_model.layers[4].activation.__name__ == "elu"
    assert keras_model.layers[4].units == 5


def test_model_to_dict():
    """Create a model and verify its wrapped dict."""
    model = Sequential()
    model.add(layers.Input(shape=(8, 12, 3)))
    model.add(layers.Conv2D(filters=4, strides=(2, 2), kernel_size=(4, 4)))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPool2D(pool_size=(3, 3), padding="valid"))
    model.add(layers.Flatten())
    model.add(layers.Dense(4, activation="elu"))
    model.add(layers.Dense(2, activation="softmax"))

    wrapped = WrappedArchitecture.from_keras_model(model)

    dict_layers = wrapped.to_json()

    assert dict_layers[0] == {"type": "Input", "shape": (8, 12, 3)}

    assert dict_layers[1]["type"] == "Conv2D"
    assert dict_layers[1]["strides"] == (2, 2)
    assert dict_layers[1]["kernel_size"] == (4, 4)

    assert dict_layers[2]["type"] == "BatchNormalization"

    assert dict_layers[3]["type"] == "MaxPooling2D"

    assert dict_layers[4]["type"] == "Flatten"

    assert dict_layers[5]["type"] == "Dense"
    assert dict_layers[5]["units"] == 4
    assert dict_layers[5]["activation"] == "elu"

    assert dict_layers[6]["type"] == "Dense"
    assert dict_layers[6]["units"] == 2
    assert dict_layers[6]["activation"] == "softmax"
