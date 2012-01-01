import gevent.monkey
gevent.monkey.patch_all()

from gserver.routes import Routes
from gserver.request import parse_vals
from gserver.wsgi import WSGIServer

from pprint import pprint

from paver.path import path
from fuzzydict import FuzzyDict
from copy import copy

## for image stuff
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

routes = Routes()
route = routes.route
route_json = routes.route_json

MEME_MAP = FuzzyDict()
IMPACT = path("Impact.ttf")
IMPACT_MAP = {k: v for k, v in [(fontsize, ImageFont.truetype(IMPACT, fontsize)) for fontsize in xrange(1, 400)]}


def populate_map():
    memes = path("./memes")
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


def meme_image(name, line_a, line_b):
    line_a = line_a.upper()
    line_b = line_b.upper()

    image = copy(MEME_MAP[name]['image'])
    draw = ImageDraw.Draw(image)

    font, fontsize, padding = size_text(line_a, image.size[0], 1)
    draw_text(padding, 8, line_a, draw, font)

    font, fontsize, padding = size_text(line_b, image.size[0], 1)
    draw_text(padding, image.size[1] - 16 - fontsize, line_b, draw, font)

    return image


def parse_meme(meme_string):
    # minimum meme == "name/top/botom"
    if meme_string.starts_with("meme") and len(meme_string) > 5:
        divider = "/"
        meme = meme_string.split(m)
        if len(meme) != 3:
            raise Exception("Not a recognized meme format")
        else:
            return meme
    else:
        raise Exception("Not a recognized meme format")


@route("^/example/$")
def example(req):
        return "hello"


@route("^/memeer/(?P<name>[\w\s]+)/(?P<line_a>[\w\s]+)/(?P<line_b>[\w\s]+)[/]?$")
def serve_meme(req, name, line_a, line_b):
    pprint(req.env)
    pprint(req.query_data)

    meme_img = meme_image(name, line_a, line_b)
    img.save(name + ".jpeg")
    return ["A Meme is born!"]


if __name__ == '__main__':
    populate_map()
    port = 8088
    print 'Serving on %d...' % port
    server = WSGIServer(('', port), routes)
    server.serve_forever()
