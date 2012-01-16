import gevent.monkey
gevent.monkey.patch_all()
import gevent

# debug
from pprint import pformat

# utils
from paver.path import path
from fuzzydict import FuzzyDict
from copy import copy
from cStringIO import StringIO
# from greplin import scales
# import time

## for image stuff
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from logging import getLogger
LOG = getLogger(__name__)

IMG_TYPE_MAP = {
    'PNG': 'PNG',
    'JPG': 'JPEG',
    'JPEG': 'JPEG',
    'GIF': 'GIF',
}

MEME_MAP = FuzzyDict()

# STATS = scales.collection('/libmeme',
#     scales.Stat('currentTime', time.time),
#     scales.PmfStat('size_text'),
#     scales.PmfStat('draw_text'),
#     scales.PmfStat('draw_text2'),
    # )


class FontMap(dict):
    _max_size = 1

    def __init__(self, p=None):
        super(FontMap, self).__init__()
        self.ttf = path(p) if p else None

    def set_ttf_path(self, p):
        self.ttf = path(p)
        self.clear()

    def __missing__(self, key):
        if self.ttf:
            f = ImageFont.truetype(self.ttf, key)
        else:
            raise Exception("Font not yet set")

        self[key] = f

        if key > self._max_size:
            self._max_size = key
        return self[key]

    def max_size(self):
        return self._max_size

IMPACT = FontMap()


def _populate_item(f, meme_map):
    name = f.basename()[:-len(f.ext)]
    LOG.info("loading meme %s", name)
    meme_map[name] = {
        'path': f,
        'image': Image.open(f)
        }


def populate_map(meme_path):
    memes = path(meme_path)
    meme_openers = []

    for f in memes.files('*.jpeg'):
        pi = gevent.Greenlet.spawn(_populate_item, f, MEME_MAP)
        meme_openers.append(pi)

    gevent.joinall(meme_openers)
    LOG.debug(pformat(MEME_MAP))


def size_text(txt, size, img_fraction=1):
    #TODO adam: care about height?
    img_size = img_fraction * size - 16

    # with STATS.size_text.time():
    breaker = 0
    lo = 0
    hi = IMPACT._max_size

    # faster via binary search?
    while True:
        mid = (lo + hi) // 2

        current = IMPACT[mid].getsize(txt)[0]
        next = IMPACT[mid + 1].getsize(txt)[0]

        if current <= img_size and next >= img_size:
            break
        elif current < img_size:
            lo = mid + 1
        else:
            hi = mid - 1

        if mid == hi:
            hi = hi * 2
    LOG.debug("time to find fontsize: %s", breaker)

    # optionally de-increment to be sure it is less than criteria
    fontsize = mid - 1
    font = IMPACT[fontsize]
    extra = size - font.getsize(txt)[0]
    padding = extra / 2
    return (font, fontsize, padding)


def draw_text(x, y, txt, draw, font, fillcolor="white", shadowcolor="black"):
    inc = 2
    xp = x + inc
    xm = x - inc
    yp = y + inc
    ym = y - inc

    # put the text shadow on the image
    draw.text((xm, ym), txt, font=font, fill=shadowcolor)
    draw.text((xp, ym), txt, font=font, fill=shadowcolor)
    draw.text((xm, yp), txt, font=font, fill=shadowcolor)
    draw.text((xp, yp), txt, font=font, fill=shadowcolor)

    # put the actual text on top of the shadow
    draw.text((x, y), txt, font=font, fill=fillcolor)


def fuzzy_meme(lookfor):
    matched, key, item, ratio = MEME_MAP._search(lookfor)
    if not matched and not item:
        raise KeyError("'%s'. closest match: '%s' with ratio %.3f" % (str(lookfor), str(key), ratio))
    return key


def meme_image(full_name, line_a, line_b, blank=False):
    # with STATS.draw_text.time():
    item = MEME_MAP[full_name]
    image = copy(item['image'])

    line_a = line_a.upper()
    line_b = line_b.upper()

    draw = ImageDraw.Draw(image)

    if line_a:
        font, fontsize, padding = size_text(line_a, image.size[0], 1)
        draw_text(padding, 8, line_a, draw, font)

    if line_b:
        font, fontsize, padding = size_text(line_b, image.size[0], 1)
        draw_text(padding, image.size[1] - 16 - fontsize, line_b, draw, font)

    return image


def bufferize_image(meme_img, img_type, size=None):
    img_type = IMG_TYPE_MAP[img_type.upper()]
    # put the image in a string buffer for output
    f = StringIO()
    if size:
        x, y = size.split("x")
        meme_img.thumbnail((int(x), int(y)), Image.ANTIALIAS)
    meme_img.save(f, img_type.upper(), optimize=1)
    length = f.tell()
    f.seek(0)
    return f, length
