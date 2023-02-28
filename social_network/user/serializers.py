from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Update User object data
    """
    class Meta:
        model = User
        fields = "__all__"


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        if self.initial_data["old_password"] == self.initial_data["new_password"]:
            raise serializers.ValidationError(
                "New password can't be same as old password"
            )
        return value

