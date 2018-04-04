from functools import reduce
from glob import iglob
import math
from operator import add
import os

from PIL import Image, ImageChops


class FlairDiff():

  flair = []

  def __init__(self, dir):
    for file in iglob(dir + '**', recursive=True):
      if os.path.isdir(file):
        continue
      self.flair.append(file)

  def find_match(self, file):
    im = Image.open(file)
    best_match = min(self.flair, key=lambda f: FlairDiff.rms(Image.open(f), im))
    return best_match, FlairDiff.rms(Image.open(best_match), im)

  @staticmethod
  def rms(im1, im2):
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value * ((idx % 256)**2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
    return rms