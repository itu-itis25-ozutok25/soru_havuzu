#!/bin/sh
set -eu

python manage.py migrate --noinput

if [ "${DJANGO_COLLECTSTATIC:-false}" = "true" ]; then
    python manage.py collectstatic --noinput
fi

if [ "$#" -eq 0 ]; then
    set -- python manage.py runserver 0.0.0.0:8000
fi

exec "$@"
