import json
from os import environ

import requests
from azure.storage.blob import BlockBlobService

queue_data = open(environ['inputDocument']).read()
blade_json = json.loads(queue_data)

name = blade_json['name']
url = blade_json['url']

img_bytes = requests.get(url, streaming=True).raw.data
blob_name = f'original/{url.split("/blades/")[1]}'
blob_service = BlockBlobService(account_name=environ['STORAGE_ACCOUNT_NAME'],
                                 account_key=environ['STORAGE_ACCOUNT_KEY'])
resp = blob_service.create_blob_from_bytes(
    'blades',
    blob_name,
    img_bytes

)
print(resp)