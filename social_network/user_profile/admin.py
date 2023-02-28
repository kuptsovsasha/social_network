from django.contrib import admin

from social_network.user_profile.models import Profile, FriendList, FriendRequest

# Register your models here.

admin.site.register(Profile)
admin.site.register(FriendList)
admin.site.register(FriendRequest)
