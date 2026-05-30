"""Auth-related serializers (login, refresh, password reset)."""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.serializers import UserSerializer


class MITTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds user info & role claims to the JWT response."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_active:
            from rest_framework import serializers
            raise serializers.ValidationError('User account is disabled.')
        data['user'] = UserSerializer(self.user).data
        return data
