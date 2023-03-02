import json

from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, RedirectView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_network.user.forms import CustomAuthenticationForm, UserRegistrationForm
from social_network.user.serializers import ChangePasswordSerializer

User = get_user_model()


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user and self.request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if User.objects.filter(email=request.POST["email"]).exists():
            messages.warning(request, "This email is already taken")
            return redirect("register")

        user_form = UserRegistrationForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get("password1")
            user.set_password(password)
            user.save()
            messages.success(request, "Successfully registered")
            return redirect(reverse_lazy("login"))
        else:
            return render(request, "users/register.html", {"form": user_form})


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    success_url = "/"
    form_class = CustomAuthenticationForm

    def form_invalid(self, form):
        if self.request.method == "POST":
            context = self.get_context_data(form=form)
            context["form_errors"] = form.errors
            return self.render_to_response(context)
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        return self.success_url


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """

    url = reverse_lazy("home")

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        messages.success(request, "You are now logged out")
        return super(LogoutView, self).get(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):

        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        old_password = serializer.data.get("old_password")
        if not user.check_password(old_password):
            return Response(
                {"old_password_error": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.data.get("new_password"))
        user.save()
        return Response(
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )
