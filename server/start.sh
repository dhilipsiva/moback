#!/bin/bash
. /home/moback/ENV/bin/activate && \
    cd  /home/moback/CODE/server/ && \
    gunicorn -w 4 -b 127.0.0.1:8000 moback:app \
    --access-logfile /data/moback.log \
    --error-logfile /data/moback.log
