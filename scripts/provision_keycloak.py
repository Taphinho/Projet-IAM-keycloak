"""Provision the reserved local lab realm; no tokens or passwords are printed."""
import argparse
import getpass
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import requests

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
BASE = "http://localhost:8080"
REALM = "enterprise-lab"


def client_config(client_id, port, secret):
    return {
        "clientId": client_id, "enabled": True, "protocol": "openid-connect",
        "publicClient": False, "secret": secret,
        "standardFlowEnabled": True, "implicitFlowEnabled": False,
        "directAccessGrantsEnabled": False, "serviceAccountsEnabled": False,
        "rootUrl": f"http://localhost:{port}",
        "baseUrl": f"http://localhost:{port}/",
        "redirectUris": [f"http://localhost:{port}/oidc/callback/"],
        "webOrigins": [], "fullScopeAllowed": False,
        "attributes": {
            "pkce.code.challenge.method": "S256",
            "post.logout.redirect.uris": f"http://localhost:{port}/logged-out/",
        },
    }


def ldap_config(parent_id, password):
    return {
        "name": "enterprise-openldap", "parentId": parent_id,
        "providerId": "ldap",
        "providerType": "org.keycloak.storage.UserStorageProvider",
        "config": {
            "enabled": ["true"], "priority": ["0"], "vendor": ["other"],
            "connectionUrl": ["ldaps://ldap:636"], "startTls": ["false"],
            "useTruststoreSpi": ["always"], "authType": ["simple"],
            "bindDn": ["cn=keycloak,ou=services,dc=enterprise,dc=test"],
            "bindCredential": [password],
            "usersDn": ["ou=people,dc=enterprise,dc=test"],
            "usernameLDAPAttribute": ["uid"], "rdnLDAPAttribute": ["uid"],
            "uuidLDAPAttribute": ["entryUUID"],
            "userObjectClasses": ["inetOrgPerson"],
            "editMode": ["READ_ONLY"], "importEnabled": ["true"],
            "syncRegistrations": ["false"], "searchScope": ["2"],
            "connectionPooling": ["true"], "connectionTimeout": ["5000"],
            "readTimeout": ["10000"], "cachePolicy": ["NO_CACHE"],
            "pagination": ["true"], "batchSizeForSync": ["100"],
            "fullSyncPeriod": ["-1"], "changedSyncPeriod": ["-1"],
        },
    }


