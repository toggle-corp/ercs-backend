#! /bin/bash -e

gunicorn main.asgi:application \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:80 \
    --workers 2 \
    --timeout 120
