from io import BytesIO
import json
from urllib.parse import urljoin


import azure.functions as func
import requests


from .oarspotterimage import OarSpotterImage


def main(msg: func.QueueMessage, blob: func.Out[bytes]) -> str:
    msg_body = msg.get_json()
    base_url = "http://www.oarspotter.com/blades/"
    img_bytes = BytesIO(requests.get(urljoin(base_url, msg_body["src"])).content)

    try:
        osi = OarSpotterImage(img_bytes)
    except ValueError:
        # Image was wrong size
        exit(0)

    blob.set(osi.resize().getvalue())

    return json.dumps(msg.get_json())
