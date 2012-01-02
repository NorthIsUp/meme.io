import gevent.monkey
gevent.monkey.patch_all()

from urllib import quote

## make wsgi easier
from gserver.routes import Routes
from gserver.wsgi import WSGIServer

# utils
from paver.path import path
import cStringIO

# debug
import libmeme

from content_types import IMAGE

routes = Routes()
route = routes.route
route_json = routes.route_json


@route("^/example/$")
def example(req):
        return "hello"


@route("^/memeer/(?P<name>[\w\s_\-]+)/(?P<line_a>[\w\s_\-]+)/(?P<line_b>[\w\s_\-]+)[/]?$", content_type=IMAGE.JPEG)
def serve_meme(req, name, line_a, line_b):
    meme_img, better_name = libmeme.meme_image(name, line_a, line_b)

    if better_name != name:
        line_a_format = quote(line_a)
        line_b_format = quote(line_b)
        new_url = "/memeer/{0}/{1}/{2}/".format(better_name, line_a_format, line_b_format)
        req.redirect(new_url)

    f = cStringIO.StringIO()
    meme_img.save(f, "JPEG")
    f.seek(0)

    #output to browser
    return [f.read()]


if __name__ == '__main__':
    meme_path = path("memes").abspath()
    libmeme.populate_map(meme_path)
    port = 8088
    print 'Serving on %d...' % port
    server = WSGIServer(('', port), routes)
    server.serve_forever()
