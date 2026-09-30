from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import LearningOutcome, Question


def _allowed_topic_ids(question):
    return set(question.secondary_topics.values_list("pk", flat=True)) | {
        question.primary_topic_id
    }


@receiver(m2m_changed, sender=Question.secondary_topics.through)
def validate_secondary_topics(sender, instance, action, reverse, pk_set, **kwargs):
    if action == "pre_add":
        if reverse:
            invalid_question_codes = list(
                Question.objects.filter(
                    pk__in=pk_set,
                    primary_topic_id=instance.pk,
                ).values_list("code", flat=True)
            )
            if invalid_question_codes:
                raise ValidationError(
                    "Bir konu aynı soruda hem ana hem ikincil konu olamaz: "
                    + ", ".join(invalid_question_codes)
                )
        elif instance.primary_topic_id in pk_set:
            raise ValidationError(
                {"secondary_topics": "Ana konu ikincil konu olarak seçilemez."}
            )

    if action not in {"pre_remove", "pre_clear"}:
        return

    if reverse:
        question_ids = pk_set if action == "pre_remove" else instance.secondary_questions.values_list("pk", flat=True)
        invalid_question_codes = list(
            Question.objects.filter(
                pk__in=question_ids,
                learning_outcomes__topic=instance,
            )
            .distinct()
            .values_list("code", flat=True)
        )
        if invalid_question_codes:
            raise ValidationError(
                "Bu konuya bağlı kazanımlar seçili olduğu için ilişki kaldırılamaz: "
                + ", ".join(invalid_question_codes)
            )
    else:
        removed_topic_ids = (
            set(pk_set)
            if action == "pre_remove"
            else set(instance.secondary_topics.values_list("pk", flat=True))
        )
        if instance.learning_outcomes.filter(topic_id__in=removed_topic_ids).exists():
            raise ValidationError(
                {
                    "secondary_topics": (
                        "Bu konulara bağlı kazanımlar seçili olduğu için ilişki "
                        "kaldırılamaz."
                    )
                }
            )


@receiver(m2m_changed, sender=Question.learning_outcomes.through)
def validate_learning_outcomes(sender, instance, action, reverse, pk_set, **kwargs):
    if action != "pre_add":
        return

    if reverse:
        invalid_question_codes = [
            question.code
            for question in Question.objects.filter(pk__in=pk_set).prefetch_related(
                "secondary_topics"
            )
            if instance.topic_id not in _allowed_topic_ids(question)
        ]
        if invalid_question_codes:
            raise ValidationError(
                "Kazanımın konusu bu soruların sınıflandırmasında yok: "
                + ", ".join(invalid_question_codes)
            )
    else:
        invalid_codes = list(
            LearningOutcome.objects.filter(pk__in=pk_set)
            .exclude(topic_id__in=_allowed_topic_ids(instance))
            .values_list("code", flat=True)
        )
        if invalid_codes:
            raise ValidationError(
                {
                    "learning_outcomes": (
                        "Kazanımlar yalnızca ana veya ikincil konulara bağlı "
                        "olabilir: "
                        + ", ".join(invalid_codes)
                    )
                }
            )
