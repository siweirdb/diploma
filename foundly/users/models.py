import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
import os
from PIL import Image

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
        logo_path = os.path.join(settings.MEDIA_ROOT, 'qr_logo.png')
        print("Checking file existence...")
        print("File exists:", os.path.exists(logo_path), flush=True)
        print("Check complete.")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=4,
        )
        qr.add_data(f"http://localhost:8000/qr-code/{self.id}/")
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        if os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                if logo.mode != 'RGBA':
                    logo = logo.convert('RGBA')

                qr_width, qr_height = qr_img.size
                logo_size = min(qr_width, qr_height) // 5

                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

                logo_bg = Image.new('RGBA', (logo_size, logo_size), 'white')
                logo_bg.paste(logo, (0, 0), logo)

                pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

                qr_img.paste(logo_bg, pos)

            except Exception as e:
                print(f"Error adding logo to QR code: {e}")

        buffer = BytesIO()
        qr_img.save(buffer, format="PNG", quality=95)
        buffer.seek(0)

        file_name = f"qr_{self.id}.png"
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            super().save(*args, **kwargs)
            self.generate_qr_code()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.qr_code and self.qr_code.name:
            qr_path = os.path.join(settings.MEDIA_ROOT, self.qr_code.name)
            if os.path.isfile(qr_path):
                os.remove(qr_path)

        super().delete(*args, **kwargs)


class VerificationCode(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = str(random.randint(100000, 999999))
            super().save(*args, **kwargs)
            self.send_email()
        else:
            super().save(*args, **kwargs)

    def send_email(self):
        send_mail(
            'Email Verification - Foundly',
            f'Your verification code is: {self.code}',
            'foundly@yandex.kz',
            [self.email],
            fail_silently=False,
        )

