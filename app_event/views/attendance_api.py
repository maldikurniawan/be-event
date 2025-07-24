from decouple import config
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.template.loader import render_to_string
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from app_event.models import Event, EventAttendance
from app_event.paginations import CustomPagination
from app_event.serializers import EventAttendanceSerializer
from be_event.permissions import PermissionMixin
from utils.utils import verify_turnstile_token


class EventAttendanceListApi(PermissionMixin, generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = EventAttendance.objects.all().order_by("-created_at")
    serializer_class = EventAttendanceSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["nama"]
    ordering_fields = "__all__"

    def get_queryset(self):
        """
        Filter daftar hadir berdasarkan slug event (jika ada).
        """
        queryset = EventAttendance.objects.all().order_by("-created_at")
        slug = self.kwargs.get("slug")
        if slug:
            queryset = queryset.filter(event__slug=slug)
        return queryset

    def create(self, request, *args, **kwargs):
        slug = self.kwargs.get("slug")
        try:
            event = Event.objects.get(slug=slug)
        except Event.DoesNotExist:
            return Response(
                {
                    "status": status.HTTP_404_NOT_FOUND,
                    "message": f"Event dengan slug '{slug}' tidak ditemukan.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        now = timezone.now()

        if event.waktu_mulai and now < event.waktu_mulai:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Pendaftaran belum dibuka. Event ini belum dimulai.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event.waktu_selesai and now > event.waktu_selesai:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Pendaftaran ditutup. Event ini sudah selesai.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verifikasi token Turnstile
        token = request.data.get("token")
        if not token or not verify_turnstile_token(
            token, request.META.get("REMOTE_ADDR")
        ):
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Verifikasi Turnstile gagal.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)

        # Ambil data email dan nama dari hasil serializer
        nama = serializer.validated_data.get("nama")
        email_to = serializer.validated_data.get("email")

        # Siapkan isi email
        subject = f"Konfirmasi Kehadiran Event: {event.nama}"
        message = f"Halo {nama},\n\nTerima kasih telah mendaftar ke event {event.nama}."

        html_message = render_to_string(
            "emails/event_attendance_confirmation.html",
            {
                "nama": nama,
                "event": event,
            },
        )

        from_email = f"EventBoard <{config('EMAIL_HOST_USER')}>"

        # Konfigurasi backend email manual
        backend_email = EmailBackend(
            host=config("EMAIL_HOST"),
            port=config("EMAIL_PORT", cast=int),
            username=config("EMAIL_HOST_USER"),
            password=config("EMAIL_HOST_PASSWORD"),
            use_tls=config("EMAIL_USE_TLS", cast=bool),
            fail_silently=False,
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[email_to],
                html_message=html_message,
                connection=backend_email,
                fail_silently=False,
            )
        except Exception as e:
            return Response(
                {
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": f"Gagal mengirim email: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = {
            "status": status.HTTP_201_CREATED,
            "message": "Data Created Successfully!",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_201_CREATED)


class EventAttendanceAPIView(PermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = EventAttendance.objects.all()
    serializer_class = EventAttendanceSerializer
    pagination_class = CustomPagination
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response = {
            "status": status.HTTP_200_OK,
            "message": "Data Updated Successfully!",
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        response = {
            "status": status.HTTP_200_OK,
            "message": "Data Deleted Successfully!",
        }
        return Response(response, status=status.HTTP_200_OK)


class EventAttendanceAllListApi(PermissionMixin, APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, slug=None):
        attendances = EventAttendance.objects.all().order_by("-created_at")

        serializer = EventAttendanceSerializer(attendances, many=True)
        return Response(
            {
                "count": attendances.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
