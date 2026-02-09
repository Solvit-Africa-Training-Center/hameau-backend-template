#!/bin/bash


celery -A config worker --loglevel=info --concurrency=1 &

exec gunicorn --bind 0.0.0.0:${PORT:-8000} \
    --workers=1 \
    --threads=2 \
    --timeout=300 \
    --access-logfile - \
    --error-logfile - \
    config.wsgi:application