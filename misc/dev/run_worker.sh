#!/bin/bash -e

./manage.py wait_for_resources --db --redis

./manage.py run_celery_dev
