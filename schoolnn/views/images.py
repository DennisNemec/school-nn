"""All views having to to with images."""
from django.http import HttpResponse
from django.views import View

from schoolnn.models import Image
from schoolnn.views.mixins import AuthMixin


class ImageView(AuthMixin, View):
    """Get a raw jpeg image."""

    @staticmethod
    def get(*_, **kwargs):
        """Respond to the HTTP get request."""
        image = Image.objects.get(**kwargs)

        image_data = open(image.path, "rb").read()

        return HttpResponse(image_data, "image/jpg")
