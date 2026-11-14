from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve


@override_settings(ALLOWED_HOSTS=["testserver"])
class PortalSecurityTests(SimpleTestCase):
    def test_dashboard_requires_login(self):
        request = RequestFactory().get("/dashboard/")
        request.user = AnonymousUser()
        response = resolve(request.path).func(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login/?next="))

    def test_logout_rejects_get(self):
        request = RequestFactory().get("/logout/")
        self.assertEqual(resolve(request.path).func(request).status_code, 405)

    def test_logout_callback_requires_state(self):
        request = RequestFactory().get("/logged-out/")
        request.session = {}
        self.assertEqual(resolve(request.path).func(request).status_code, 400)
