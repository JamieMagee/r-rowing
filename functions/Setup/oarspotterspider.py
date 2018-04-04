import logging
import os
from urllib.parse import urljoin

from grab.spider import Spider, Task
import requests


class OarSpotterSpider(Spider):

  initial_urls = ['http://www.oarspotter.com']

  visited_pages = set()

  def task_initial(self, grab, task):
    for link in grab.doc.select(
        '//a[starts-with(@href, "http://www.oarspotter.com/blades/")]'):
      yield Task('list_page', url=link.attr('href'))

  def task_list_page(self, grab, task):
    logging.info(task.url)
    yield Task('page_images', url=task.url)

    for link in grab.doc.select(
        '//a[starts-with(@href, "http://www.oarspotter.com/blades/")]'):
      url = link.attr('href')
      if url not in self.visited_pages:
        self.visited_pages.add(url)
        yield Task('list_page', url=url)

  def task_page_images(self, grab, task):
    for blade in grab.doc.select('//td[@class="list"]'):
      try:
        name = blade.select('.//b').text()
        location = blade.select('.//i').text()[2:]
        src = urljoin(task.url, blade.select('.//img/@src')[0].text())
        filename = 'blades/original/' + src.split('/blades/')[1]
      except IndexError:
        continue
      r = requests.get(src)
      OarSpotterSpider.create_dir(filename)
      with open(filename, 'wb') as f:
        f.write(r.content)

  @staticmethod
  def create_dir(filename):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
      os.makedirs(dirname)
