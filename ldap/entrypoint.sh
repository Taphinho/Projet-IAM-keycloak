#!/bin/sh
set -eu
umask 077

config_dir=/etc/ldap/slapd.d
data_dir=/var/lib/ldap
work_dir=/run/slapd

mkdir -p "$config_dir" "$data_dir" "$work_dir"

if [ ! -f "$data_dir/.lab-ready" ]; then
    if [ -f "$data_dir/data.mdb" ] || [ -f "$config_dir/cn=config.ldif" ]; then
        echo "Initialisation incomplète détectée. Intervention nécessaire." >&2
        exit 1
    fi

    : "${LDAP_ADMIN_PASSWORD:?Secret administrateur LDAP absent}"
    : "${LDAP_BIND_PASSWORD:?Secret du compte technique absent}"
    : "${LDAP_BOB_PASSWORD:?Secret de Bob absent}"

    hash_password() {
        printf '%s' "$1" > "$work_dir/password"
        slappasswd -T "$work_dir/password"
        rm -f "$work_dir/password"
    }

    admin_hash=$(hash_password "$LDAP_ADMIN_PASSWORD")
    bind_hash=$(hash_password "$LDAP_BIND_PASSWORD")
    bob_hash=$(hash_password "$LDAP_BOB_PASSWORD")

    sed "s|__LDAP_ADMIN_HASH__|$admin_hash|" \
        /opt/ldap/slapd.conf.template > "$work_dir/bootstrap.conf"

    sed \
        -e "s|__LDAP_BIND_HASH__|$bind_hash|" \
        -e "s|__LDAP_BOB_HASH__|$bob_hash|" \
        /opt/ldap/bootstrap.ldif.template > "$work_dir/bootstrap.ldif"

    slapadd -f "$work_dir/bootstrap.conf" \
        -l "$work_dir/bootstrap.ldif"

    slaptest -f "$work_dir/bootstrap.conf" -F "$config_dir"

    touch "$data_dir/.lab-ready"
    rm -f "$work_dir/bootstrap.conf" "$work_dir/bootstrap.ldif"
fi

# TLS is applied offline on every start, including existing initialized volumes.
for file in /tls/ca.crt /tls/server.crt /tls/server.key; do
    test -s "$file" || { echo "Certificat TLS manquant : $file" >&2; exit 1; }
done
# The bind mount remains root-only; slapd reads a protected runtime copy.
cp /tls/server.key "$work_dir/server.key"
cp /tls/server.crt "$work_dir/server.crt"
cp /tls/ca.crt "$work_dir/ca.crt"
cat > "$work_dir/tls.ldif" <<'LDIF'
dn: cn=config
changetype: modify
replace: olcTLSCACertificateFile
olcTLSCACertificateFile: /run/slapd/ca.crt
-
replace: olcTLSCertificateFile
olcTLSCertificateFile: /run/slapd/server.crt
-
replace: olcTLSCertificateKeyFile
olcTLSCertificateKeyFile: /run/slapd/server.key
-
replace: olcSecurity
olcSecurity: simple_bind=128
LDIF
slapmodify -F "$config_dir" -n 0 -l "$work_dir/tls.ldif"
rm -f "$work_dir/tls.ldif"

chown -R openldap:openldap "$config_dir" "$data_dir" "$work_dir"

unset LDAP_ADMIN_PASSWORD LDAP_BIND_PASSWORD LDAP_BOB_PASSWORD

exec slapd -F "$config_dir" \
    -h "ldaps://0.0.0.0:636/" \
    -u openldap -g openldap -d 256
