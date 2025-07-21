from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response

from app_event.models import EventAttendance
from app_event.paginations import CustomPagination
from app_event.serializers import EventAttendanceSerializer
from be_event.permissions import PermissionMixin


class EventAttendanceListApi(PermissionMixin, generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = EventAttendance.objects.all()
    serializer_class = EventAttendanceSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "nama",
    ]
    ordering_fields = "__all__"

    def get_queryset(self):
        """
        Optionally filters the queryset based on request parameters.
        """
        queryset = self.queryset
        return queryset

    def create(self, request, *args, **kwargs):
        # Convert request.data to mutable to avoid QueryDict immutability error
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
