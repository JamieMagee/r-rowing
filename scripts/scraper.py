import datetime
import os
import time
from configparser import ConfigParser
from io import BytesIO
from urllib import parse, request

import praw
from PIL import Image
from azure.storage import CloudStorageAccount
from azure.storage.blob.models import ContentSettings
from bs4 import BeautifulSoup


def log(message):
    table_service.insert_entity('logs',
                                {'PartitionKey': 'scraper', 'RowKey': str(datetime.datetime.now()), 'text': message})
    print('[*] ' + message)


def download_images(url, level):
    global website
    netloc = parse.urlsplit(url).netloc.split('.')
    if netloc[-2] + netloc[-1] != website:
        return

    global url_list
    if url in url_list:
        return

    try:
        urlcontent = request.urlopen(url).read().decode('latin-1')
        url_list.append(url)
        log(url)
    except:
        return

    soup = BeautifulSoup(''.join(urlcontent), 'lxml')
    rows = soup.findAll('td', {'class': 'list'})
    for row in rows:
        if row.find('b'):
            name = row.find('b').text.strip()
            img_url = row.find('img')['src']
            if img_url.lower().endswith('.png'):
                try:
                    resize_image(BytesIO(request.urlopen(parse.urljoin(url, img_url)).read()), name)
                except:
                    pass

    if level > 0:
        link_tags = soup.findAll('a')
        if len(link_tags) > 0:
            for linkTag in link_tags:
                try:
                    link_url = linkTag['href']
                    download_images(link_url, level - 1)
                except:
                    pass


def resize_image(fp, name):
    im = Image.open(fp)
    if im.size != (436, 48):
        return
    im = crop(trim(im))
    im.thumbnail([100, 14], Image.LANCZOS)
    blob = BytesIO()
    im.save(blob, 'png')
    blob_service.create_blob_from_bytes('images', name, blob.getvalue(),
                                        content_settings=ContentSettings(content_type='image/png'))
    log('resized ' + name)


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def trim(im):
    return im.crop(im.getbbox())


def crop(im):
    return im.crop([357, 5, im.size[0] - 6, im.size[1] - 4])


if os.path.isfile(os.path.join(os.path.dirname(__file__), 'settings.cfg')):
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'settings.cfg'))

    subreddit = config.get('reddit', 'subreddit')
    username = config.get('reddit', 'username')
    password = config.get('reddit', 'password')

    storage_account_name = config.get('azure', 'name')
    storage_account_key = config.get('azure', 'key')
else:
    subreddit = os.getenv('SUBREDDIT')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
    storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')

storage_account = CloudStorageAccount(storage_account_name, storage_account_key)

table_service = storage_account.create_table_service()
blob_service = storage_account.create_block_blob_service()

blob_service.create_container('images', public_access='container')
table_service.create_table('logs')

rooturl = 'http://www.oarspotter.com'
netloc = parse.urlsplit(rooturl).netloc.split('.')
website = netloc[-2] + netloc[-1]

while True:
    url_list = []
    log('scraping oarspotter')
    download_images(rooturl, 2)
    log('finished scraping oarspotter')

    replacements = {'\'': '\\\'',
                    '(': '\(',
                    ')': '\)'}

    log('Generating dictionary')
    flair, content = {}, 'Howto\n==\nClick the link for your club, edit the "YourTextHere" part to whatever you want, but leave everything else including the quotation marks. Submit the message form and wait for max. 5 minutes. If it doesn\'t work, message the mods.\n\n'

    for file in blob_service.list_blobs('images'):
        escaped_name = replace_all(file.name, replacements)
        content += '* [' + file.name + '](//reddit.com/message/compose/?to=RowingFlairBot&subject=f&message={"' + escaped_name + '":"YourTextHere"})\n'

    r = praw.Reddit('RowingFlair by /u/Jammie1')
    r.login(username, password)

    r.edit_wiki_page(subreddit, 'flair', content, '')
    log('Done!')
    time.sleep(86400)
