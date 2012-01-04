## gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent.queue import Queue

## make wsgi easier
from flask import Flask
from flask import redirect
from flask import make_response
from flask import render_template

# from helpers import view, render_html

## application
from converters import RegexConverter
from lib import libmeme
from template import THREAD
from const import IMG_CONTENT_TYPES
# from helpers import view, render_html

## utils
from urllib import quote
from paver.path import path
from shove import Shove
from logging import getLogger

## TODO: Refactor this into config
__file_path = path(__file__).dirname().abspath()
meme_path = __file_path + "/memes"
font_path = __file_path + "/_static/Impact.ttf"
libmeme.populate_map(meme_path)
libmeme.IMPACT.set_ttf_path(font_path)
IMG_DEXT = ".png"

LOG = getLogger(__name__)
Q = Queue()
store_name = Shove("file://%s/db.names" % path(__file__).dirname().abspath())

app = Flask(__name__)
app.url_map.converters['re'] = RegexConverter


def build_image_response(f, length, img_type):
    resp = make_response(f.read(), 200)
    resp.headers['Content-Length'] = length

    img_type = img_type.upper()

    if hasattr(IMG_CONTENT_TYPES, img_type):
        ct = getattr(IMG_CONTENT_TYPES, img_type)
        resp.headers[ct[0]] = ct[1]
    return resp


@app.route("/memeer/")
def front_page():
    d = {'meme_map': libmeme.MEME_MAP}
    return render_template("memeer.html", **d)


@app.route("/memeer/<name>.<re(r'(?i)(png|jp[e]?g|gif)'):ext>")
def serve_meme_blank(name, ext):
    better_name = libmeme.fuzzy_meme(name)

    # should you redirect?
    if better_name != name:
        new_url = "/memeer/{n}".format(n=better_name)
        LOG.info("redirecting to: ", new_url)
        return redirect(new_url)

    meme_img = libmeme.meme_image(better_name, "", "")
    f, length = libmeme.bufferize_image(meme_img, ext)
    resp = build_image_response(f, length, ext)

    return resp


@app.route("/memeer/<name>/<line_a>/<line_b>.<re(r'(?i)(png|jp[e]?g|gif)'):ext>")
def serve_meme_image(name, line_a, line_b, ext):
    better_name = libmeme.fuzzy_meme(name)

    # should you redirect?
    if better_name != name:
        line_a_format = quote(line_a)
        line_b_format = quote(line_b)
        new_url = "/memeer/{n}/{a}/{b}.{e}".format(n=better_name, a=line_a_format, b=line_b_format, e=ext)
        LOG.info("redirecting to: ", new_url)
        return redirect(new_url)

    libmeme.meme_image(better_name, line_a, line_b)

    meme_img = libmeme.meme_image(better_name, line_a, line_b)
    f, length = libmeme.bufferize_image(meme_img, ext)
    resp = build_image_response(f, length, ext)

    return resp


@app.route("/memeer/<name>/<line_a>/<line_b>/")
def serve_meme_thread(name, line_a, line_b):
    better_name = libmeme.fuzzy_meme(name)

    line_a_format = quote(line_a)
    line_b_format = quote(line_b)

    final_name = better_name if better_name != name else name

    meme_base = "/memeer/{n}/{a}/{b}".format(n=final_name, a=line_a_format, b=line_b_format)

    if better_name != name:
        LOG.info("redirecting to: ", meme_base)
        return redirect(meme_base)

    meme_link = meme_base + IMG_DEXT

    ret = (THREAD.format(meme_link=meme_link, meme_name=final_name, line_a=line_a, line_b=line_b))
    return ret

if __name__ == '__main__':
    import greplin.scales.flaskhandler as statserver
    statserver.serveInBackground(8765, serverName='memeer-stats')

    app.debug = True
    app.run(host="127.0.0.1")
else:
    # gunicorn
    application = app
