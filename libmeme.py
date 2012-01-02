import gevent.monkey
gevent.monkey.patch_all()

# debug
from pprint import pprint

# utils
from paver.path import path
from fuzzydict import FuzzyDict
from copy import copy

## for image stuff
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

MEME_MAP = FuzzyDict()
IMPACT = path("Impact.ttf")
IMPACT_MAP = {k: v for k, v in [(fontsize, ImageFont.truetype(IMPACT, fontsize)) for fontsize in xrange(1, 400)]}


def populate_map(meme_path="./memes"):
    memes = path(meme_path)
    for f in memes.files('*.jpeg'):
        name = f.basename()[:-5]
        MEME_MAP[name] = {
            'path': f,
            'image': Image.open(f)
            }
    pprint(MEME_MAP)


def size_text(txt, size, img_fraction=1):
    fontsize = 1  # starting font size
    font = IMPACT_MAP[fontsize]
    while font.getsize(txt)[0] < img_fraction * size - 16:                      # 16 is apple hig padding. i.e. looks purdy
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = IMPACT_MAP[fontsize]

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1
    font = IMPACT_MAP[fontsize]
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


def meme_image(name, line_a, line_b):
    line_a = line_a.upper()
    line_b = line_b.upper()

    item, full_name = fuzzy_meme(name)
    image = copy(item['image'])
    draw = ImageDraw.Draw(image)

    font, fontsize, padding = size_text(line_a, image.size[0], 1)
    draw_text(padding, 8, line_a, draw, font)

    font, fontsize, padding = size_text(line_b, image.size[0], 1)
    draw_text(padding, image.size[1] - 16 - fontsize, line_b, draw, font)

    return image, full_name
