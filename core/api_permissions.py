import logging

from rest_framework.permissions import BasePermission


API_STUDENT_GROUP = "api_student"
API_SERVER_GROUP = "api_server"
API_GROUPS = (API_STUDENT_GROUP, API_SERVER_GROUP)

security_logger = logging.getLogger("core.api.security")


def user_has_api_role(user, role: str) -> bool:
    return bool(
        user
        and user.is_authenticated
        and user.is_active
        and user.groups.filter(name=role).exists()
    )


def is_api_server(user) -> bool:
    return user_has_api_role(user, API_SERVER_GROUP)


class HasQuestionAPIRole(BasePermission):
    """Require an authenticated integration user with an explicit API role."""

    message = "Bu token soru API'sine erişim yetkisine sahip değil."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        has_role = request.user.groups.filter(name__in=API_GROUPS).exists()
        if not has_role:
            security_logger.warning(
                "API access denied: user=%s path=%s reason=missing_role",
                request.user.get_username(),
                request.path,
            )
        return has_role
