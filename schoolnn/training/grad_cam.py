from tensorflow.keras import layers, Model
from tensorflow import keras
import numpy as np
import tensorflow as tf
import matplotlib.cm as cm
from PIL import Image as PillowImage, ImageOps


# Code from
# https://keras.io/examples/vision/grad_cam/
# and slightly adapted


def get_submodels(model: Model):
    last_conv2d = 0
    for i in range(len(model.layers)):
        if isinstance(model.layers[i], layers.Conv2D):
            last_conv2d = i

    last_conv_layer_model = Model(
        model.inputs,
        model.layers[last_conv2d].output,
    )

    classifier_input = layers.Input(
        shape=last_conv_layer_model.output.shape[1:]
    )
    x = classifier_input
    for i in range(last_conv2d + 1, len(model.layers)):
        x = model.layers[i](x)

    classifier_model = Model(classifier_input, x)

    return last_conv_layer_model, classifier_model


def grad_cam(
    last_conv_layer_model: Model,
    classifier_model: Model,
    image: np.array,
    original_image: np.array,
):
    """Calculate heatmap and overlay it ontop of original image."""
    image_array = np.array([image])
    with tf.GradientTape() as tape:
        last_conv_layer_output = last_conv_layer_model(image_array)
        tape.watch(last_conv_layer_output)

        preds = classifier_model(last_conv_layer_output)
        top_pred_index = tf.argmax(preds[0])
        top_class_channel = preds[:, top_pred_index]

    grads = tape.gradient(top_class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    last_conv_layer_output = last_conv_layer_output.numpy()[0]
    pooled_grads = pooled_grads.numpy()
    for i in range(pooled_grads.shape[-1]):
        last_conv_layer_output[:, :, i] *= pooled_grads[i]

    heatmap = np.mean(last_conv_layer_output, axis=-1)

    np_max = np.max(heatmap)
    if np_max == 0:
        pass

    heatmap = np.maximum(heatmap, 0) / np_max
    heatmap = np.uint8(255 * heatmap)

    jet = cm.get_cmap("jet")
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    jet_heatmap = keras.preprocessing.image.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize(
        image.shape[:-1], resample=PillowImage.NEAREST
    )

    original_image_pillow = PillowImage.fromarray(original_image)
    image_grey_scale = ImageOps.grayscale(original_image_pillow).convert("RGB")

    result_array = 0.5 * np.array(image_grey_scale) + 0.5 * np.array(
        jet_heatmap
    )

    return np.uint8(result_array)
