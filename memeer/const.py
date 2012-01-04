from collections import namedtuple

_image = namedtuple('IMG_CONTENT_TYPES',
'PNG JPG JPEG GIF')

IMG_CONTENT_TYPES = _image(
        ('Content-Type', 'image/png'),
        ('Content-Type', 'image/jpeg'),
        ('Content-Type', 'image/jpeg'),
        ('Content-Type', 'image/gif'),
    )

