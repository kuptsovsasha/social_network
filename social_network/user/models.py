from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'username',
        max_length=50,
        unique=False,
        help_text='Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.',
    )
    email = models.EmailField(unique=True, blank=False,
                              error_messages={
                                  'unique': "A user with that email already exists.",
                              })
    gender = models.CharField(max_length=20, blank=True, null=True)
    status = models.BooleanField(default=False)
    about = models.TextField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email