class Admin:
    def __init__(self, username, password):
        response = requests.post(
            f"{BASE}/realms/master/protocol/openid-connect/token",
            data={"client_id": "admin-cli", "grant_type": "password",
                  "username": username, "password": password}, timeout=15,
        )
        response.raise_for_status()
        self.http = requests.Session()
        self.http.headers["Authorization"] = "Bearer " + response.json()["access_token"]

    def call(self, method, path, body=None):
        response = self.http.request(method, f"{BASE}/admin/realms{path}",
                                     json=body, timeout=30)
        response.raise_for_status()
        return response.json() if response.content else None

    def user(self, realm, username, password, actions=()):
        users = self.call("GET", f"/{realm}/users?username={username}&exact=true")
        if users:
            return users[0]["id"]
        self.call("POST", f"/{realm}/users", {
            "username": username, "enabled": True,
            "firstName": username.title(), "lastName": "Demo",
            "requiredActions": list(actions),
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        })
        return self.call("GET", f"/{realm}/users?username={username}&exact=true")[0]["id"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admin", default="lab-admin")
    parser.add_argument("--retire-bootstrap", action="store_true")
    args = parser.parse_args()
    password = getpass.getpass(f"Mot de passe de {args.admin} : ")
    api = Admin(args.admin, password)
    realms = api.call("GET", "")
    if REALM not in {r["realm"] for r in realms}:
        api.call("POST", "", {"realm": REALM, "enabled": True})
    api.call("PUT", f"/{REALM}", {
        "bruteForceProtected": True, "failureFactor": 5,
        "permanentLockout": False, "waitIncrementSeconds": 60,
        "maxFailureWaitSeconds": 900, "ssoSessionIdleTimeout": 900,
        "ssoSessionMaxLifespan": 28800,
        "passwordPolicy": "length(14)",
        "otpPolicyType": "totp", "otpPolicyDigits": 6,
        "otpPolicyPeriod": 30, "otpPolicyLookAheadWindow": 1,
    })
    for client_id, port, secret_key in (
        ("django-app", 8001, "OIDC_CLIENT_SECRET"),
        ("portal-b", 8002, "OIDC_B_CLIENT_SECRET"),
    ):
        config = client_config(client_id, port, os.environ[secret_key])
        clients = api.call("GET", f"/{REALM}/clients?clientId={client_id}")
        if clients:
            cid = clients[0]["id"]
            api.call("PUT", f"/{REALM}/clients/{cid}", config)
        else:
            api.call("POST", f"/{REALM}/clients", config)
            cid = api.call("GET", f"/{REALM}/clients?clientId={client_id}")[0]["id"]
        if client_id != "django-app":
            continue
        roles = api.call("GET", f"/{REALM}/clients/{cid}/roles")
        for role in ("reader", "manager"):
            if role not in {r["name"] for r in roles}:
                api.call("POST", f"/{REALM}/clients/{cid}/roles", {"name": role})
        roles = api.call("GET", f"/{REALM}/clients/{cid}/roles")
        api.call("POST", f"/{REALM}/clients/{cid}/scope-mappings/clients/{cid}", roles)
        mapper = {
            "name": "django-app-roles", "protocol": "openid-connect",
            "protocolMapper": "oidc-usermodel-client-role-mapper",
            "config": {"usermodel.clientRoleMapping.clientId": "django-app",
                       "claim.name": "app_roles", "jsonType.label": "String",
                       "multivalued": "true", "id.token.claim": "true",
                       "access.token.claim": "false", "userinfo.token.claim": "false"},
        }
        mappers = api.call("GET", f"/{REALM}/clients/{cid}/protocol-mappers/models")
        existing = next((m for m in mappers if m["name"] == mapper["name"]), None)
        if existing:
            mapper["id"] = existing["id"]
            api.call("PUT", f"/{REALM}/clients/{cid}/protocol-mappers/models/{existing['id']}", mapper)
        else:
            api.call("POST", f"/{REALM}/clients/{cid}/protocol-mappers/models", mapper)
        uid = api.user(REALM, "alice", os.environ["ALICE_PASSWORD"], ("CONFIGURE_TOTP",))
        reader = [r for r in roles if r["name"] == "reader"]
        api.call("POST", f"/{REALM}/users/{uid}/role-mappings/clients/{cid}", reader)
    realm_id = api.call("GET", f"/{REALM}")["id"]
    component = ldap_config(realm_id, os.environ["LDAP_BIND_PASSWORD"])
    components = api.call("GET", f"/{REALM}/components?name=enterprise-openldap")
    if components:
        component["id"] = components[0]["id"]
        api.call("PUT", f"/{REALM}/components/{component['id']}", component)
    else:
        api.call("POST", f"/{REALM}/components", component)
    admin_id = api.user("master", "iam-admin", os.environ["KC_PERMANENT_ADMIN_PASSWORD"])
    role = api.call("GET", "/master/roles/admin")
    api.call("POST", f"/master/users/{admin_id}/role-mappings/realm", [role])
    # Authenticate the replacement before allowing removal of the bootstrap account.
    Admin("iam-admin", os.environ["KC_PERMANENT_ADMIN_PASSWORD"])
    if args.retire_bootstrap:
        replacement = Admin("iam-admin", os.environ["KC_PERMANENT_ADMIN_PASSWORD"])
        users = replacement.call("GET", "/master/users?username=lab-admin&exact=true")
        if users:
            replacement.call("DELETE", f"/master/users/{users[0]['id']}")
    print("Configuration appliquée. Exécuter les tests navigateur et LDAPS documentés.")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, KeyError) as exc:
        print(f"Provisionnement interrompu ({type(exc).__name__}), aucun secret affiché.", file=sys.stderr)
        raise SystemExit(1)
