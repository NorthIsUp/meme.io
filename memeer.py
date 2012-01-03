# import gevent.monkey
# gevent.monkey.patch_all()

## application
import libmeme
from template import THREAD
from  content_types_mixin import IMAGE
import memeer_routes

## make wsgi easier
from flask import Flask
from flask import redirect
from flask import make_response

# from flask import request
# from flask import abort
# from flask import url_for


## utils
from urllib import quote
from paver.path import path

try:
    from cStringIO import StringIO
except:
    pass
    #from StringIO import StringIO

## data
from shove import Shove

from logging import getLogger

app = Flask(__name__)
LOG = getLogger(__name__)

store_name = Shove("file://%s/db.names" % path(__file__).dirname().abspath())

_SEP = "@@"
_IMG_EXT = "png"
_IMG_DEXT = ".png"
_IMG_TYPE = "PNG"
_IMG_CONTENT_TYPE = IMAGE.PNG


@app.route("/memeer")
def front_page():
    ret = []
    #TODO adam: store this in a data structure that can be printed via simple traversal
    for meme_name, history in store_name.iteritems():
        ret.append("<li>" + meme_name + "</li><ul>")
        for line_a, line_b in history:
            line_a_format = quote(line_a)
            line_b_format = quote(line_b)
            url = "/memeer/disqus/{1}{0}{2}{0}{3}".format(_SEP, meme_name, line_a_format, line_b_format)
            ret.append("<li><a href='{url}'>{line_a} \\\\ {line_b}</a></li>".format(url=url, line_a=line_a, line_b=line_b))
        ret.append("</ul>")
    return "".join(ret)


@app.route(memeer_routes.serve_meme_thread)
def serve_meme_thread(name, line_a, line_b):
    better_name = libmeme.fuzzy_meme(name)

    line_a_format = quote(line_a)
    line_b_format = quote(line_b)

    final_name = better_name if better_name != name else name

    meme_base = "/{n}{S}{a}{S}{b}".format(S=_SEP, n=final_name, a=line_a_format, b=line_b_format)
    meme_link = "/memeer" + meme_base + _IMG_DEXT
    disqus_link = "/memeer/disqus" + meme_base

    if better_name != name:
        LOG.info("redirecting to: ", disqus_link)
        return redirect(disqus_link)

    ret = (THREAD.format(meme_link=meme_link, meme_name=final_name, line_a=line_a, line_b=line_b))
    return ret


@app.route("/memeer/<name>@@<line_a>@@<line_b>.png")
def serve_meme_image(name, line_a, line_b):
    print name, line_a, line_b
    better_name = libmeme.fuzzy_meme(name)

    # should you redirect?
    if better_name != name:
        line_a_format = quote(line_a)
        line_b_format = quote(line_b)
        new_url = "/memeer/{n}{S}{a}{S}{b}.{E}".format(S=_SEP, E=_IMG_EXT, n=better_name, a=line_a_format, b=line_b_format)
        LOG.info("redirecting to: ", new_url)
        return redirect(new_url)

    meme_img = libmeme.meme_image(better_name, line_a, line_b)

    # put the image in a string buffer for output
    f = StringIO()
    meme_img.save(f, _IMG_TYPE)
    length = f.tell()
    f.seek(0)

    # make the response
    resp = make_response(f.read(), 200)
    resp.headers['Content-Length'] = length
    resp.headers['Content-Type'] = _IMG_CONTENT_TYPE
    #output to browser
    return resp


## Setup
meme_path = path("memes").abspath()
libmeme.populate_map(meme_path)


if __name__ == '__main__':
    # flask
    app.debug = True
    app.run(host="127.0.0.1")
else:
    # gunicorn
    application = app
