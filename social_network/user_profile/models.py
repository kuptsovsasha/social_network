from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.DO_NOTHING, related_name="profile"
    )
    profile_image = models.ImageField(upload_to="avatars", default="avatars/guest.png")
    cover_image = models.ImageField(upload_to="avatars", default="avatars/cover.png")
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.email

    def get_profile_image(self):
        if self.profile_image:
            return self.profile_image.url

    def get_cover_image(self):
        if self.cover_image:
            return self.cover_image.url
        return settings.MEDIA_URL + self._meta.get_field("cover_image").get_default()


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    if kwargs.get("created", False):
        Profile.objects.create(user=kwargs["instance"])


class FriendList(models.Model):
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="friend_list_profile"
    )
    friends = models.ManyToManyField(Profile, blank=True, related_name="friends")

    def __str__(self):
        return self.profile.user.email

    def add_friend(self, profile):
        if profile not in self.friends.all():
            self.friends.add(profile)
            self.save()

    def remove_friend(self, profile):
        if profile in self.friends.all():
            self.friends.remove(profile)
            self.save()


class FriendRequest(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="receiver"
    )
    is_active = models.BooleanField(blank=True, null=True, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.user.email

    def accept(self):
        # update both sender and receiver friend list
        receiver_friend_list = FriendList.objects.get_or_create(profile=self.receiver)
        if receiver_friend_list:
            receiver_friend_list[0].add_friend(self.sender)
            sender_friend_list = FriendList.objects.get_or_create(profile=self.sender)
            if sender_friend_list:
                sender_friend_list[0].add_friend(self.receiver)
                self.is_active = False
                self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()
