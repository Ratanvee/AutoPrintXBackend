import base64
from django.conf import settings
from imagekitio import ImageKit


# Initialize ImageKit client (ensure this is done only once)
imagekit = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
)

# 68fe3fb65c7cd75eb837152d
class ImageKitClient():
    def __init__(self, file=None, file_id=None):
        self.file = file
        self.file_id = file_id
        # self.file_name = file.name
        

    def convert_to_binary(self, file):
        self.binary_file = base64.b64encode(file.read())
        return self.binary_file
    
    @property
    def upload_media(self):
        result = imagekit.upload_file(
            file = self.convert_to_binary(self.file),
            file_name = self.file.name,
        )
        return result.response_metadata.raw
    
    # @property
    def delete_media(self, file_id):
        print("this is file id for deletion : ", file_id)
        result = imagekit.delete_file(file_id=file_id)
        print("This is delete media result: ", result)
        return result