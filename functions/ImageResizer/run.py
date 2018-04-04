from io import BytesIO
import json
from os import environ
from sys import exit

import requests
from azure.storage.blob import BlockBlobService, ContentSettings
from PIL import Image

from oarspotterimage import OarSpotterImage
from flairblobservice import FlairStorageService


def dequeue_message():
  queue_data = open(environ['inputMessage']).read()
  blade_json = json.loads(queue_data)

  name = blade_json['name']
  location = blade_json['location']
  src = blade_json['src']

  return "Assumption College", "Worchester, VA", "http://www.oarspotter.com/blades/USA/Uni/Assumption.png"
  #return name, location, src


name, location, src = dequeue_message()

# Download original blade image
img_bytes = BytesIO(requests.get(src).content)

try:
  osi = OarSpotterImage(img_bytes)
except ValueError:
  # Image was wrong size
  exit(0)

blob_service = FlairStorageService(name, location, src)
# Make thumbnail
thumbnail_bytes = osi.resize()
blob_service.upload_flair(thumbnail_bytes)

# Create table row
blob_service.create_table_row()