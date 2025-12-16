import os

from django.core.exceptions import ValidationError
from PIL import Image


def validate_icon_image_size(image):
    if image:
      with Image.open(image) as img:
        if img.width > 70 or img.height > 70:
          raise ValidationError(
            f"The maximum allowed dimentions for the image 70X70-size of image you uploaded: {img.size}"
          )

def validate_image_file_extention(value):
    ext = os.path.splitext(value.name)[1]
    valid_extentions = [".jpeg", ".jpg",".png",".gif"]
    if not ext.lower() in valid_extentions:
       raise ValidationError("Unsupported file extention")