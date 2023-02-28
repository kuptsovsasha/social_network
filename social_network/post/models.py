from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from social_network.user_profile.models import Profile


class Post(models.Model):
    content = models.TextField(blank=True, null=True)
    img = models.ImageField(blank=True, null=True, upload_to="post_images")
    date_posted = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.date_posted.__str__()

