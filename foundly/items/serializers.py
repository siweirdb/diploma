from .models import ItemPhoto
from users.models import User
from rest_framework import serializers
import re
import random
from django.core.mail import send_mail

from items.models import Item, Category, Subcategory, Subsubcategory, ItemPhoto
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class ImageAnalysisSerializer(serializers.Serializer):
    image = serializers.ImageField()
    suggestions = serializers.SerializerMethodField()

    def get_suggestions(self, obj):
        return obj.get('suggestions', [])


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

class ItemPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPhoto
        fields = ['image']

class ItemSerializer(serializers.ModelSerializer):
    photos = ItemPhotoSerializer(many=True, read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    subcategory = serializers.CharField(source='subcategory.name', read_only=True)
    subsubcategory = serializers.CharField(source='subsubcategory.name', read_only=True)

    class Meta:
        model = Item
        fields = '__all__'

class ItemEditSerilizer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category',
                                                     write_only=True, required=False)
    subcategory_id = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all(), source='subcategory',
                                                        write_only=True, required=False)
    subsubcategory_id = serializers.PrimaryKeyRelatedField(queryset=Subsubcategory.objects.all(),
                                                           source='subsubcategory', write_only=True, required=False)

    photos = ItemPhotoSerializer(many=True, read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    subcategory = serializers.CharField(source='subcategory.name', read_only=True)
    subsubcategory = serializers.CharField(source='subsubcategory.name', read_only=True)

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
        child=serializers.ImageField(
            max_length=1000,  # Limit filename length
            allow_empty_file=False
        ),
        required=False,
        write_only=True,
        max_length=10  # Max 10 photos per item
    )

    class Meta:
        model = Item
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'category': {'required': True},
            'subcategory': {'required': False},
            'subsubcategory': {'required': False}
        }

    def validate(self, data):
        # Validate category hierarchy
        category = data.get('category')
        subcategory = data.get('subcategory')
        subsubcategory = data.get('subsubcategory')

        if subcategory and subcategory.category != category:
            raise serializers.ValidationError("Subcategory doesn't belong to selected category")

        if subsubcategory and subsubcategory.subcategory != subcategory:
            raise serializers.ValidationError("Subsubcategory doesn't belong to selected subcategory")

        return data

    def create(self, validated_data):
        photos = validated_data.pop("photos", [])
        user = self.context["request"].user

        item = Item.objects.create(
            user=user,
            email= user.email,
            **{k: v for k, v in validated_data.items() if k != 'user' and k!= 'email'}
        )

        if not photos:
            ItemPhoto.objects.create(item=item, image="item_photos/default.jpg")
        else:
            ItemPhoto.objects.bulk_create([
                ItemPhoto(item=item, image=photo) for photo in photos
            ])

        return item



