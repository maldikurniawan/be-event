from io import BytesIO

import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Event(models.Model):
    nama = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    deskripsi = models.TextField(null=True, blank=True)
    waktu_mulai = models.DateTimeField(null=True, blank=True)
    waktu_selesai = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.nama:
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Hapus barcode jika ada
        if hasattr(self, "barcode"):
            if self.barcode.image and self.barcode.image.name:
                # Hapus file barcode dari storage
                if default_storage.exists(self.barcode.image.name):
                    default_storage.delete(self.barcode.image.name)
            # Hapus instance EventBarcode-nya
            self.barcode.delete()

        super().delete(*args, **kwargs)

    def is_finished(self):
        return self.waktu_selesai and timezone.now() > self.waktu_selesai


class EventAttendance(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="attendances",
        null=True,
        blank=True,
    )
    nama = models.CharField(max_length=255, null=True, blank=True)
    nohp = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    nama_perusahaan = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class EventBarcode(models.Model):
    event = models.OneToOneField(
        "Event", on_delete=models.CASCADE, related_name="barcode", null=True, blank=True
    )
    barcode_value = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="barcodes/", null=True, blank=True)

    def generate_barcode(self):
        # Default barcode_value = event slug
        if not self.barcode_value:
            self.barcode_value = f"http://localhost:5173/form/{self.event.slug}"

        if not self.url:
            self.url = self.barcode_value

        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(self.barcode_value)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")

        filename = f"{self.event.slug or self.event.id}_qrcode.png"
        self.image.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        self.generate_barcode()
        super().save(*args, **kwargs)
