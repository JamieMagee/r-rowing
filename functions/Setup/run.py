import glob
import logging
import os

from oarspotterspider import OarSpotterSpider
from oarspotterimage import OarSpotterImage

#OarSpotterSpider().run()

directory_original = 'blades/original/'
directory_flair = 'blades/flair/'

for file in glob.iglob(directory_original + '**', recursive=True):
  if os.path.isdir(file):
    continue
  try:
    flair = OarSpotterImage(file).resize()
  except ValueError:
    continue
  filename = directory_flair + file.split(directory_original)[1].replace('jpg', 'png')
  dirname = os.path.dirname(filename)
  if not os.path.exists(dirname):
    os.makedirs(dirname)
  with open(filename, 'wb') as f:
    logging.info(f'writing {filename}')
    f.write(flair.getvalue())
