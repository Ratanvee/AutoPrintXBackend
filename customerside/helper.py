# core/utils/imagekit_storage.py
from imagekitio import ImageKit
from django.conf import settings

imagekit = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
)

def upload_to_imagekit(file, filename):
    """
    Uploads file to ImageKit and returns the URL
    """
    upload = imagekit.upload_file(
        file=file,
        file_name=filename,
        options={"folder": "/smartdocx/documents/"}  # Folder name in ImageKit
    )
    return upload['url']
