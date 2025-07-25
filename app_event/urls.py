from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app_event.views import *

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("event/", EventListApi.as_view(), name="event-list-create"),
    path("event/<int:id>/", EventAPIView.as_view(), name="event-detail"),
    path(
        "event/attendance/all/",
        EventAttendanceAllListApi.as_view(),
        name="event-attendance-all",
    ),
    path(
        "event/attendance/<int:id>/",
        EventAttendanceAPIView.as_view(),
        name="event-attendance-detail",
    ),
    path(
        "event/<slug:slug>/attendance/",
        EventAttendanceListApi.as_view(),
        name="event-attendance-list-create",
    ),
    path(
        "event/<slug:slug>/attendance/export-excel/",
        EventAttendanceExportExcelApi.as_view(),
        name="event-attendance-export-excel",
    ),
]
