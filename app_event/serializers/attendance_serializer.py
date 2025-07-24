import phonenumbers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import serializers

from app_event.models import EventAttendance


class EventAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendance
        fields = "__all__"

    def validate_nohp(self, value):
        try:
            parsed = phonenumbers.parse(value, "ID")
            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError("Nomor HP tidak valid.")
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Format nomor HP tidak dikenali.")
        return value

    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Email tidak valid.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Samarkan nomor HP
        nohp = data.get("nohp", "")
        if len(nohp) >= 6:
            data["nohp"] = f"{nohp[:2]}{'*' * (len(nohp) - 4)}{nohp[-2:]}"
        elif len(nohp) > 0:
            data["nohp"] = f"{nohp[0]}{'*' * (len(nohp) - 1)}"

        # Samarkan email
        email = data.get("email", "")
        if "@" in email:
            name, domain = email.split("@", 1)
            if len(name) > 1:
                data["email"] = f"{name[0]}{'*' * (len(name) - 1)}@{domain}"
            else:
                data["email"] = f"{name}*@{domain}"

        return data
