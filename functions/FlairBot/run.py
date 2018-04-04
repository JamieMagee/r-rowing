import datetime
import json
import time
from io import BytesIO
from urllib import request, parse

import praw
from PIL import Image
from azure.storage import CloudStorageAccount

from flairblobservice import FlairBlobService
from subredditflair import SubredditFlair


def get_flair_info(message):
  info = json.loads('{' + message.body + '}')
  return info.popitem()


def assign_flair(r, subreddit message, text, position):
  r.set_flair(subreddit, message.author, text, position)
  message.mark_as_read()


def get_css_images(r, subreddit):
  stylesheet = r.get_stylesheet(subreddit)
  css = stylesheet['stylesheet']
  image = next(image['url']
               for image in stylesheet['images']
               if image['name'] == 'flairsheet')
  return css, image


def upload_image(r, image, subreddit):
  r._request(
      r.config['upload_image'],
      data={
          'r': subreddit,
          'img_type': 'png',
          'name': 'flairsheet'
      },
      files={'file': image.getvalue()})


def make_new_flairsheet(flairsheet, new_flair):
  flairsheet = Image.open(BytesIO(request.urlopen(flairsheet).read()))
  new_flair = Image.open(
      BytesIO(blob_service.get_blob_to_bytes('images', new_flair).content))

  new_flairsheet = Image.new(
      "RGBA", [flairsheet.size[0], flairsheet.size[1] + new_flair.size[1]])
  new_flairsheet.paste(flairsheet, (0, 0))
  new_flairsheet.paste(new_flair, (0, flairsheet.size[1], flairsheet.size[0],
                                   flairsheet.size[1] + new_flair.size[1]))
  new_flairsheet = new_flairsheet.convert('P', palette=Image.ADAPTIVE)

  flairsheet = BytesIO()
  new_flairsheet.save(flairsheet, 'png', optimize=True)
  position = new_flairsheet.size[1] // new_flair.size[1] - 1

  return flairsheet, position, new_flair.size[1]


def append_css(r, subreddit, css, position, height):
  new_css = f'.flair-{str(position)}{{background-position:0-{str(height * position)}px}}'
  r.set_stylesheet(subreddit, css + new_css)

subreddit_flair = SubredditFlair(env['SUBREDDIT'])
flair_blob_service = FlairBlobService()

for message in subreddit_flair.get_messages()):
  logging.info(f'received mesage from {message.author.name}')
  try:
    message_info = subreddit_flair.get_message_info(message)
    if flair_blob_service.flair_exists(message_info):
        # Flair exists, and is already in spritesheet
        flair_entity = flair_blob_service.get_flair_entity(message_info)
        flair_position_entity = flair_blob_service.get_flair_position_entity(flair_entity)
        subreddit_flair.assign_flair(message_info)
    else:
        try:
            # Flair exists, but isn't in spritesheet
            flair_entity = flair_blob_service.get_flair_entity(message_info)
            subreddit_flair.assign_flair(message.author, flair_entity)
        except:
            # Flair doesn't exist


    if file in [blob.name for blob in list(blob_service.list_blobs('images'))]:
      if len(
          table_service.query_entities(
              'flair', "RowKey eq '" + parse.quote_plus(file) + "'").items) > 0:
        flair = table_service.get_entity('flair', 'flair',
                                         parse.quote_plus(file))
        try:
          assign_flair(r, message, text, int(flair.position))
        except:
          assign_flair(r, message, text, flair.position.value)
        r.send_message(message.author, 'Rowing flair success',
                       'Your flair has been set')
        logging.info('Assigned existing flair: ' + file + ' with text: ' +
                     text + ' to user: ' + message.author.name)

      else:
        css, flairsheet = get_css_images(r, subreddit)

        flairsheet, position, height = make_new_flairsheet(flairsheet, file)
        logging.info('Generated new flairsheet')

        try:
          upload_image(r, flairsheet, subreddit)
          append_css(r, subreddit, css, position, height)
          table_service.insert_entity(
              'flair', {
                  'PartitionKey': 'flair',
                  'RowKey': parse.quote_plus(file),
                  'position': position
              })

          assign_flair(r, message, text, position)
          r.send_message(message.author, 'Rowing flair success',
                         'Your flair has been set')
          logging.info('Assigned flair: ' + file + ' with text: ' + text +
                       ' to user: ' + message.author.name)
        except praw.errors.BadCSS as e:
          message.mark_as_read()
          r.send_message(message.author, 'Rowing flair error',
                         'Oops! Something went wrong.')
          r.send_message('jammie1', 'Rowing flair error',
                         'Hit CSS limit. Check logging.infos.')
    else:
      message.mark_as_read()
      r.send_message(
          message.author, 'Rowing flair error',
          'Sorry, I couldn\'t find that flair. Please try selecting your '
          'flair again https://www.reddit.com/r/rowing/wiki/flair')
      logging.info('Couldn\'t find flair with name:' + file)
  except Exception as e:
    print(e)
    message.mark_as_read()
    r.send_message(message.author, 'Rowing flair error',
                   'Sorry, I couldn\'t find a flair with that filename')
    logging.info('Error reading user message')
