import glob
from io import BytesIO
import logging
import math
import operator
from functools import reduce
import os

from PIL import Image, ImageChops
import requests

from flairdiff import FlairDiff
from oarspotterimage import OarSpotterImage
from oarspotterspider import OarSpotterSpider

OarSpotterSpider().run()

directory_original = 'blades/original/'
directory_new_flair = 'blades/flair/new/'
directory_existing_flair = 'blades/flair/old/'
flair_url = 'https://a.thumbs.redditmedia.com/4ZaPPvRcOKF6NZfKEl5qDFK8FDYewfqtuaXLaRF-sx4.png'

# for file in glob.iglob(directory_original + '**', recursive=True):
#   if os.path.isdir(file):
#     continue
#   try:
#     flair = OarSpotterImage(file).resize()
#   except ValueError:
#     continue
#   filename = directory_new_flair + file.split(directory_original)[1].replace(
#       'jpg', 'png')
#   dirname = os.path.dirname(filename)
#   if not os.path.exists(dirname):
#     os.makedirs(dirname)
#   with open(filename, 'wb') as f:
#     logging.info(f'writing {filename}')
#     f.write(flair.getvalue())

# r = BytesIO(requests.get(flair_url).content)
# img = Image.open(r)

# width, height = img.size
# slice_size = 14
# upper = 0
# left = 0
# slices = int(math.ceil(height / 14))

# if not os.path.exists(directory_existing_flair):
#   os.makedirs(directory_existing_flair)

# count = 1
# for slice in range(slices):
#   lower = int(count * slice_size)

#   bbox = (left, upper, width, lower)
#   working_slice = img.crop(bbox)
#   upper += slice_size
#   working_slice.convert('RGBA').save(
#       os.path.join(directory_existing_flair,
#                    str(count) + '.png'), 'PNG')
#   count += 1

fd = FlairDiff(directory_new_flair)

for file in glob.iglob(directory_existing_flair + '**'):
  if os.path.isdir(file):
    continue
  match, rms = fd.find_match(file)
  print(f'{file} matches {match} with RMS {rms}')
  if rms > 50:
    print(f'RMS is {rms}')
