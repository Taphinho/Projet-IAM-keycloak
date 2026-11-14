from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def roles_required(*required_roles):
    """Require authentication and at least one role from the server session."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            roles = request.session.get("app_roles", [])

            if not isinstance(roles, list) or not all(
                isinstance(role, str) for role in roles
            ):
                return HttpResponseForbidden("Accès refusé.")

            if not set(roles).intersection(required_roles):
                return HttpResponseForbidden("Accès refusé.")

            return view(request, *args, **kwargs)

        return wrapped

    return decorator
