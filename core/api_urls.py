from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .api_views import QuestionViewSet, api_root, api_schema


app_name = "api-v1"

router = SimpleRouter()
router.register("questions", QuestionViewSet, basename="question")

urlpatterns = [
    path("", api_root, name="root"),
    path("schema/", api_schema, name="schema"),
    path("", include(router.urls)),
]
