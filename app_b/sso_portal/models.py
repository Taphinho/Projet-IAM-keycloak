from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class OIDCIdentity(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="oidc_identity",
    )
    issuer = models.URLField(max_length=255)
    subject = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["issuer", "subject"],
                name="unique_oidc_identity",
            ),
        ]
