import json

layer_list = """
        [
          {
            "type": "MaxPooling2D",
            "default_name": "MaxPooling2D",
            "properties": [
              {
                "name": "pool_size",
                "description": "Poolgröße",
                "value": {
                  "type": "vector",
                  "dataType": "int",
                  "dimension": 2,
                  "default_value": [
                    32,
                    32
                  ],
                  "min": 0,
                  "max": 65535
                },
                "activated": true
              },
              {
                "name": "strides",
                "description": "Strides",
                "value": {
                  "type": "vector",
                  "dataType": "int",
                  "dimension": 2,
                  "default_value": [
                    0,
                    0
                  ],
                  "min": 0,
                  "max": 65535
                },
                "activated": true
              }
            ]
          },
          {
            "type": "Conv2D",
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
                    "tanh",
                    "sigmoid",
                    "softmax",
                    "relu"
                  ]
                },
                "activated": false
              },
              {
                "name": "filters",
                "value": {
                  "type": "scalar",
                  "dataType": "int",
                  "default_value": 0,
                  "min": 0,
                  "max": 65535
                },
                "description": "Filter",
                "activated": true
              },
              {
                "name": "strides",
                "description": "Strides",
                "value": {
                  "type": "vector",
                  "dataType": "int",
                  "dimension": 2,
                  "default_value": [
                    0,
                    0
                  ],
                  "min": 0,
                  "max": 65535
                },
                "activated": true
              },
              {
                "name": "kernel_size",
                "value": {
                  "type": "vector",
                  "dataType": "int",
                  "dimension": 2,
                  "default_value": [
                    32,
                    32
                  ],
                  "min": 0,
                  "max": 65535
                },
                "description": "Kernelgröße",
                "activated": true
              },
              {
                "name": "padding",
                "description": "Padding",
                "value": {
                  "type": "list",
                  "dataType": "string",
                  "default_value": "valid",
                  "possible_values": [
                    "same",
                    "valid"
                  ]
                },
                "activated": true
              }
            ]
          },
          {
            "type": "Flatten",
            "default_name": "Flatten",
            "properties": []
          },
          {
            "type": "Dense",
            "default_name": "Dense",
            "properties": [
              {
                "name": "activation",
                "description": "Aktivierungsfunktion",
                "value": {
                  "type": "list",
                  "dataType": "string",
                  "default_value": "tanh",
                  "possible_values": [
                    "tanh",
                    "sigmoid",
                    "softmax",
                    "relu"
                  ]
                },
                "activated": true
              },
              {
                "name": "units",
                "description": "Anzahl Neuronen",
                "value": {
                  "type": "scalar",
                  "dataType": "int",
                  "default_value": 32,
                  "min": 0,
                  "max": 65535
                },
                "activated": true
              }
            ]
          },
          {
            "type": "Dropout",
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
                  "step": 0.01
                },
                "activated": true
              }
            ]
          },
          {
            "type": "BatchNormalization",
            "default_name": "Batch normalization",
            "properties": []
          }
        ]
        """


def default_layers() -> str:
    """
    Django expected the default value of JSONField
    to be a callable.
    """
    return json.loads(
        """
        [
          {
            "type": "MaxPooling2D",
            "name": "Input Layer",
            "pool_size": [
              32,
              32
            ],
            "strides": [
              0,
              0
            ]
          },
          {
            "type": "MaxPooling2D",
            "name": "Output Layer",
            "pool_size": [
              32,
              32
            ],
            "strides": [
              0,
              0
            ]
          }
        ]
        """
    )
