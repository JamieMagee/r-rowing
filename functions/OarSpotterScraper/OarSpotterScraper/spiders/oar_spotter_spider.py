import json
from os import environ
from azure.storage.queue import QueueService
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class OarSpotterSpider(CrawlSpider):
    name = "oarspotter"
    allowed_domains = ['oarspotter.com']
    start_urls = ['http://www.oarspotter.com']
    queue_name = 'blades'

    queue_service = QueueService(account_name=environ['STORAGE_ACCOUNT_NAME'],
                                 account_key=environ['STORAGE_ACCOUNT_KEY'])

    rules = [
        Rule(LinkExtractor(allow=(r'blades/\w+',)),
             callback='parse_blades', follow=True)
    ]

    def __init__(self, *a, **kw):
        super(OarSpotterSpider, self).__init__(*a, **kw)
        self.queue_service.create_queue(self.queue_name)

    def parse_blades(self, response):
        for blade in response.xpath('//td[@class="list"]'):
            try:
                name = blade.xpath('.//b[1]/text()').extract()[0]
                url = blade.xpath('.//img/@src').extract()[0]
            except IndexError:
                continue
            url = response.urljoin(url)
            self.queue_blade(name, url)
        return response.xpath('//a[starts-with(@href, "http://www.oarspotter.com/blades/")]').extract()

    def queue_blade(self, name, url):
        json_message = json.dumps({
            "name": name,
            "url": url
        })
        self.queue_service.put_message(
            self.queue_name,
            json_message
        )
