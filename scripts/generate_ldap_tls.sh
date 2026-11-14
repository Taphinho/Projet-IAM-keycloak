#!/bin/sh
# Local CA, never committed. Existing material is never overwritten.
set -eu
cd "$(dirname "$0")/.."
umask 077
mkdir -p certs/ldap
if [ -n "$(ls -A certs/ldap)" ]; then
    echo "certs/ldap non vide : conservation des certificats existants." >&2
    exit 1
fi
openssl req -x509 -newkey rsa:3072 -nodes -sha256 -days 365 \
    -keyout certs/ldap/ca.key -out certs/ldap/ca.crt \
    -subj '/CN=Enterprise IAM Lab CA' \
    -addext 'basicConstraints=critical,CA:TRUE' \
    -addext 'keyUsage=critical,keyCertSign,cRLSign'
openssl req -new -newkey rsa:3072 -nodes \
    -keyout certs/ldap/server.key -out certs/ldap/server.csr \
    -subj '/CN=ldap'
cat > certs/ldap/server.ext <<'EOF'
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:ldap,DNS:localhost,IP:127.0.0.1
EOF
openssl x509 -req -sha256 -days 365 -in certs/ldap/server.csr \
    -CA certs/ldap/ca.crt -CAkey certs/ldap/ca.key -CAcreateserial \
    -extfile certs/ldap/server.ext -out certs/ldap/server.crt
# Certificate is public and must be readable by the Keycloak container.
chmod 644 certs/ldap/ca.crt certs/ldap/server.crt
openssl verify -CAfile certs/ldap/ca.crt certs/ldap/server.crt
