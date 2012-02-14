from memeer import app as application


def configure_heroku(app):
    import os
    import traceback
    if 'SENTRY_DSN' in os.environ:
        try:
            import raven
            from raven.contrib.flask import Sentry
            raven.load(os.environ['SENTRY_DSN'], app.config)
            sentry = Sentry(app)
            return sentry
        except Exception, e:
            print "Unexpected error:", e
            traceback.print_exc()

        if 'MEMCACHE_SERVERS' in os.environ:
            mc = dict(
            servers=[os.environ.get('MEMCACHE_SERVERS')],
            username=os.environ.get('MEMCACHE_USERNAME'),
            password=os.environ.get('MEMCACHE_PASSWORD'),
            binary=True)

sentry = configure_heroku(application)
