import logging
import os
import signal
import sys
import gevent.monkey
from paver.path import path

gevent.monkey.patch_all()
import multiprocessing

bind = "unix:/tmp/gunicorn.sock"
workers = multiprocessing.cpu_count() * 2 + 1

debug = True
spew = False

p = path(__file__).dirname().abspath()

loglevel = 'debug'

logfile = p + '/log/log'
errorlog = p + '/log/err'
accesslog = p + '/log/access'


## for dynamic reloading
def on_starting(server):
    # use server hook to patch socket to allow worker reloading
    from gevent import monkey
    monkey.patch_socket()


## for dynamic reloading
def when_ready(server):
    def monitor():
        modify_times = {}
        while True:
            logging.info("=" * 80)
            for module in sys.modules.values():
                path = getattr(module, "__file__", None)
                if not path:
                    continue
                if path.endswith(".pyc") or path.endswith(".pyo"):
                    path = path[:-1]
                try:
                    modified = os.stat(path).st_mtime
                except:
                    continue
                if path not in modify_times:
                    modify_times[path] = modified
                    continue
                if modify_times[path] != modified:
                    logging.info("%s modified; restarting server", path)
                    os.kill(os.getpid(), signal.SIGHUP)
                    modify_times = {}
                    break
            gevent.sleep(1)

    import gevent
    gevent.spawn(monitor)
