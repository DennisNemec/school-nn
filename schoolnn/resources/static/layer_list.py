def provided_layer():
    provided_layer = [
        {
            "type": "MaxPooling2D",
            "default_name": "MaxPooling2D",
            "input_dimension": 2,
            "output_dimension": 2,
            "hidden": False,
            "properties": [
                {
                    "name": "pool_size",
                    "description": "Poolgröße",
                    "value": {
                        "type": "vector",
                        "dataType": "int",
                        "dimension": 2,
                        "default_value": [2, 2],
                        "min": 1,
                        "max": 32,
                    },
                    "activated": True,
                },
                {
                    "name": "strides",
                    "description": "Strides",
                    "value": {
                        "type": "vector",
                        "dataType": "int",
                        "dimension": 2,
                        "default_value": [1, 1],
                        "min": 1,
                        "max": 32,
                    },
                    "activated": True,
                },
            ],
        },
        {
            "type": "Conv2D",
            "hidden": False,
            "input_dimension": 2,
            "output_dimension": 2,
            "default_name": "Conv2D",
            "properties": [
                {
                    "name": "activation",
                    "description": "Aktivierungsfunktion",
                    "value": {
                        "type": "list",
                        "dataType": "string",
                        "default_value": "relu",
                        "possible_values": [
                            "linear",
                            "tanh",
                            "sigmoid",
                            "softmax",
                            "relu",
                        ],
                    },
                    "activated": False,
                },
                {
                    "name": "filters",
                    "value": {
                        "type": "scalar",
                        "dataType": "int",
                        "default_value": 16,
                        "min": 1,
                        "max": 4096,
                    },
                    "description": "Filter",
                    "activated": True,
                },
                {
                    "name": "strides",
                    "description": "Strides",
                    "value": {
                        "type": "vector",
                        "dataType": "int",
                        "dimension": 2,
                        "default_value": [1, 1],
                        "min": 1,
                        "max": 32,
                    },
                    "activated": True,
                },
                {
                    "name": "kernel_size",
                    "value": {
                        "type": "vector",
                        "dataType": "int",
                        "dimension": 2,
                        "default_value": [3, 3],
                        "min": 1,
                        "max": 32,
                    },
                    "description": "Kernelgröße",
                    "activated": True,
                },
                {
                    "name": "padding",
                    "description": "Padding",
                    "value": {
                        "type": "list",
                        "dataType": "string",
                        "default_value": "valid",
                        "possible_values": ["same", "valid"],
                    },
                    "activated": True,
                },
            ],
        },
        {
            "type": "Flatten",
            "hidden": False,
            "input_dimension": 2,
            "output_dimension": 1,
            "default_name": "Flatten",
            "properties": [],
        },
        {
            "type": "Dense",
            "hidden": False,
            "input_dimension": 1,
            "output_dimension": 1,
            "default_name": "Dense",
            "properties": [
                {
                    "name": "activation",
                    "description": "Aktivierungsfunktion",
                    "value": {
                        "type": "list",
                        "dataType": "string",
                        "default_value": "relu",
                        "possible_values": [
                            "linear",
                            "tanh",
                            "sigmoid",
                            "softmax",
                            "relu",
                        ],
                    },
                    "activated": True,
                },
                {
                    "name": "units",
                    "description": "Anzahl Neuronen",
                    "value": {
                        "type": "scalar",
                        "dataType": "int",
                        "default_value": 32,
                        "min": 1,
                        "max": 4096,
                    },
                    "activated": True,
                },
            ],
        },
        {
            "type": "Dropout",
            "hidden": False,
            "default_name": "Dropout",
            "properties": [
                {
                    "name": "rate",
                    "description": "Dropoutrate",
                    "value": {
                        "type": "scalar",
                        "dataType": "float",
                        "default_value": 0.1,
                        "min": 0,
                        "max": 1,
                        "step": 0.01,
                    },
                    "activated": True,
                }
            ],
        },
        {
            "type": "BatchNormalization",
            "hidden": False,
            "default_name": "Batch normalization",
            "properties": [],
        },
        {
            "type": "Input",
            "hidden": True,
            "default_name": "Input",
            "input_dimension": 2,
            "output_dimension": 2,
            "properties": [
                {
                    "name": "shape",
                    "description": "Eingabegröße",
                    "value": {
                        "type": "vector",
                        "dataType": "int",
                        "dimension": 3,
                        "default_value": [32, 32, 3],
                        "min": 1,
                        "max": 512,
                    },
                    "activated": True,
                },
            ],
        },
    ]

    return provided_layer


def default_layers() -> list:
    """
    Django expected the default value of JSONField
    to be a callable.
    """
    layers = [
        {
            "type": "Input",
            "name": "Input Layer",
            "shape": [
                32,
                32,
                3,
            ],
        },
    ]

    return layers
