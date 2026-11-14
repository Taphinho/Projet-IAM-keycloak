set -eu
umask 077
pw=/run/slapd/smoke-password
trap 'rm -f "$pw" /run/slapd/smoke.ldif' EXIT
bob='uid=bob,ou=people,dc=enterprise,dc=test'
bind='cn=keycloak,ou=services,dc=enterprise,dc=test'
printf '%s' "$LDAP_BOB_PASSWORD" > "$pw"
ldapwhoami -x -H ldaps://ldap:636 -D "$bob" -y "$pw"
echo 'PASS: Bob + LDAPS + CA vérifiée'
set +e
ldapwhoami -x -H ldaps://ldap:636 -D "$bob" -w deliberately-invalid >/dev/null 2>&1
status=$?
set -e
[ "$status" -eq 49 ]
echo 'PASS: mauvais mot de passe refusé (49)'
printf '%s' "$LDAP_BIND_PASSWORD" > "$pw"
result=$(ldapsearch -x -LLL -H ldaps://ldap:636 -D "$bind" -y "$pw" -b "$bob" -s base '(objectClass=*)' uid userPassword)
printf '%s' "$result" | grep -q 'uid: bob'
if printf '%s' "$result" | grep -q '^userPassword'; then echo 'FAIL: attribut secret lisible'; exit 1; fi
echo 'PASS: lecture autorisée, userPassword masqué'
cat > /run/slapd/smoke.ldif <<'LDIF'
dn: uid=bob,ou=people,dc=enterprise,dc=test
changetype: modify
replace: description
description: Must be denied
LDIF
set +e
ldapmodify -x -H ldaps://ldap:636 -D "$bind" -y "$pw" -f /run/slapd/smoke.ldif >/dev/null 2>&1
status=$?
set -e
[ "$status" -eq 50 ]
echo 'PASS: écriture refusée (50)'
if LDAPTLS_CACERT=/dev/null LDAPTLS_REQCERT=demand ldapwhoami -x -H ldaps://ldap:636 -D "$bind" -y "$pw" >/dev/null 2>&1; then
 echo 'FAIL: CA inconnue acceptée'; exit 1
fi
echo 'PASS: CA inconnue refusée'
if ldapwhoami -x -H ldap://ldap:389 >/dev/null 2>&1; then
 echo 'FAIL: port clair ouvert'; exit 1
fi
echo 'PASS: LDAP clair indisponible'
