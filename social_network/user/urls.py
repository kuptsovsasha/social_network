from django.urls import path
from django.views.generic import TemplateView

from social_network.user.views import (
    ChangePasswordView,
    CustomLoginView,
    LogoutView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path(
        "change-password-template/",
        TemplateView.as_view(template_name="users/change-password.html"),
        name="change_password_template",
    ),
    path("change-password", ChangePasswordView.as_view(), name="change_password"),
]
