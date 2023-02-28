from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username",
                  "email",
                  "password1",
                  "password2")

    def clean_username(self):
        username = self.cleaned_data['username']

        if ' ' in username:
            raise forms.ValidationError("Username can't contain spaces.")
        return username

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['username']

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is None or password is None:
            raise ValidationError("Please enter both email and password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("User does not exist")

        if not user.check_password(password):
            raise ValidationError("Invalid email or password")

        self.user_cache = user
        return self.cleaned_data
