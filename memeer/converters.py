from werkzeug.routing import BaseConverter


## FIXME: MOVE ME TO HELPERS
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

