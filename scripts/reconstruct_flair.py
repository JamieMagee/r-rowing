import glob
import math
import os
from configparser import ConfigParser
from functools import reduce
from io import BytesIO
from operator import add
from urllib import request

from PIL import Image, ImageChops
from azure.storage import CloudStorageAccount

replacements = {
    '"': '',
    '/': '',
    '\\': '',
    '*': '',
    '|': ''
}


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def download_images(blob_service):
    if not os.path.exists('images'):
        os.makedirs('images')

    generator = blob_service.list_blobs('images')
    for blob in generator:
        safe_name = replace_all(blob.name, replacements)
        blob_service.get_blob_to_path('images', blob.name, 'images\\' + safe_name + '.png')


def download_flair(flairsheet):
    im = Image.open(BytesIO(request.urlopen(flairsheet).read()))
    width, height = im.size

    if not os.path.exists('flair'):
        os.makedirs('flair')

    for i in range(0, height, 14):
        box = (0, i, 26, i + 14)
        flair = im.crop(box)
        try:
            flair.save('flair\\' + str(i // 14) + '.png')
        except:
            pass


def equal(flair, image):
    im1 = Image.open(flair)
    im2 = Image.open(image)

    h = ImageChops.difference(im1, im2).histogram()

    rms = math.sqrt(reduce(add,
                           map(lambda h, i: h * (i ** 2), h, range(256))
                           ) / (float(im1.size[0]) * im1.size[1]))
    return rms < 10


def compare_images(table_service):
    matched = 0
    total_files = str(len([name for name in os.listdir('flair') if os.path.isfile(os.path.join('flair', name))]))
    for flair in glob.glob1('flair', '*.png'):
        for image in glob.glob1('images', '*.png*'):
            if equal('flair\\' + flair, 'images\\' + image):
                image = image.replace('\'', '\'\'')
                if len(table_service.query_entities('flair', "RowKey eq '" + image[:-4] + "'").items) == 0:
                    table_service.insert_entity('flair',
                                                {'PartitionKey': 'flair', 'RowKey': image[:-4], 'position': flair[:-4]})
                    matched += 1
                    print('Matched ' + str(matched) + ' out of ' + total_files)
                else:
                    continue
                break


flairsheet = 'https://b.thumbs.redditmedia.com/PeieqCQXXBbp93s1m_JGFUF-FJmcpaaqSSmyjxkNOzo.png'
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

table_service.create_table('flair')

download_images(blob_service)
download_flair(flairsheet)
compare_images(table_service)
