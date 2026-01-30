from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

from utils.general_codes import generate_manager_password
from utils.emails import send_temporary_credentials

from .models import User


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
        ]

    def create(self, validated_data):
        password = generate_manager_password()
        user = User.objects.create_user(password=password,**validated_data)       


        if not send_temporary_credentials(user.email, password):
            return
        user.raw_password = password
        return user
       


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        user = authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed("Invalid email or password")

        if not user.is_active:
            raise AuthenticationFailed("Account is disabled")       

        refresh = RefreshToken.for_user(user)

        to_return = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
            },
        }

        return to_return

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']

        return attrs
    
    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist
        except TokenError:
            self.fail('Wrong Token!')
