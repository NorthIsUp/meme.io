import gevent.monkey
gevent.monkey.patch_all()

## application
import libmeme
from template import THREAD
from  content_types_mixin import IMAGE

## make wsgi easier
from gserver.routes import Routes
from gserver.wsgi import get_handler
from gserver.content_types import TEXT

## utils
from urllib import quote
from paver.path import path
import cStringIO

from logging import getLogger

LOG = getLogger(__name__)

routes = Routes()
route = routes.route
route_json = routes.route_json

meme_path = path("memes").abspath()
libmeme.populate_map(meme_path)


@route("^/memeer/disqus/(?P<name>[\w\s_\-]+)/(?P<line_a>[\w\s_\-]+)/(?P<line_b>[\w\s_\-]+)[/]?$", content_type=TEXT.HTML)
def serve_meme_thread(req, name, line_a, line_b):
    _meme_img, better_name = libmeme.meme_image(name, line_a, line_b)

    line_a_format = quote(line_a)
    line_b_format = quote(line_b)

    final_name = better_name if better_name != name else name

    meme_base = "/{0}/{1}/{2}/".format(final_name, line_a_format, line_b_format)
    meme_link = "/memeer" + meme_base
    disqus_link = "/memeer/disqus" + meme_base

    if better_name != name:
        LOG.info("redirecting to: ", disqus_link)
        req.redirect(disqus_link)

    ret = (THREAD.format(meme_link=meme_link, meme_name=final_name, line_a=line_a, line_b=line_b))
    return ret


@route("^/memeer/(?P<name>[\w\s_\-]+)/(?P<line_a>[\w\s_\-]+)/(?P<line_b>[\w\s_\-]+)[/]?$", content_type=IMAGE.JPEG)
def serve_meme(req, name, line_a, line_b):
    meme_img, better_name = libmeme.meme_image(name, line_a, line_b)

    if better_name != name:
        line_a_format = quote(line_a)
        line_b_format = quote(line_b)
        new_url = "/memeer/{0}/{1}/{2}/".format(better_name, line_a_format, line_b_format)
        LOG.info("redirecting to: ", new_url)
        req.redirect(new_url)

    f = cStringIO.StringIO()
    meme_img.save(f, "JPEG")
    f.seek(0)

    #output to browser
    return [f.read()]


if __name__ == '__main__':
    from gserver.wsgi import WSGIServer

    port = 8088
    LOG.info('Serving on %d...' % port)
    server = WSGIServer(('', port), routes)
    server.serve_forever()
else:
    application = get_handler(routes)
