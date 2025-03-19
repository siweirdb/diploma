import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, default='', unique=False, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_photo/', default='profile_photo/photo_2025-02-24 23.37.57.jpeg')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
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

    def generate_qr_code(self):
        qr = qrcode.make(f"http://localhost:8000/qr-code/{self.id}/")  # QR code URL
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        file_name = f"qr_{self.id}.png"
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)  # Save to ImageField

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to get a valid user ID
        if not self.qr_code:  # Generate QR code only if it doesn't exist
            self.generate_qr_code()
            super().save(*args, **kwargs)  # Save again with QR code



class VerificationCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"

