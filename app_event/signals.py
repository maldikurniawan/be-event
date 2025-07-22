from django.db.models.signals import post_save
from django.dispatch import receiver

from app_event.models import Event, EventBarcode


@receiver(post_save, sender=Event)
def generate_barcode_for_event(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "barcode"):
        EventBarcode.objects.create(event=instance)
