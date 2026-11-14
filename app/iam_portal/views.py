import logging
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from .identity import get_or_create_oidc_user
from .oidc import oauth
from .permissions import roles_required

logger = logging.getLogger(__name__)

@never_cache
def home(request):
    if request.user.is_authenticated:
        return HttpResponse(
            "Laboratoire Enterprise IAM — session Django authentifiée."
        )

    return HttpResponse(
        "Laboratoire Enterprise IAM — visiteur non connecté."
    )

def login(request):
    redirect_uri = "http://localhost:8001/oidc/callback/"
    return oauth.keycloak.authorize_redirect(request, redirect_uri)

@never_cache
def oidc_callback(request):
    try:
        token = oauth.keycloak.authorize_access_token(request)
    except Exception as exc:
        logger.warning(
            "Erreur OIDC : %s.%s",
            type(exc).__module__,
            type(exc).__name__,
        )
        return HttpResponse("Authentification refusée.", status=400)

    claims = token.get("userinfo") or {}
    issuer = claims.get("iss")
    subject = claims.get("sub")

    if (
        issuer != settings.OIDC_ISSUER
        or not isinstance(subject, str)
        or not subject
    ):
        return HttpResponse("Identité OIDC refusée.", status=400)

    try:
        user = get_or_create_oidc_user(issuer, subject)
    except DatabaseError:
        return HttpResponse(
            "Connexion temporairement indisponible.",
            status=503,
        )

    if not user.is_active:
        return HttpResponse("Compte local désactivé.", status=403)

    roles = claims.get("app_roles", [])

    if not isinstance(roles, list) or not all(
        isinstance(role, str) for role in roles
    ):
        return HttpResponse("Format des rôles invalide.", status=400)

    allowed_roles = {"reader", "manager"}
    app_roles = sorted(set(roles) & allowed_roles)
    auth_login(
        request,
        user,
        backend="django.contrib.auth.backends.ModelBackend",
    )
    request.session["oidc_id_token"] = token["id_token"]
    request.session["app_roles"] = app_roles
    return redirect("home")

@never_cache
@login_required
def dashboard(request):
    return render(request, "iam_portal/dashboard.html")


@never_cache
@roles_required("reader", "manager")
def reports(request):
    return HttpResponse("Rapports — consultation autorisée.")


@never_cache
@roles_required("manager")
def management(request):
    return HttpResponse("Gestion — accès manager autorisé.")


@never_cache
@require_POST
def logout(request):
    id_token = request.session.get("oidc_id_token")

    auth_logout(request)

    if not id_token:
        return HttpResponse(
            "Session Django fermée. "
            "Déconnexion Keycloak non effectuée : ID token absent."
        )

    try:
        return oauth.keycloak.logout_redirect(
            request,
            post_logout_redirect_uri="http://localhost:8001/logged-out/",
            id_token_hint=id_token,
        )
    except Exception as exc:
        logger.warning(
            "Erreur déconnexion OIDC : %s.%s",
            type(exc).__module__,
            type(exc).__name__,
        )
        return HttpResponse(
            "Session Django fermée. "
            "La déconnexion Keycloak n’a pas pu être demandée.",
            status=503,
        )


@never_cache
def logged_out(request):
    try:
        oauth.keycloak.validate_logout_response(request)
    except Exception:
        return HttpResponse(
            "Retour de déconnexion non reconnu.",
            status=400,
        )

    return HttpResponse(
        "Déconnexion Django et Keycloak terminée."
    )
