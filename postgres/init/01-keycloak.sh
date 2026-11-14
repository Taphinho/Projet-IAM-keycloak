#!/bin/sh
set -eu

psql \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 \
  --set=app_password="$KC_DB_PASSWORD" <<'SQL'
CREATE ROLE keycloak
  LOGIN
  NOSUPERUSER
  NOCREATEDB
  NOCREATEROLE
  PASSWORD :'app_password';

CREATE DATABASE keycloak OWNER keycloak;
SQL
