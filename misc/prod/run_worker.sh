#!/bin/bash -e

./manage.py wait_for_resources --db --celery-broker

celery -A main worker \
    -l INFO \
    -Q default \
    --concurrency 1 \
    --max-tasks-per-child 4
