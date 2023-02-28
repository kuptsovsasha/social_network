from rest_framework import serializers

from social_network.user.serializers import UserSerializer
from social_network.user_profile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    gender = serializers.CharField(source="user.gender", read_only=True)

    class Meta:
        model = Profile
        fields = ("profile_image", "username", "email", "gender")

    def to_internal_value(self, data):
        """
        remove from external data values which related to auth user object
        and update User model with UserSerializer
        """
        auth_user_data = {
            key: value for key, value in data.items() if key not in "profile_image"
        }

        user_sz = UserSerializer(
            instance=self.instance.user, data=auth_user_data, partial=True
        )
        user_sz.is_valid(raise_exception=True)
        user_sz.save()

        if data.get("profile_image"):

            return {"profile_image": data["profile_image"]}
        return {}
