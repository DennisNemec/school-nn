"""Test schoolnn.training.one_hot_coding."""
from django.test import TestCase
from schoolnn.training.one_hot_coding import (
    get_one_hot_decoder,
    get_one_hot_encoder,
)
from numpy import array_equal
from schoolnn.models import (
    Label,
)
from ..sample_models import (
    get_test_project,
)


class OneHotCodingTestCase(TestCase):
    """Test one hot coding methods."""

    def setUp(self):
        # project has three labels
        self.project = get_test_project()
        self.encoder = get_one_hot_encoder(self.project.dataset)
        self.decoder = get_one_hot_decoder(self.project.dataset)
        self.labels = Label.objects.filter(
            dataset=self.project.dataset
        ).order_by("id")

    def test_encode(self):
        assert array_equal(self.encoder(self.labels[0]), [1.0, 0.0, 0.0])
        assert array_equal(self.encoder(self.labels[1]), [0.0, 1.0, 0.0])
        assert array_equal(self.encoder(self.labels[2]), [0.0, 0.0, 1.0])

    def test_decode(self):
        assert self.decoder([1.0, 0.0, 0.0]) == self.labels[0]
        assert self.decoder([0.0, 1.0, 0.0]) == self.labels[1]
        assert self.decoder([0.0, 0.0, 1.0]) == self.labels[2]

        assert self.decoder([0.9, 0.11, 0.4]) == self.labels[0]
        assert self.decoder([0.5, 0.55, 0.1]) == self.labels[1]
        assert self.decoder([0.8, 0.77, 0.9]) == self.labels[2]

    def test_autocode(self):
        assert self.decoder(self.encoder(self.labels[0])) == self.labels[0]
        assert self.decoder(self.encoder(self.labels[1])) == self.labels[1]
        assert self.decoder(self.encoder(self.labels[2])) == self.labels[2]
