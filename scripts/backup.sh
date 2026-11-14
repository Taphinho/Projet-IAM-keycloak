#!/bin/sh
# Consistent snapshot: stop all writers; keep local Django processes stopped too.
set -eu
cd "$(dirname "$0")/.."
umask 077
destination="backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$destination"
for service in keycloak postgres ldap; do
    state=$(docker compose ps --status running --services "$service")
    test -z "$state" || { echo "Arrêter $service avant sauvegarde." >&2; exit 1; }
done
for volume in postgres_data ldap_data ldap_config; do
    docker volume inspect "enterprise-iam-lab_$volume" >/dev/null
    docker run --rm --network none \
        -v "enterprise-iam-lab_$volume:/source:ro" \
        -v "$(pwd)/$destination:/backup" debian:trixie-20261104-slim \
        tar -C /source -czf "/backup/$volume.tar.gz" .
done
for project in app app_b; do
    if [ -f "$project/db.sqlite3" ]; then
        cp "$project/db.sqlite3" "$destination/$project.sqlite3"
    fi
done
cp .env "$destination/environment.env"
cp -R certs "$destination/certs"
(cd "$destination" && sha256sum ./*.tar.gz > SHA256SUMS)
echo "Sauvegarde sensible : $destination (à chiffrer avant stockage externe)."
