#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
attempt=0
until docker compose exec -T ldap ldapwhoami -x -H ldaps://ldap:636 >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    test "$attempt" -lt 30 || { echo "LDAP TLS indisponible" >&2; exit 1; }
    sleep 1
done
docker compose exec -T ldap sh < ldap/test-security.sh
