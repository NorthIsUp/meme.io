from collections import namedtuple


_image = namedtuple('_IMG_CONTENT_TYPES',
'PNG JPEG GIF')

_IMG_CONTENT_TYPES = _image(
        ('Content-Type', 'image/png'),
        ('Content-Type', 'image/jpeg'),
        ('Content-Type', 'image/gif'),
    )

_SEP = "@@"
_IMG_EXT = "png"
_IMG_DEXT = ".png"
_IMG_TYPE = "PNG"
_IMG_CONTENT_TYPE = _IMG_CONTENT_TYPES.PNG

_routes = namedtuple('ROUTES',
'root front_page serve_meme_blank serve_meme_thread serve_meme_image')

ROUTES = _routes(
    "/",
    "/memeer",
    "/memeer/<name>",
    "/memeer/<name>{0}<line_a>{0}<line_b>".format(_SEP),
    "/memeer/<name>{0}<line_a>{0}<line_b>.png".format(_SEP),
    )
