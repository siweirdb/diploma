from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
# class RegisterSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(required=True, max_length=30)
#     last_name = serializers.CharField(required=True, max_length=30)
#     password2 = serializers.CharField(write_only=True, required=True)
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']
#         extra_kwargs = {'password': {'write_only': True}}
#
#     def validate(self, data):
#         password = data.get("password")
#         password2 = data.get("password2")
#
#         if password != password2:
#             raise serializers.ValidationError({"password2": "Passwords do not match."})
#
#         if len(password) < 8:
#             raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
#         if not re.search(r'[A-Z]', password):
#             raise serializers.ValidationError({"password": "Password must contain at least one uppercase letter."})
#         if not re.search(r'[a-z]', password):
#             raise serializers.ValidationError({"password": "Password must contain at least one lowercase letter."})
#         if not re.search(r'[0-9]', password):
#             raise serializers.ValidationError({"password": "Password must contain at least one digit."})
#         if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
#             raise serializers.ValidationError({"password": "Password must contain at least one special character."})
#
#         return data
#
#     def create(self, validated_data):
#         validated_data.pop('password2')
#         user = User.objects.create_user(**validated_data)
#         return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')

    def validate(self, data):

        password = data.get("password")
        password2 = data.get("password2")

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
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one special character."})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)




# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)
#         data.update({
#             'user_id': self.user.id,
#             'username': self.user.username,
#             'email': self.user.email,
#         })
#         return data
#
#
# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'first_name', 'last_name']
