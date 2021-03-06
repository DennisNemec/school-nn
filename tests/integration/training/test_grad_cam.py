"""Test schoolnn.training.grad_cam.py"""
from schoolnn.training.grad_cam import get_submodels, grad_cam
from schoolnn.training.batch_generator import numpy_image_batch_to_x_batch
from numpy import random, array
from ..sample_models import get_sample_model


def test_get_submodels():
    model = get_sample_model()
    model_a, model_b = get_submodels(model)

    assert model_a.input_shape == model.input_shape
    assert model_b.input_shape == model_a.output_shape
    assert model_b.output_shape == model.output_shape


def test_grad_cam():
    model = get_sample_model()
    model_a, model_b = get_submodels(model)

    img_rgb = random.randint(255, size=model.input_shape[1:]).astype("uint8")
    img_nn = numpy_image_batch_to_x_batch(array([img_rgb]))[0]

    img_with_gradient = grad_cam(
        last_conv_layer_model=model_a,
        classifier_model=model_b,
        image=img_nn,
        original_image=img_rgb,
    )

    assert img_with_gradient.shape == img_rgb.shape
