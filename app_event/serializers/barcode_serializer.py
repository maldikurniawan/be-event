from rest_framework import serializers

from app_event.models import EventBarcode


class EventBarcodeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    form_url = serializers.SerializerMethodField()

    class Meta:
        model = EventBarcode
        fields = ["barcode_value", "form_url", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_form_url(self, obj):
        request = self.context.get("request")
        if obj.url and request:
            return request.build_absolute_uri(obj.url)
        return obj.url
