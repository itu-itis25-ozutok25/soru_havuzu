from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import ValidationError

from .api_schema import OPENAPI_SCHEMA
from .api_permissions import HasQuestionAPIRole, is_api_server
from .models import Question
from .serializers import ServerQuestionSerializer, StudentQuestionSerializer


def _csv_values(request, name):
    return [value.strip() for value in request.query_params.get(name, "").split(",") if value.strip()]


def _is_true(request, name):
    return request.query_params.get(name, "").lower() in {"1", "true", "yes"}


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, HasQuestionAPIRole)
    lookup_field = "code"
    lookup_value_regex = r"Q[0-9]{6}"

    def get_serializer_class(self):
        if is_api_server(self.request.user):
            return ServerQuestionSerializer
        return StudentQuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.select_related(
            "primary_topic",
            "question_type",
        ).prefetch_related(
            "secondary_topics",
            "learning_outcomes__topic",
        )
        is_authorized_server = is_api_server(self.request.user)

        if not (is_authorized_server and _is_true(self.request, "include_archived")):
            queryset = queryset.filter(archived_at__isnull=True)
        if not (is_authorized_server and _is_true(self.request, "include_incomplete")):
            queryset = queryset.filter(
                question_type__isnull=False,
                difficulty__isnull=False,
            ).exclude(solution="")

        if self.action not in {"list", "random"}:
            return queryset

        search_term = self.request.query_params.get("q", "").strip()
        if search_term:
            queryset = queryset.filter(
                Q(code__icontains=search_term)
                | Q(question_text__icontains=search_term)
            )

        topic_codes = _csv_values(self.request, "topics")
        if topic_codes:
            queryset = queryset.filter(
                Q(primary_topic__code__in=topic_codes)
                | Q(secondary_topics__code__in=topic_codes)
            )

        outcome_codes = _csv_values(self.request, "outcomes")
        outcome_match = self.request.query_params.get("outcome_match", "any")
        if outcome_match not in {"any", "all"}:
            raise ValidationError(
                {"outcome_match": "Bu alan 'any' veya 'all' olmalıdır."}
            )
        if outcome_codes:
            if outcome_match == "all":
                queryset = queryset.annotate(
                    selected_outcome_count=Count(
                        "learning_outcomes",
                        filter=Q(learning_outcomes__code__in=outcome_codes),
                        distinct=True,
                    )
                ).filter(selected_outcome_count=len(set(outcome_codes)))
            else:
                queryset = queryset.filter(
                    learning_outcomes__code__in=outcome_codes
                )

        question_type = self.request.query_params.get("question_type", "").strip()
        if question_type:
            queryset = queryset.filter(question_type__code=question_type)

        difficulty = self.request.query_params.get("difficulty", "").strip()
        if difficulty:
            try:
                difficulty_value = int(difficulty)
            except ValueError as exc:
                raise ValidationError(
                    {"difficulty": "Zorluk 1 ile 5 arasında bir tam sayı olmalıdır."}
                ) from exc
            if difficulty_value not in range(1, 6):
                raise ValidationError(
                    {"difficulty": "Zorluk 1 ile 5 arasında olmalıdır."}
                )
            queryset = queryset.filter(difficulty=difficulty_value)

        excluded_codes = _csv_values(self.request, "exclude")
        if excluded_codes:
            queryset = queryset.exclude(code__in=excluded_codes)

        return queryset.distinct().order_by("code")

    @action(detail=False, methods=("get",), url_path="random")
    def random(self, request):
        count = request.query_params.get("count", "1")
        try:
            count = int(count)
        except ValueError:
            return Response(
                {"count": "Bu alan 1 ile 100 arasında bir tam sayı olmalıdır."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if count not in range(1, 101):
            return Response(
                {"count": "Bu alan 1 ile 100 arasında olmalıdır."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        questions = list(self.filter_queryset(self.get_queryset()).order_by("?")[:count])
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)


@api_view(("GET",))
@authentication_classes((TokenAuthentication,))
@permission_classes((AllowAny,))
def api_root(request):
    return Response(
        {
            "name": "Soru Havuzu API",
            "version": "v1",
            "status": "ready",
            "questions": reverse("api-v1:question-list", request=request),
            "random_questions": reverse("api-v1:question-random", request=request),
            "schema": reverse("api-v1:schema", request=request),
        }
    )


@api_view(("GET",))
@authentication_classes(())
@permission_classes((AllowAny,))
def api_schema(request):
    return Response(OPENAPI_SCHEMA)
