from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from app_event.views import *

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("event/", EventAttendanceListApi.as_view(), name="event"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
