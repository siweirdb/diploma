from .models import User, ItemPhoto
from rest_framework import serializers
import re
import random
from django.core.mail import send_mail

from items.models import VerificationCode, Item, Category, Subcategory, Subsubcategory
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

# class ItemSerializer(serializers.ModelSerializer):


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'


class SubsubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsubcategory
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number','profile_picture', 'birthday')


class CreateItemSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True
    )

    class Meta:
        model = Item
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        photos = validated_data.pop("photos", [])
        user = self.context["request"].user
        print(user)
        item = Item.objects.create(
            title = validated_data["title"],
            item_type = validated_data["item_type"],
            description = validated_data["description"],
            latitude = validated_data["latitude"],
            longitude = validated_data["longitude"],
            address = validated_data["address"],
            status = validated_data["status"],
            user = user,
            category = validated_data["category"],
            subcategory = validated_data["subcategory"],
            subsubcategory = validated_data["subsubcategory"],
        )

        if not photos:
            ItemPhoto.objects.create(item=item, image="item_photos/default.jpg")
        else:
            for photo in photos:
                ItemPhoto.objects.create(item=item, image=photo)

        return item


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
        if User.objects.filter(email=data.get("email")).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})

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

        email = validated_data['email']
        username = email.split('@')[0]
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number'),
            is_active=False
        )

        verification_code = str(random.randint(100000, 999999))
        VerificationCode.objects.create(user=user, code=verification_code)

        send_mail(
            'Email Verification - Foundly',
            f'Your verification code is: {verification_code}',
            'foundly@yandex.kz',
            [user.email],
            fail_silently=False,
        )

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

# class CreateItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Item
#         fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'phone_number')
#
#         extra_kwargs = {
#             'password': {'write_only': True},
#             'phone_number': {'required': False},
#         }






