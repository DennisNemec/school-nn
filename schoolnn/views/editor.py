"""
  Module of Architecture-Editor

  It contains the needed view in order to integrate the
  architecture-editor into Django.
"""

from django.views.generic import ListView
from schoolnn.models.models import Architecture


class ArchitectureEditor(ListView):
    """
    The architecture-editor view generates output required for the
    drag-and-drop-field implemented in Vue.js.
    Furthermore it handles incoming requests triggered by the user.
    """

    model = Architecture
    template_name = "editor/editor.html"
    context_object_name = "architecture_data"

    def get_queryset(self):
        provided_layer_list = """
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
                  "default_value": "tanh",
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
                "name": "filter",
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
                "value": {
                  "type": "scalar",
                  "dataType": "int",
                  "default_value": 32,
                  "min": 0,
                  "max": 65535
                },
                "description": "Padding",
                "activated": true
              }
            ]
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

        selected_layer_list = """
        [
          {
            "id": 1,
            "name": "Input Layer",
            "note": "",
            "layer": {
              "type": "MaxPooling2D",
              "properties": [
                {
                  "name": "pool_size",
                  "value": [
                    32,
                    32
                  ]
                },
                {
                  "name": "strides",
                  "value": [
                    0,
                    0
                  ]
                }
              ]
            },
            "layer_information": {
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
            "fixed": true,
            "first": true
          },
          {
            "id": 2,
            "name": "OutputLayer",
            "note": "",
            "layer": {
              "type": "MaxPooling2D",
              "properties": [
                {
                  "name": "pool_size",
                  "value": [
                    32,
                    32
                  ]
                },
                {
                  "name": "strides",
                  "value": [
                    0,
                    0
                  ]
                }
              ]
            },
            "layer_information": {
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
            "fixed": true,
            "last": true
          }
        ]
        """

        return [provided_layer_list, selected_layer_list]
