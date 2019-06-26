import json
import logging
from typing import Set

import azure.functions as func
from grab.spider import Spider, Task

messages = set()


class OarSpotterSpider(Spider):

    initial_urls = ["http://www.oarspotter.com"]

    visited_pages = set()

    def task_initial(self, grab, task):
        for link in grab.doc.select(
            '//a[starts-with(@href, "http://www.oarspotter.com/blades/")]'
        ):
            yield Task("list_page", url=link.attr("href"))

    def task_list_page(self, grab, task):
        logging.info(task.url)
        self.queue_page(task.url)

        for link in grab.doc.select(
            '//a[starts-with(@href, "http://www.oarspotter.com/blades/")]'
        ):
            url = link.attr("href")
            if url not in self.visited_pages:
                self.visited_pages.add(url)
                yield Task("list_page", url=url)

    def queue_page(self, url):
        messages.add(json.dumps({"url": url}))


def main(timer: func.TimerRequest) -> Set[str]:
    OarSpotterSpider().run()
    return messages
