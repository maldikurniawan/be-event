from django.db import models
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


class EventAttendance(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="attendances", null=True, blank=True
    )
    nama = models.CharField(max_length=255, null=True, blank=True)
    nohp = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    nama_perusahaan = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
