from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("oidc/callback/", views.oidc_callback, name="oidc_callback"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout, name="logout"),
    path("logged-out/", views.logged_out, name="logged_out"),
]
