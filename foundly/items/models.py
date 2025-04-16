from django.db import models
import uuid
from django.conf import settings


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

class Subsubcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subsubcategories", null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="subcategory", null=True, blank=True)
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
    date = models.DateTimeField()
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    subsubcategory = models.ForeignKey(Subsubcategory, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, default="")







    def __str__(self):
        return f"{self.title} ({self.category.name} -> {self.subcategory.name})"

class ItemPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="photos", null=True, blank=True)
    image = models.ImageField(upload_to="item_photos/")
    predicted_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Photo for {self.item.title}"