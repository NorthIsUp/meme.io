import logging
import os
import signal
import sys
import gevent.monkey
gevent.monkey.patch_all()
import multiprocessing

bind = "0.0.0.0:5000"
workers = 1  # multiprocessing.cpu_count() * 2 + 1

debug = True
spew = False

loglevel = 'debug'
errorfile = '-'
logfile = '-'
accesslog = '-'


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("Forked child, re-executing.")


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
                    print("=" * 80)
                    print path
                    logging.info("%s modified; restarting server", path)
                    os.kill(os.getpid(), signal.SIGHUP)
                    modify_times = {}
                    break
            gevent.sleep(1)

    import gevent
    gevent.spawn(monitor)
