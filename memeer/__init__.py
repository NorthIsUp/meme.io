from memeer import app as application


def configure_raven(app):
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
sentry = configure_raven(application)
