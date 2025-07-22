from django.utils import timezone
from rest_framework import serializers

from app_event.models import Event
from .barcode_serializer import EventBarcodeSerializer


class EventSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    barcode = EventBarcodeSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "status",
            "nama",
            "slug",
            "deskripsi",
            "waktu_mulai",
            "waktu_selesai",
            "created_at",
            "updated_at",
            "deleted_at",
            "barcode",
        ]

    def get_status(self, obj):
        now = timezone.now()
        if obj.waktu_mulai and now < obj.waktu_mulai:
            return "belum dimulai"
        if obj.waktu_selesai and now > obj.waktu_selesai:
            return "selesai"
        return "berlangsung"
