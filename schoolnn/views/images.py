import os

from django.http import HttpResponse
from django.views import View

from schoolnn.models import Image


class ImageView(View):

    def get(self, request, *args, **kwargs):
        image = Image.objects.get(**kwargs)

        image_data = open(
            os.path.join('storage/1', image.path),
            'rb'
        ).read()

        return HttpResponse(image_data, 'image/jpg')
