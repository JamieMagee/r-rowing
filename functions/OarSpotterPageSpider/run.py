import json
import logging

from azure.storage.queue import QueueService, QueueMessageFormat
from grab.spider import Spider, Task
from os import environ
from urllib.parse import urljoin

logging.basicConfig(filename='oarspotterpagespider.log',
                    filemode='w', level=logging.DEBUG)
logger = logging.getLogger(__name__)


class OarSpotterSpider(Spider):

    initial_urls = ['http://www.oarspotter.com']

    visited_pages = set()

    def prepare(self):
        self.queue_service = QueueService(
            connection_string=environ['AzureWebJobsStorage']
        )
        self.queue_service.encode_function = QueueMessageFormat.text_base64encode
        self.queue_name = 'oarspotter-page'
        self.queue_service.create_queue(self.queue_name)

    def task_initial(self, grab, task):
        for link in grab.doc.select('//a[starts-with(@href, "http://www.oarspotter.com/blades/")]'):
            yield Task('list_page', url=link.attr('href'))

    def task_list_page(self, grab, task):
        logging.info(task.url)
        self.queue_page(task.url)

        for link in grab.doc.select('//a[starts-with(@href, "http://www.oarspotter.com/blades/")]'):
            url = link.attr('href')
            if url not in self.visited_pages:
                self.visited_pages.add(url)
                yield Task('list_page', url=url)

    def queue_page(self, url):
        json_message = json.dumps({
            "url": url
        })
        self.queue_service.put_message(
            self.queue_name,
            json_message
        )


OarSpotterSpider().run()
