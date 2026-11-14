#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
PYTHON=${PYTHON:-.venv/bin/python}
"$PYTHON" -m pip check
for project in app app_b; do
    "$PYTHON" "$project/manage.py" check
    "$PYTHON" "$project/manage.py" makemigrations --check --dry-run
done
"$PYTHON" app/manage.py test iam_portal
"$PYTHON" app_b/manage.py test sso_portal
"$PYTHON" -m unittest discover -s tests
for script in scripts/*.sh ldap/entrypoint.sh postgres/init/*.sh; do
    sh -n "$script"
done
docker compose config --quiet
