import gevent.monkey
gevent.monkey.patch_all()

# debug
from pprint import pformat
from logging import getLogger
# utils
from paver.path import path
from fuzzydict import FuzzyDict
from copy import copy

## for image stuff
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

LOG = getLogger(__name__)

MEME_MAP = FuzzyDict()
IMPACT_FONT = path("Impact.ttf")


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
#{k: v for k, v in [(fontsize, ImageFont.truetype(IMPACT, fontsize)) for fontsize in xrange(1, 400)]}


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
    fontsize = 1  # starting font size
    font = IMPACT[fontsize]
    img_size = img_fraction * size - 16

    breaker = 0

    lo = 0
    hi = IMPACT._max_size

    # faster via binary search?
    while True:
        breaker += 1
        mid = (lo + hi) // 2

        current = IMPACT[mid].getsize(txt)[0]
        next = IMPACT[mid + 1].getsize(txt)[0]

        if current <= img_size and next > img_size:
            break
        elif current < img_size:
            lo = mid + 1
        else:
            hi = mid - 1

        if mid == hi:
            hi = hi * 2

    LOG.debug("time to find fontsize: %s", breaker)
    # while font.getsize(txt)[0] < img_fraction * size - 16:                      # 16 is apple hig padding. i.e. looks purdy
    #     # iterate until the text size is just larger than the criteria
    #     fontsize += 1
    #     font = IMPACT[fontsize]

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
    return item, key


def meme_image(name, line_a, line_b, blank=False):
    item, full_name = fuzzy_meme(name)
    image = copy(item['image'])

    if not blank:
        line_a = line_a.upper()
        line_b = line_b.upper()

        draw = ImageDraw.Draw(image)

        font, fontsize, padding = size_text(line_a, image.size[0], 1)
        draw_text(padding, 8, line_a, draw, font)

        font, fontsize, padding = size_text(line_b, image.size[0], 1)
        draw_text(padding, image.size[1] - 16 - fontsize, line_b, draw, font)

    return image, full_name
