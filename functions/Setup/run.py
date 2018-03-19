import glob
import logging
import os

from oarspotterspider import OarSpotterSpider
from oarspotterimage import OarSpotterImage

#OarSpotterSpider().run()

directory = 'blades/original/'

for file in glob.iglob(directory + '**', recursive=True):
  if os.path.isdir(file):
    continue
  flair = OarSpotterImage(file).resize()
  filename = 'blades/flair/' + file.split(directory)[1].replace('jpg', 'png')
  dirname = os.path.dirname(filename)
  if not os.path.exists(dirname):
    os.makedirs(dirname)
  with open(filename, 'wb') as f:
    logging.info(f'writing {filename}')
    f.write(flair.getvalue())
