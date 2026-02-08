from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from datetime import datetime

from utils.general_codes import generate_manager_password, generate_verification_code
from utils.emails import send_temporary_credentials, send_password_reset_email
from utils.validators import validate_rwanda_phone

from .models import User, VerificationCode


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

    def validate_phone(self, value):
        return validate_rwanda_phone(value)

    def create(self, validated_data):
        password = generate_manager_password()
        user = User.objects.create_user(password=password, **validated_data)

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


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        code = generate_verification_code()

        VerificationCode.objects.filter(
            user=user, purpose=VerificationCode.PASSWORD_RESET, is_used=False
        ).update(is_used=True)

        VerificationCode.objects.create(
            user=user,
            code=code,
            purpose=VerificationCode.PASSWORD_RESET,
        )

        send_password_reset_email(email, code)


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def save(self):
        email = self.validated_data["email"]
        code = self.validated_data["code"]
        new_password = self.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)

            verification_code = VerificationCode.objects.filter(
                user=user,
                code=code,
                purpose=VerificationCode.PASSWORD_RESET,
                is_used=False,
            ).latest("created_on")

        except (User.DoesNotExist, VerificationCode.DoesNotExist):
            raise serializers.ValidationError({"code": "Invalid verification code"})

        if not verification_code.is_valid:
            raise serializers.ValidationError({"code": "Code is expired or used"})

        user.set_password(new_password)
        user.has_temporary_password = False
        user.save()

        verification_code.is_used = True
        verification_code.save()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]

        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist
        except TokenError:
            self.fail("Wrong Token!")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
