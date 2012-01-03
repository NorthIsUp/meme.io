## gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent.queue import Queue

## make wsgi easier
from flask import Flask
from flask import redirect
from flask import make_response

## application
import libmeme
from template import THREAD
from const import _SEP, _IMG_DEXT, _IMG_EXT, _IMG_TYPE, _IMG_CONTENT_TYPE, ROUTES

## utils
from urllib import quote
from paver.path import path
from shove import Shove
from logging import getLogger

## Setup
meme_path = path("memes").abspath()
libmeme.populate_map(meme_path)

app = Flask(__name__)
LOG = getLogger(__name__)
Q = Queue()
store_name = Shove("file://%s/db.names" % path(__file__).dirname().abspath())


def build_image_response(f, length):
    resp = make_response(f.read(), 200)
    resp.headers['Content-Length'] = length
    resp.headers[_IMG_CONTENT_TYPE[0]] = _IMG_CONTENT_TYPE[1]
    return resp


@app.route(ROUTES.front_page)
def front_page():
    ret = []
    #TODO adam: store this in a data structure that can be printed via simple traversal
    for meme_name, history in store_name.iteritems():
        ret.append("<li>" + meme_name + "</li><ul>")
        for line_a, line_b in history:
            line_a_format = quote(line_a)
            line_b_format = quote(line_b)
            url = "/memeer/{1}{0}{2}{0}{3}".format(_SEP, meme_name, line_a_format, line_b_format)
            ret.append("<li><a href='{url}'>{line_a} \\\\ {line_b}</a></li>".format(url=url, line_a=line_a, line_b=line_b))
        ret.append("</ul>")
    return "".join(ret)


@app.route(ROUTES.serve_meme_blank)
def serve_meme_blank(name):
    better_name = libmeme.fuzzy_meme(name)

    # should you redirect?
    if better_name != name:
        new_url = "/memeer/{n}".format(n=better_name)
        LOG.info("redirecting to: ", new_url)
        return redirect(new_url)

    meme_img = libmeme.meme_image(better_name, "", "")
    f, length = libmeme.bufferize_image(meme_img, _IMG_TYPE)
    resp = build_image_response(f, length)

    return resp


@app.route(ROUTES.serve_meme_image)
def serve_meme_image(name, line_a, line_b):
    better_name = libmeme.fuzzy_meme(name)

    # should you redirect?
    if better_name != name:
        line_a_format = quote(line_a)
        line_b_format = quote(line_b)
        new_url = "/memeer/{n}{S}{a}{S}{b}.{E}".format(S=_SEP, E=_IMG_EXT, n=better_name, a=line_a_format, b=line_b_format)
        LOG.info("redirecting to: ", new_url)
        return redirect(new_url)

    libmeme.meme_image(better_name, line_a, line_b)

    meme_img = libmeme.meme_image(better_name, line_a, line_b)
    f, length = libmeme.bufferize_image(meme_img, _IMG_TYPE)
    resp = build_image_response(f, length)

    return resp


@app.route(ROUTES.serve_meme_thread)
def serve_meme_thread(name, line_a, line_b):
    better_name = libmeme.fuzzy_meme(name)

    line_a_format = quote(line_a)
    line_b_format = quote(line_b)

    final_name = better_name if better_name != name else name

    meme_base = "/{n}{S}{a}{S}{b}".format(S=_SEP, n=final_name, a=line_a_format, b=line_b_format)

    if better_name != name:
        disqus_link = "/memeer/disqus" + meme_base
        LOG.info("redirecting to: ", disqus_link)
        return redirect(disqus_link)

    meme_link = "/memeer" + meme_base + _IMG_DEXT

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
