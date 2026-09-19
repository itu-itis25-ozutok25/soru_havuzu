from django.urls import path

from .views import api_root, health_check


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("api/v1/", api_root, name="api-v1-root"),
]

