from functools import wraps
from werkzeug import BaseResponse
from flask import render_template


def render_html(template, **defaults):
    def wrapped(result):
        variables = defaults.copy()
        variables.update(result)
        return render_template(template, **variables)
    return wrapped


def view(self, url, renderer=None, *args, **kwargs):
    super_route = self.route

    defaults = kwargs.pop('defaults', {})
    route_id = object()
    defaults['_route_id'] = route_id

    def deco(f):
        @super_route(url, defaults=defaults, *args, **kwargs)
        @wraps(f)
        def decorated_function(*args, **kwargs):
            this_route = kwargs.get('_route_id')
            if not getattr(f, 'is_route', False):
                del kwargs['_route_id']

            result = f(*args, **kwargs)

            if this_route is not route_id:
                return result

            # catch redirects.
            if isinstance(result, (app.response_class,
                                   BaseResponse)):
                return result

            if renderer is None:
                return result
            return renderer(result)

        decorated_function.is_route = True
        return decorated_function

    return deco
