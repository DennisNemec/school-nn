import json


def default_training_parameters() -> str:
    return json.loads(
        """
        {
            "validation_split": 0.1,
            "learning_rate": 0.01,
            "termination_condition": {
                "seconds": 1800,
                "epochs": 16
            },
            "batch_size": 32,
            "loss_function": "categorical_crossentropy",
            "optimizer": "adam",
            "augmentation_options": {
                "channel_shuffle": true,
                "brightness": true,
                "gaussian_noise": true,
                "dropout_boxes": true,
                "salt_and_pepper": true,
                "jpeg_artifacts": true,
                "vertical_flip": true,
                "distortion": true,
                "rotate": true,
                "scale_and_translate": true,
                "color": true
            }
        }
        """
    )
