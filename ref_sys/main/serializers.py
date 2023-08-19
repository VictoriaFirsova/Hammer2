from rest_framework import serializers
from .models import UserProfile, AuthorizationCode
import random
import string


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

    def perform_create(self, serializer):
        phone = self.kwargs.get('phone')

        # Генерация кода авторизации и инвайт-кода
        auth_code = ''.join(random.choices(string.digits, k=6))
        invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        serializer.save(phone=phone, auth_code=auth_code, invite_code=invite_code)


class UserProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone']


class AuthorizationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizationCode
        fields = ['phone', 'code']


class UserProfileInviteCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['invite_code']


class AuthorizationCodeVerifySerializer(serializers.Serializer):
    code = serializers.CharField()