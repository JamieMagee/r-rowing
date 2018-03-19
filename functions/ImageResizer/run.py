from io import BytesIO
import json
from os import environ

import requests
from azure.storage.blob import BlockBlobService, ContentSettings
from PIL import Image

from oarspotterimage import OarSpotterImage
from flairblobservice import FlairStorageService


def dequeue_message():
    queue_data = open(environ['inputMessage']).read()
    blade_json = json.loads(queue_data)

    name = blade_json['name']
    src = blade_json['src']

    return name, src


name, src = dequeue_message()

# Download original blade image
img_bytes = BytesIO(requests.get(src).content)

# Save original
blob_service = FlairStorageService(name, src)
blob_service.upload_original(img_bytes)

# Make thumbnail
thumbnail_bytes = OarSpotterImage(img_bytes).resize()
blob_service.upload_flair(thumbnail_bytes)