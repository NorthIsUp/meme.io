import gevent.monkey
gevent.monkey.patch_all()

## make wsgi easier
from gserver.routes import Routes
from gserver.wsgi import WSGIServer

# utils
from paver.path import path
import cStringIO

# debug
from pprint import pprint
import libmeme

from content_types import IMAGE

routes = Routes()
route = routes.route
route_json = routes.route_json


@route("^/example/$")
def example(req):
        return "hello"


@route("^/memeer/(?P<name>[\w\s]+)/(?P<line_a>[\w\s]+)/(?P<line_b>[\w\s]+)[/]?$", content_type=IMAGE.JPEG)
def serve_meme(req, name, line_a, line_b):
    pprint(req.env)
    pprint(req.query_data)

    meme_img = libmeme.meme_image(name, line_a, line_b)

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
