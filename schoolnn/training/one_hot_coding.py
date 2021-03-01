"""Generate one hot encoders / decoders for datasets."""
import django

django.setup()

from typing import Callable, List
from ..models import Dataset, Label


def get_one_hot_encoder(dataset: Dataset) -> Callable:
    """Make lable to hot encoded array."""
    label_list = Label.objects.filter(dataset_id=dataset.id).order_by("id")

    def encoder(label: Label) -> List[int]:
        array = []
        for label_entry in label_list:
            array.append((label.id == label_entry.id) * 1)
        return array

    return encoder


def get_one_hot_decoder(dataset: Dataset) -> Callable:
    """Make hot encoded array to a label."""
    label_list = Label.objects.filter(dataset_id=dataset.id).order_by("id")

    def decoder(array: List[int]) -> Label:
        # print("DEC", array)
        max_value = array[0]
        matched_label = label_list[0]

        for array_value, label_entry in zip(array, label_list):
            if array_value > max_value:
                max_value = array_value
                matched_label = label_entry
        return matched_label

    return decoder
