import datetime
import json
import time
from io import BytesIO
from urllib import request, parse

import praw
from PIL import Image
from azure.storage import CloudStorageAccount
from settings import user_agent
from tokens import subreddit, username, password, storage_account_name, storage_account_key


def get_flair_info(message):
    info = json.loads('{' + message.body + '}')
    return info.popitem()


def assign_flair(r, message, text, position):
    r.set_flair(subreddit, message.author, text, position)
    message.mark_as_read()


def get_css_images(r, subreddit):
    stylesheet = r.get_stylesheet(subreddit)
    css = stylesheet['stylesheet']
    image = next(image['url'] for image in stylesheet['images'] if image['name'] == 'flairsheet')
    return css, image


def upload_image(r, image, subreddit):
    r._request(r.config['upload_image'],
               data={'r': subreddit, 'img_type': 'png', 'name': 'flairsheet'},
               files={'file': image.getvalue()})


def make_new_flairsheet(flairsheet, new_flair):
    flairsheet = Image.open(BytesIO(request.urlopen(flairsheet).read()))
    new_flair = Image.open(
        BytesIO(blob_service.get_blob_to_bytes('images', new_flair).content))

    new_flairsheet = Image.new("RGBA", [flairsheet.size[0], flairsheet.size[1] + new_flair.size[1]])
    new_flairsheet.paste(flairsheet, (0, 0))
    new_flairsheet.paste(new_flair, (
        0, flairsheet.size[1], flairsheet.size[0], flairsheet.size[1] + new_flair.size[1]))
    new_flairsheet = new_flairsheet.convert('P', palette=Image.ADAPTIVE)

    flairsheet = BytesIO()
    new_flairsheet.save(flairsheet, 'png', optimize=True)
    position = new_flairsheet.size[1] // new_flair.size[1] - 1

    return flairsheet, position, new_flair.size[1]


def append_css(r, subreddit, css, position, height):
    new_css = '.flair-' + str(position) + '{background-position: 0 -' + str(
        height * position) + 'px}'
    r.set_stylesheet(subreddit, css + new_css)


def log(message):
    table_service.insert_entity('logs',
                                {'PartitionKey': 'flair', 'RowKey': str(datetime.datetime.now()),
                                 'text': message})
    print('[*] ' + message)


storage_account = CloudStorageAccount(storage_account_name, storage_account_key)

table_service = storage_account.create_table_service()
blob_service = storage_account.create_block_blob_service()

blob_service.create_container('images', public_access='container')
table_service.create_table('flair')
table_service.create_table('logs')

r = praw.Reddit(user_agent)
r.login(username, password)
r.config.decode_html_entities = True

while True:
    for message in (m for m in r.get_unread(limit=None)):
        log('received mesage from ' + message.author.name)
        try:
            file, text = get_flair_info(message)
            if file in [blob.name for blob in list(blob_service.list_blobs('images'))]:
                if len(table_service.query_entities('flair', "RowKey eq '" + parse.quote_plus(
                        file) + "'").items) > 0:
                    flair = table_service.get_entity('flair', 'flair', parse.quote_plus(file))
                    try:
                        assign_flair(r, message, text, int(flair.position))
                    except:
                        assign_flair(r, message, text, flair.position.value)
                    r.send_message(message.author, 'Rowing flair success',
                                   'Your flair has been set')
                    log(
                        'Assigned existing flair: ' + file + ' with text: ' + text + ' to user: ' + message.author.name)

                else:
                    css, flairsheet = get_css_images(r, subreddit)

                    flairsheet, position, height = make_new_flairsheet(flairsheet, file)
                    log('Generated new flairsheet')

                    try:
                        upload_image(r, flairsheet, subreddit)
                        append_css(r, subreddit, css, position, height)
                        table_service.insert_entity('flair',
                                                    {'PartitionKey': 'flair', 'RowKey': parse.quote_plus(file),
                                                     'position': position})

                        assign_flair(r, message, text, position)
                        r.send_message(message.author, 'Rowing flair success',
                                       'Your flair has been set')
                        log(
                            'Assigned flair: ' + file + ' with text: ' + text + ' to user: ' + message.author.name)
                    except praw.errors.BadCSS as e:
                        message.mark_as_read()
                        r.send_message(message.author, 'Rowing flair error',
                                       'Oops! Something went wrong.')
                        r.send_message('jammie1', 'Rowing flair error',
                                       'Hit CSS limit. Check logs.')
            else:
                message.mark_as_read()
                r.send_message(message.author, 'Rowing flair error',
                               'Sorry, I couldn\'t find that flair. Please try selecting your '
                               'flair again https://www.reddit.com/r/rowing/wiki/flair')
                log('Couldn\'t find flair with name:' + file)
        except Exception as e:
            print(e)
            message.mark_as_read()
            r.send_message(message.author, 'Rowing flair error',
                           'Sorry, I couldn\'t find a flair with that filename')
            log('Error reading user message')

    time.sleep(30)
