from django.http import HttpResponse
from django.views import View

from schoolnn.models import Image


class ImageView(View):

    def get(self, request, *args, **kwargs):
        image = Image.objects.get(**kwargs)

        image_data = open(
            "storage/1/{}/{}".format(image.dataset.id, image.id),
            'rb'
        ).read()

        return HttpResponse(image_data, 'image/jpg')
