from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True,null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='media/profile_photo/')

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",
        blank=True
    )





class VerificationCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

class Subsubcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subsubcategories")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="subsubcategories")
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category.name} -> {self.subcategory.name} -> {self.name}"

class Item(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("not_active", "Not Active"),
    ]

    TYPE_CHOICES = [
        ("lost_item", "Lost Item"),
        ("found_item", "Found Item")
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="items")
    subsubcategory = models.ForeignKey(Subsubcategory, on_delete=models.CASCADE, related_name="items")

    def __str__(self):
        return f"{self.title} ({self.category.name} -> {self.subcategory.name})"

class ItemPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="media/item_photos/")

    def __str__(self):
        return f"Photo for {self.item.title}"