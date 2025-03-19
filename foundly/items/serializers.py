from .models import ItemPhoto
from users.models import User
from rest_framework import serializers
import re
import random
from django.core.mail import send_mail

from items.models import Item, Category, Subcategory, Subsubcategory, ItemPhoto
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPhoto
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data["item"])
        photo = ItemPhoto.objects.create(
            item = validated_data["item"],
            image = validated_data["image"],
        )

        return photo



class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


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
            date = validated_data["date"],
            longitude = validated_data["longitude"],
            address = validated_data["address"],
            status = validated_data["status"],
            user = user,
            category = validated_data["category"],
            subcategory = validated_data["subcategory"],
            subsubcategory = validated_data["subsubcategory"],
            phone_number = validated_data["phone_number"],
        )
        print(photos)
        if not photos:
            ItemPhoto.objects.create(item=item, image="item_photos/default.jpg")
        else:
            for photo in photos:
                ItemPhoto.objects.create(item=item, image=photo)

        return item






