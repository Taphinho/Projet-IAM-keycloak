from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import OIDCIdentity


@transaction.atomic
def get_or_create_oidc_user(issuer, subject):
    identity = (
        OIDCIdentity.objects
        .select_related("user")
        .filter(issuer=issuer, subject=subject)
        .first()
    )

    if identity is not None:
        return identity.user

    User = get_user_model()

    user = User.objects.create_user(
        username=f"oidc_{uuid4().hex}",
        password=None,
        is_staff=False,
        is_superuser=False,
    )

    OIDCIdentity.objects.create(
        user=user,
        issuer=issuer,
        subject=subject,
    )

    return user
