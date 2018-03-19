import json
import logging
from os import environ
from urllib.parse import urljoin

from azure.storage.queue import QueueService, QueueMessageFormat
from requests_html import HTMLSession

logger = logging.getLogger(__name__)

queue_data = open(environ['inputMessage']).read()
message_json = json.loads(queue_data)
url = message_json['url']

queue_service = QueueService(
    connection_string=environ['AzureWebJobsStorage'],
)
queue_service.encode_function = QueueMessageFormat.text_base64encode
queue_name = 'oarspotter-image'
queue_service.create_queue(queue_name)


def queue_image(name, src):
    json_message = json.dumps({
        "name": name,
        "src": src
    })
    queue_service.put_message(
        queue_name,
        json_message
    )


session = HTMLSession()
r = session.get(url)

for blade in r.html.xpath('//td[@class="list"]'):
    try:
        name = blade.xpath('.//b[1]/text()')[0]
        src = urljoin(url, blade.xpath('.//img/@src')[0])
    except IndexError:
        continue
    queue_image(name, src)
