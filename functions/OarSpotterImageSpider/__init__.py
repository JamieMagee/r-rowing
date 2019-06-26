import json
from typing import Set
from urllib.parse import urljoin


import azure.functions as func
from requests_html import HTMLSession


def main(msg: func.QueueMessage) -> Set[str]:
    url = msg.get_json()["url"]
    images = set()
    session = HTMLSession()
    r = session.get(url)
    for blade in r.html.xpath('//td[@class="list"]'):
        try:
            name = blade.xpath(".//b/text()")[0]
            location = blade.xpath(".//i/text()")[0][2:]
            src = urljoin(url, blade.xpath(".//img/@src")[0]).replace(
                "http://www.oarspotter.com/blades/", ""
            )
            images.add(json.dumps({"name": name, "location": location, "src": src}))
        except IndexError:
            continue
    return images

