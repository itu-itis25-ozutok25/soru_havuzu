from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views
from .media_views import question_image


urlpatterns = [
    path("", views.question_list, name="question-list"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("questions/new/", views.question_create, name="question-create"),
    path("questions/<str:code>/", views.question_detail, name="question-detail"),
    path("questions/<str:code>/edit/", views.question_update, name="question-update"),
    path(
        "questions/<str:code>/solution/",
        views.question_solution,
        name="question-solution",
    ),
    path("questions/<str:code>/archive/", views.question_archive, name="question-archive"),
    path("questions/<str:code>/restore/", views.question_restore, name="question-restore"),
    path("questions/<str:code>/delete/", views.question_delete, name="question-delete"),
    path("health/", views.health_check, name="health-check"),
    path("media/<path:path>", question_image, name="question-image"),
    path("api/v1/", include("core.api_urls")),
]
