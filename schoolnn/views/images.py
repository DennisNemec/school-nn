"""All views having to to with images."""
from django.http import HttpResponse
from django.views import View

from schoolnn.models import Image
from schoolnn.views.mixins import LoginRequiredMixin


class ImageView(LoginRequiredMixin, View):
    """Get a raw jpeg image."""

    def get(self, *args, **kwargs):
        """Respond to the HTTP get request."""
        image = Image.objects.filter(dataset__user=self.request.user).get(
            **kwargs
        )

        image_data = open(image.path, "rb").read()

        return HttpResponse(image_data, "image/jpg")
