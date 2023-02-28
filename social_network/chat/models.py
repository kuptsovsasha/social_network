from django.db import models

from social_network.user_profile.models import Profile


class Message(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='message_sender')
    receiver = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='message_receiver')
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.user.email
