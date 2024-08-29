from django.urls import path
from django.contrib.auth import views as auth_view

from . import views


app_name = "account"

urlpatterns = [
    path("register/", views.SignUpView.as_view(), name="register"),
    path("login/", auth_view.LoginView.as_view(), name="login"),
    path("logout/", auth_view.LogoutView.as_view(), name="logout"),
]