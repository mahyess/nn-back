from PIL import Image
from io import BytesIO
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile
from threading import Thread


def compressImage(uploadedImage):
    imageTemproary = Image.open(uploadedImage)
    imageTemproary = imageTemproary.convert('RGB')
    outputIoStream = BytesIO()
    imageTemproary.resize((1020, 573))
    imageTemproary.save(outputIoStream, format='JPEG', quality=20)
    outputIoStream.seek(0)
    uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % uploadedImage.name.split('.')[
                                         0], 'image/jpeg', sys.getsizeof(outputIoStream), None)

    return uploadedImage


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator
