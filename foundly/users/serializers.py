from .models import User
from rest_framework import serializers
import re
import random
from django.core.mail import send_mail

from .models import VerificationCode
from rest_framework_simplejwt.tokens import RefreshToken, TokenError



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number','profile_picture', 'birthday', 'qr_code')

class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'birthday', 'profile_picture')

    def validate(self, data):
        username = data.get("username")
        phone_number = data.get("phone_number")
        first_name, last_name = data.get("first_name"), data.get("last_name")

        if username and User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})

        if phone_number and User.objects.exclude(pk=self.instance.pk).filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "This phone number is already in use."})

        if phone_number and len(phone_number) not in [11, 12]:
            raise serializers.ValidationError({"phone_number": "Phone number has incorrect length."})

        if phone_number and not (phone_number.startswith("+77") or phone_number.startswith("87")):
            raise serializers.ValidationError({"phone_number": "Phone number format is incorrect."})

        if first_name and any(char.isdigit() for char in first_name):
            raise serializers.ValidationError({"first_name": "First name should not contain digits."})
        if last_name and any(char.isdigit() for char in last_name):
            raise serializers.ValidationError({"last_name": "Last name should not contain digits."})

        return data





class QrCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profile_picture','phone_number')


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirmation = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.instance

        if not user.check_password(data["current_password"]):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})

        if data["new_password"] != data["new_password_confirmation"]:
            raise serializers.ValidationError({"new_password": "New password and confirmation do not match."})

        if user.check_password(data["new_password"]):
            raise serializers.ValidationError({"new_password": "New password must be different from the current password."})
        password = data["new_password"]
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one uppercase letter."})
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one lowercase letter."})
        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one digit."})


        return data

    def save(self, **kwargs):
        user = self.instance
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'phone_number')
        extra_kwargs = {
            'password': {'write_only': True},
            'phone_number': {'required': False},
        }

    def validate(self, data):
        password = data.get("password")
        password2 = data.pop("password2", None)  # Remove password2 from data

        if password != password2:
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one uppercase letter."})
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one lowercase letter."})
        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one digit."})

        return data

    def create(self, validated_data):
        email = validated_data['email']
        username = email.split('@')[0]

        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number'),
            is_active=True
        )

        user.generate_qr_code()
        user.save()

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh_token']

        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('invalid_token')
