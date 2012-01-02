from collections import namedtuple

_image = namedtuple('IMAGE',
'PNG JPEG GIF')

IMAGE = _image(
        ('Content-Type', 'image/png'),
        ('Content-Type', 'image/jpeg'),
        ('Content-Type', 'image/gif'),
    )
