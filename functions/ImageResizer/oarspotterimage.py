from io import BytesIO

from PIL import Image


class OarSpotterImage():

    def __init__(self, img):
        self.im = Image.open(img)
        if self.im.size != (436, 48):
            raise ValueError()

    def resize(self):
        self.im = OarSpotterImage.__crop__(OarSpotterImage.__trim__(self.im))
        self.im.thumbnail([100, 14], Image.LANCZOS)
        blob = BytesIO()
        self.im.save(blob, 'PNG')
        return blob

    @staticmethod
    def __trim__(im):
        return im.crop(im.getbbox())

    @staticmethod
    def __crop__(im):
        return im.crop([357, 5, im.size[0] - 6, im.size[1] - 4])
