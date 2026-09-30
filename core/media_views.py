import mimetypes
from pathlib import PurePosixPath

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import BasePermission

from .api_permissions import API_GROUPS, is_api_server
from .models import Question


class HasProtectedMediaAccess(BasePermission):
    message = "Bu dosyaya erişim yetkiniz yok."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.auth is None:
            return True
        return request.user.groups.filter(name__in=API_GROUPS).exists()


@api_view(("GET",))
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((HasProtectedMediaAccess,))
def question_image(request, path):
    normalized_path = PurePosixPath(path).as_posix().lstrip("/")
    if not normalized_path.startswith("questions/originals/"):
        raise Http404

    question = get_object_or_404(Question, original_image=normalized_path)
    if request.auth is not None and not is_api_server(request.user):
        if question.is_archived or not question.is_complete:
            raise Http404

    try:
        image_file = question.original_image.storage.open(
            question.original_image.name,
            mode="rb",
        )
    except (FileNotFoundError, OSError) as exc:
        raise Http404 from exc

    content_type = mimetypes.guess_type(question.original_image.name)[0]
    response = FileResponse(image_file, content_type=content_type or "application/octet-stream")
    response["Content-Disposition"] = (
        f'inline; filename="{PurePosixPath(question.original_image.name).name}"'
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response
