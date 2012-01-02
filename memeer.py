import gevent.monkey
from gevent import Greenlet
gevent.monkey.patch_all()

## application
import libmeme
from template import THREAD
from  content_types_mixin import IMAGE
import memeer_routes

## make wsgi easier
from gserver.routes import Routes
from gserver.wsgi import get_handler
from gserver.content_types import TEXT
from gevent.queue import Queue

## utils
from urllib import quote
from paver.path import path
import cStringIO

## data
from shove import Shove

from logging import getLogger
LOG = getLogger(__name__)


store_name = Shove("file://%s/db.names" % path(__file__).dirname().abspath())


routes = Routes()
route = routes.route
route_json = routes.route_json

meme_queue = Queue()


_SEP = "@@"
_IMG_EXT = "jpg"
_IMG_TYPE = "JPEG"


## worker in a grenlet
def process_meme_queue(q=meme_queue):
    while True:
        name, line_a, line_b = q.get(block=True)
        if name not in store_name:
            store_name[name] = {}
        store_name[name][(line_a, line_b)] = None


@route("^/memeer[/]?$")
def front_page(req):
    ret = []
    #TODO adam: store this in a data structure that can be printed via simple traversal
    for meme_name, history in store_name.iteritems():
        ret.append("<li>" + meme_name + "</li><ul>")
        for line_a, line_b in history:
            line_a_format = quote(line_a)
            line_b_format = quote(line_b)
            url = "/memeer/disqus/{1}{0}{2}{0}{3}/".format(_SEP, meme_name, line_a_format, line_b_format)
            ret.append("<li><a href='{url}'>{line_a} \\\\ {line_b}</a></li>".format(url=url, line_a=line_a, line_b=line_b))
        ret.append("</ul>")
    return ret


@route(memeer_routes.serve_meme_thread, content_type=TEXT.HTML)
def serve_meme_thread(req, name, line_a, line_b):
    _meme_img, better_name = libmeme.meme_image(name, line_a, line_b)

    line_a_format = quote(line_a)
    line_b_format = quote(line_b)

    final_name = better_name if better_name != name else name

    meme_base = "/{n}{S}{a}{S}{b}".format(S=_SEP, n=final_name, a=line_a_format, b=line_b_format)
    meme_link = "/memeer" + meme_base + _IMG_EXT
    disqus_link = "/memeer/disqus" + meme_base

    if better_name != name:
        LOG.info("redirecting to: ", disqus_link)
        req.redirect(disqus_link)

    ret = (THREAD.format(meme_link=meme_link, meme_name=final_name, line_a=line_a, line_b=line_b))
    return ret


@route(memeer_routes.serve_meme_image, content_type=IMAGE.JPEG)
def serve_meme_image(req, name, line_a, line_b, ext=None):
    print name, line_a, line_b, ext

    if line_b.endswith(".jpg"):
        line_b = line_b[:-4]
    elif line_b.endswith(".jpeg"):
        line_b = line_b[:-5]
    else:
        req.redirect(req.env['REQUEST_URI'] + _IMG_EXT)

    meme_img, better_name = libmeme.meme_image(name, line_a, line_b)

    if better_name != name:
        line_a_format = quote(line_a)
        line_b_format = quote(line_b)
        new_url = "/memeer/{n}{S}{a}{S}{b}.{E}".format(S=_SEP, E=_IMG_EXT, n=better_name, a=line_a_format, b=line_b_format)
        LOG.info("redirecting to: ", new_url)
        req.redirect(new_url)

    meme_queue.put((better_name, line_a, line_b))

    f = cStringIO.StringIO()
    meme_img.save(f, "JPEG")
    f.seek(0)

    #output to browser
    return [f.read()]


# @route("^/memeer/(?P<name>[\w\s_\-]+)[/]?", content_type=IMAGE.JPEG)
def serve_blank_meme_image(req, name):
    meme_img, better_name = libmeme.meme_image(name, "", "", blank=True)

    if better_name != name:
        new_url = "/memeer/{n}.{E}".format(n=better_name, E=_IMG_EXT)
        LOG.info("redirecting to: ", new_url)
        req.redirect(new_url)

    f = cStringIO.StringIO()
    meme_img.save(f, _IMG_TYPE)
    f.seek(0)

    #output to browser
    return [f.read()]


## Setup
sogq = Greenlet.spawn(process_meme_queue)

meme_path = path("memes").abspath()
libmeme.populate_map(meme_path)


if __name__ == '__main__':
    from gserver.wsgi import WSGIServer
    port = 8088
    LOG.info('Serving on %d...' % port)
    server = WSGIServer(('', port), routes)
    server.serve_forever()
else:
    application = get_handler(routes)
