#!/bin/bash
. bin/activate
bin/pip-2.7 -E . install --upgrade gevent
bin/pip-2.7 -E . install --upgrade gunicorn

/bin/gunicorn -b 0.0.0.0:$PORT -w 3 memeer
