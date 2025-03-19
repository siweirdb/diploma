from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def create_qr_code(sender, instance, created, **kwargs):
    if created:
        instance.generate_qr_code()
        instance.save()
