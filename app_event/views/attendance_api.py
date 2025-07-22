from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from app_event.models import Event, EventAttendance
from app_event.paginations import CustomPagination
from app_event.serializers import EventAttendanceSerializer
from be_event.permissions import PermissionMixin


class EventAttendanceListApi(PermissionMixin, generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = EventAttendance.objects.all().order_by("-created_at")
    serializer_class = EventAttendanceSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "nama",
    ]
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

        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)

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
