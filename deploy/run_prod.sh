#!/bin/bash -e

./manage.py wait_for_resources --db
./manage.py migrate
./manage.py collectstatic --noinput

gunicorn main.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind=0.0.0.0:80 \
    --timeout=40 \
    --workers=2
