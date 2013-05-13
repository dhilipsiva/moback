#!/bin/bash
. /home/moback/ENV/bin/activate && \
    cd  /home/moback/CODE/server/ && \
    uwsgi -H /home/moback/ENV/ -s /tmp/moback.sock -w moback:app --pidfile /tmp/moback.pid
