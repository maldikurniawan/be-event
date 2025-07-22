from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app_event.views import *

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("event/", EventListApi.as_view(), name="event-list-create"),
    path("event/<uuid:id>/", EventAPIView.as_view(), name="event-detail"),
    path(
        "event/<slug:slug>/attendance/",
        EventAttendanceListApi.as_view(),
        name="event-attendance-list-create",
    ),
    path(
        "event/attendance/<uuid:id>/",
        EventAttendanceAPIView.as_view(),
        name="event-attendance-detail",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
