from authlib.integrations.django_client import OAuth
from django.conf import settings


oauth = OAuth()

oauth.register(
    name="keycloak",
    client_id=settings.OIDC_CLIENT_ID,
    client_secret=settings.OIDC_CLIENT_SECRET,
    server_metadata_url=settings.OIDC_DISCOVERY_URL,
    client_kwargs={
        "scope": "openid profile",
        "timeout": 10,
        "code_challenge_method": "S256",
        "token_endpoint_auth_method": "client_secret_basic",
    },
)
