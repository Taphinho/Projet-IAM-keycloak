from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve


@override_settings(ALLOWED_HOSTS=["testserver"])
class RoleAccessTests(SimpleTestCase):
    def response(self, path, roles=None, *, authenticated=True):
        request = RequestFactory().get(path)
        request.user = User(username="test") if authenticated else AnonymousUser()
        request.session = {} if roles is None else {"app_roles": roles}
        return resolve(request.path).func(request)

    def test_role_access_matrix(self):
        for roles, reports, management in (
            ([], 403, 403),
            (["reader"], 200, 403),
            (["manager"], 200, 200),
            (["reader", "manager"], 200, 200),
            (["unknown"], 403, 403),
        ):
            for path, expected in (("/reports/", reports), ("/management/", management)):
                with self.subTest(roles=roles, path=path):
                    response = self.response(path, roles)
                    self.assertEqual(response.status_code, expected)
                    self.assertIn("no-store", response.headers["Cache-Control"])

    def test_missing_or_malformed_roles_are_denied(self):
        for roles in (None, "manager", {"manager": True}, ["reader", 1], [["manager"]]):
            for path in ("/reports/", "/management/"):
                with self.subTest(roles=roles, path=path):
                    self.assertEqual(self.response(path, roles).status_code, 403)

    def test_anonymous_user_is_redirected_even_with_roles(self):
        for path in ("/reports/", "/management/"):
            response = self.response(path, ["manager"], authenticated=False)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/login/?next="))

    def test_query_parameters_cannot_grant_roles(self):
        response = self.response("/management/?app_roles=manager&role=manager", [])
        self.assertEqual(response.status_code, 403)
