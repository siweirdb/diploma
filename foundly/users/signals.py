from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
import os

@receiver(post_save, sender=User)
def create_qr_code(sender, instance, created, **kwargs):
    if created:
        instance.generate_qr_code()
        instance.save()


def delete(self, *args, **kwargs):
    if self.qr_code:
        if os.path.isfile(self.qr_code.path):
            os.remove(self.qr_code.path)
    super().delete(*args, **kwargs)