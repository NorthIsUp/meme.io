# from gevent.pywsgi import WSGIServer
from paver.path import path
from pprint import pprint
from fuzzydict import FuzzyDict
from copy import copy

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
# from pil import ImageOps

MEME_MAP = FuzzyDict()
IMPACT = path("Impact.ttf")
FONT = ImageFont.load_default()


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
    font = ImageFont.truetype(IMPACT, fontsize)
    while font.getsize(txt)[0] < img_fraction * size - 16:  # 16 is apple hig padding. i.e. looks purdy
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(IMPACT, fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1
    font = ImageFont.truetype(IMPACT, fontsize)
    extra = size - font.getsize(txt)[0]
    padding = extra / 2
    return (font, fontsize, padding)


def draw_text(x, y, txt, draw, font, fillcolor="white", shadowcolor="black"):
    # xx = x
    inc = 2
    xp = x + inc
    xm = x - inc
    # yy = y
    yp = y + inc
    ym = y - inc

    draw.text((xm, y), txt, font=font, fill=shadowcolor)
    draw.text((xp, y), txt, font=font, fill=shadowcolor)
    draw.text((x, ym), txt, font=font, fill=shadowcolor)
    draw.text((x, yp), txt, font=font, fill=shadowcolor)

    # thicker border
    draw.text((xm, ym), txt, font=font, fill=shadowcolor)
    draw.text((xp, ym), txt, font=font, fill=shadowcolor)
    draw.text((xm, yp), txt, font=font, fill=shadowcolor)
    draw.text((xp, yp), txt, font=font, fill=shadowcolor)

    draw.text((x, y), txt, font=font, fill=fillcolor)  # put the text on the image


def meme_image(name, line_a, line_b):
    line_a = line_a.upper()
    line_b = line_b.upper()

    image = copy(MEME_MAP[name]['image'])
    draw = ImageDraw.Draw(image)

    x, y = 8, 16

    font, fontsize, padding = size_text(line_a, image.size[0], 1)
    draw_text(padding, y, line_a, draw, font)

    font, fontsize, padding = size_text(line_b, image.size[0], 1)
    draw_text(padding, image.size[1] - y - fontsize, line_b, draw, font)

    return image


def application(env, start_response):
    if env['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ["<b>hello world</b>"]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['<h1>Not Found</h1>']

if __name__ == '__main__':
    populate_map()
    name = 'xthey'
    img = meme_image(name, "making a meme?", "all the things!")
    img.save(name + ".jpeg")

    # print 'Serving on 8088...'
    # WSGIServer(('', 8088), application).serve_forever()
    # wsgi.WSGIServer(('', 8088), application, spawn=None).serve_forever()
