import gevent.monkey
gevent.monkey.patch_all()
from gevent import Greenlet

# debug
from pprint import pformat

# utils
from paver.path import path
from fuzzydict import FuzzyDict
from copy import copy
from cStringIO import StringIO
from greplin import scales
import time

## for image stuff
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from logging import getLogger
LOG = getLogger(__name__)

MEME_MAP = FuzzyDict()
IMPACT_FONT = path("Impact.ttf")

STATS = scales.collection('/libmeme',
    scales.Stat('currentTime', time.time),
    scales.PmfStat('size_text'),
    scales.PmfStat('draw_text'),
    scales.PmfStat('draw_text2'),
    )


class ImpactMap(dict):
    _max_size = 1

    def __missing__(self, key):
        self[key] = ImageFont.truetype(IMPACT_FONT, key)
        if key > self._max_size:
            self._max_size = key
        return self[key]

    def max_size(self):
        return self._max_size

IMPACT = ImpactMap()


def populate_map(meme_path="./memes"):
    memes = path(meme_path)
    for f in memes.files('*.jpeg'):
        name = f.basename()[:-5]
        MEME_MAP[name] = {
            'path': f,
            'image': Image.open(f)
            }
    LOG.debug(pformat(MEME_MAP))


def size_text(txt, size, img_fraction=1):
    #TODO adam: care about height?
    img_size = img_fraction * size - 16

    with STATS.size_text.time():
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
    a = Greenlet.spawn(draw.text, (xm, ym), txt, font=font, fill=shadowcolor)
    b = Greenlet.spawn(draw.text, (xp, ym), txt, font=font, fill=shadowcolor)
    c = Greenlet.spawn(draw.text, (xm, yp), txt, font=font, fill=shadowcolor)
    d = Greenlet.spawn(draw.text, (xp, yp), txt, font=font, fill=shadowcolor)

    # put the actual text on top of the shadow
    e = Greenlet.spawn(draw.text, (x, y), txt, font=font, fill=fillcolor)

    gevent.joinall((a, b, c, d, e))


def fuzzy_meme(lookfor):
    matched, key, item, ratio = MEME_MAP._search(lookfor)
    if not matched and not item:
        raise KeyError("'%s'. closest match: '%s' with ratio %.3f" % (str(lookfor), str(key), ratio))
    return key


def meme_image(full_name, line_a, line_b, blank=False):
    with STATS.draw_text.time():
        item = MEME_MAP[full_name]
        image = copy(item['image'])

        line_a = line_a.upper()
        line_b = line_b.upper()

        draw = ImageDraw.Draw(image)

        a = None
        b = None

        if line_a:
            font, fontsize, padding = size_text(line_a, image.size[0], 1)
            a = Greenlet.spawn(draw_text, padding, 8, line_a, draw, font)

        if line_b:
            font, fontsize, padding = size_text(line_b, image.size[0], 1)
            b = Greenlet.spawn(draw_text, padding, image.size[1] - 16 - fontsize, line_b, draw, font)

        gevent.joinall((a, b) if line_a and line_b else a if line_a else b if line_b else ())       # stupid speed optimization

        return image


def bufferize_image(meme_img, _IMG_TYPE):
        # put the image in a string buffer for output
    f = StringIO()
    meme_img.save(f, _IMG_TYPE)
    length = f.tell()
    f.seek(0)
    return f, length
