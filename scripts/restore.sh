#!/bin/sh
# Restores only into an empty isolated project, never into the active lab.
set -eu
cd "$(dirname "$0")/.."
snapshot=${1:?Usage: restore.sh backups/TIMESTAMP}
restore_project=${2:?Fournir un nom de projet isole, par exemple iam-restore-test}
case "$restore_project" in
    iam-restore-*) ;;
    *) echo "Le nom doit commencer par iam-restore-." >&2; exit 1 ;;
esac
case "$restore_project" in *[!a-z0-9_-]*) exit 1 ;; esac
(cd "$snapshot" && sha256sum -c SHA256SUMS)
for volume in postgres_data ldap_data ldap_config; do
    if docker volume inspect "${restore_project}_$volume" >/dev/null 2>&1; then
        echo "Volume cible déjà présent : abandon sans écrasement." >&2
        exit 1
    fi
done
for volume in postgres_data ldap_data ldap_config; do
    docker volume create "${restore_project}_$volume" >/dev/null
    docker run --rm --network none \
        -v "${restore_project}_$volume:/target" \
        -v "$(realpath "$snapshot"):/backup:ro" debian:trixie-20261104-slim \
        tar -C /target -xzf "/backup/$volume.tar.gz"
done
echo "Volumes restaurés dans $restore_project. Aucun service lancé."
echo "Voir docs/08-exploitation.md pour vérifier dans un environnement isolé."
