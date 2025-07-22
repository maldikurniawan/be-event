from django.utils import timezone
from rest_framework import serializers

from app_event.models import Event


class EventSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = "__all__"

    def get_status(self, obj):
        now = timezone.now()
        if obj.waktu_mulai and now < obj.waktu_mulai:
            return "belum dimulai"
        if obj.waktu_selesai and now > obj.waktu_selesai:
            return "selesai"
        return "berlangsung"
