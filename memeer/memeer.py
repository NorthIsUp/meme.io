import os
from urllib import quote
from logging import getLogger

## gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent.queue import Queue

## Web
from flask import Flask
from flask import redirect
from flask import make_response
from flask import render_template
from flask import request

from flaskext.cache import Cache
from paver.path import path

## application
from converters import RegexConverter
from lib import libmeme
from template import THREAD
from const import IMG_CONTENT_TYPES

## stats
# from greplin import scales
# from greplin.scales import meter
# from helpers import view, render_html


## TODO: Refactor this into config
__file_path = path(__file__).dirname().abspath()
libmeme.populate_map(__file_path + "/memes")
libmeme.IMPACT.set_ttf_path(__file_path + "/static/Impact.ttf")

SITE_ROOT = ""
IMG_DEXT = "jpeg"

LOG = getLogger(__name__)
Q = Queue()

app = Flask(__name__, static_folder=__file_path + "/static", static_path=SITE_ROOT + "/static")
app.url_map.converters['re'] = RegexConverter

if 'REDIS_TO_GO' in os.environ:
    import urlparse

    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(os.environ['REDIS_TO_GO'])
    app.config.from_envvar('REDIS_TO_GO')
    app.config['CACHE_TYPE'] = "redis"
    app.config['CACHE_REDIS_HOST'] = url.hostname
    app.config['CACHE_REDIS_PORT'] = url.port
    app.config['CACHE_REDIS_PASSWORD'] = url.password
    # from werkzeug.contrib.cache import RedisCache
    # cache = RedisCache(host=url.hostname, port=url.port)
else:
    app.config['CACHE_TYPE'] = "simple"
    # from werkzeug.contrib.cache import SimpleCache
    # cache = SimpleCache()

app.config['CACHE_DEFAULT_TIMEOUT'] = 500
cache = Cache(app)

# STATS = scales.collection('/web',
    # meter.MeterStat('hits'),
    # scales.IntStat('requests'),
    # scales.PmfStat('latency'),
    # scales.IntDictStat('byPath'),
    # )


def build_image_response(f, length, img_type):
    resp = make_response(f.read(), 200)
    resp.headers['Content-Length'] = length

    img_type = img_type.upper()

    if hasattr(IMG_CONTENT_TYPES, img_type):
        ct = getattr(IMG_CONTENT_TYPES, img_type)
        resp.headers[ct[0]] = ct[1]
    return resp


@app.route(SITE_ROOT + "/")
@cache.cached(timeout=600)
def front_page():
    d = {'meme_map': libmeme.MEME_MAP, 'SITE_ROOT': SITE_ROOT}
    return render_template("memeer.html", **d)


@app.route(SITE_ROOT + "/<name>.<re(r'(?i)(png|jp[e]?g|gif)'):ext>")
@cache.cached(timeout=600)
def serve_meme_blank(name, ext):
    # STATS.hits.mark()
    # with STATS.latency.time():
    better_name = libmeme.fuzzy_meme(name)

    # should you redirect?
    if better_name != name or ext != IMG_DEXT:
        new_url = "/memeer/{n}.{e}".format(n=better_name, e=IMG_DEXT)
        LOG.info("redirecting to: ", new_url)
        return redirect(new_url)

    size = request.args.get("size", "")
    better_name_size = better_name + size

    resp = cache.get(better_name_size)

    if resp:
        return resp

    meme_img = libmeme.meme_image(better_name, "", "")
    f, length = libmeme.bufferize_image(meme_img, ext, size)
    resp = build_image_response(f, length, ext)

    cache.set(better_name_size, resp, timeout=5 * 60)
    return resp


@app.route(SITE_ROOT + "/<name>/<line_a>/<line_b>.<re(r'(?i)(png|jp[e]?g|gif)'):ext>")
def serve_meme_image(name, line_a, line_b, ext):
    better_name = libmeme.fuzzy_meme(name)

    # should you redirect?
    if better_name != name or ext != IMG_DEXT:
        line_a_format = quote(line_a)
        line_b_format = quote(line_b)
        new_url = SITE_ROOT + "/{n}/{a}/{b}.{e}".format(n=better_name, a=line_a_format, b=line_b_format, e=IMG_DEXT)
        LOG.info("redirecting to: ", new_url)
        return redirect(new_url)

    libmeme.meme_image(better_name, line_a, line_b)

    meme_img = libmeme.meme_image(better_name, line_a, line_b)
    f, length = libmeme.bufferize_image(meme_img, ext)
    resp = build_image_response(f, length, ext)

    return resp


@app.route(SITE_ROOT + "/<name>/<line_a>/<line_b>/")
def serve_meme_thread(name, line_a, line_b):
    better_name = libmeme.fuzzy_meme(name)

    line_a_format = quote(line_a)
    line_b_format = quote(line_b)

    final_name = better_name if better_name != name else name

    meme_base = SITE_ROOT + "/{n}/{a}/{b}".format(n=final_name, a=line_a_format, b=line_b_format)

    if better_name != name:
        LOG.info("redirecting to: ", meme_base)
        return redirect(meme_base)

    meme_link = meme_base + "." + IMG_DEXT

    ret = (THREAD.format(meme_link=meme_link, meme_name=final_name, line_a=line_a, line_b=line_b))
    return ret
