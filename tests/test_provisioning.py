import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'scripts/provision_keycloak.py'
spec = importlib.util.spec_from_file_location('provision', PATH)
provision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision)


class ProvisioningSecurityTests(unittest.TestCase):
    def test_client_uses_exact_redirects_and_pkce(self):
        for client, port in [('django-app', 8001), ('portal-b', 8002)]:
            config = provision.client_config(client, port, 'fake-secret')
            self.assertEqual(config['redirectUris'], [f'http://localhost:{port}/oidc/callback/'])
            self.assertFalse(config['publicClient'])
            self.assertFalse(config['fullScopeAllowed'])
            self.assertFalse(config['directAccessGrantsEnabled'])
            self.assertEqual(config['attributes']['pkce.code.challenge.method'], 'S256')

    def test_ldap_requires_tls_and_read_only(self):
        config = provision.ldap_config('realm-id', 'fake-secret')['config']
        self.assertEqual(config['connectionUrl'], ['ldaps://ldap:636'])
        self.assertEqual(config['editMode'], ['READ_ONLY'])
        self.assertEqual(config['useTruststoreSpi'], ['always'])
        self.assertEqual(config['syncRegistrations'], ['false'])
        self.assertNotIn('cn=admin', config['bindDn'][0])
