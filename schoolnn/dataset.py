from schoolnn.models import Dataset, Image, Label
from os import makedirs
from io import BytesIO
from zipfile import ZipFile
from django.db import transaction
from PIL import Image as ImagePillow, ImageOps, UnidentifiedImageError

ACCEPTED_IMAGE_FORMATS = [
    "bmp",
    "jpg",
    "jpeg",
    "png",
    "gif",
]


@transaction.atomic
def zip_to_full_dataset(zip_file: BytesIO, dataset: Dataset):
    """Unzip images to storage."""
    dataset_zip = ZipFile(zip_file)
    makedirs(dataset.dir, exist_ok=True)

    label_name_dict = {}

    for entry in dataset_zip.namelist():
        fileending = entry.split(".")[-1]
        if fileending.lower() not in ACCEPTED_IMAGE_FORMATS:
            print("Skip file because of file ending:", entry)
            continue

        label_name = entry.split("/")[0].title()
        if label_name not in label_name_dict:
            label_name_dict[label_name] = Label.objects.create(
                dataset=dataset, name=label_name
            )

        image_binary = BytesIO(dataset_zip.read(entry))
        try:
            image_pil = ImagePillow.open(image_binary)
        except UnidentifiedImageError:
            print("Skip file, seems to be no valid image: ", entry)
            continue

        width, height = image_pil.size
        target_size = min([width, height, 512])
        image_pil = ImageOps.fit(
            image_pil, (target_size, target_size), ImagePillow.ANTIALIAS
        )

        image = Image.objects.create(
            dataset=dataset,
            label=label_name_dict[label_name],
        )
        image_pil.save(image.path)
