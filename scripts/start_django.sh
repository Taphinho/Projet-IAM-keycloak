#!/bin/sh
set -eu
case "${PROJECT_DIR:?}" in app|app_b) ;; *) exit 1 ;; esac
python "$PROJECT_DIR/manage.py" migrate --noinput
exec python "$PROJECT_DIR/manage.py" runserver "127.0.0.1:${DJANGO_PORT:?}" --noreload
