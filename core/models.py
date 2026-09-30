import hashlib

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.utils import timezone


def calculate_file_hash(file):
    digest = hashlib.sha256()
    file.open("rb")
    for chunk in file.chunks():
        digest.update(chunk)
    file.seek(0)
    return digest.hexdigest()


class ImmutableCodeQuerySet(models.QuerySet):
    def update(self, **kwargs):
        if "code" in kwargs:
            raise ValidationError({"code": "Kod oluşturulduktan sonra değiştirilemez."})
        return super().update(**kwargs)


class ImmutableCodeModel(models.Model):
    objects = ImmutableCodeQuerySet.as_manager()

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        self.code = self.code.strip()

        if not self._state.adding:
            original_code = (
                type(self).objects.filter(pk=self.pk).values_list("code", flat=True).first()
            )
            if original_code is not None and self.code != original_code:
                raise ValidationError(
                    {"code": "Kod oluşturulduktan sonra değiştirilemez."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Topic(ImmutableCodeModel):
    code = models.CharField("konu kodu", max_length=30, unique=True)
    name = models.CharField("konu adı", max_length=200)
    description = models.TextField("açıklama", blank=True)
    created_at = models.DateTimeField("oluşturulma zamanı", auto_now_add=True)
    updated_at = models.DateTimeField("güncellenme zamanı", auto_now=True)

    class Meta:
        verbose_name = "konu"
        verbose_name_plural = "konular"
        ordering = ("code",)
        constraints = [
            models.CheckConstraint(
                condition=~Q(code=""),
                name="topic_code_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(name=""),
                name="topic_name_not_empty",
            ),
        ]

    def clean(self):
        super().clean()
        self.name = self.name.strip()

    def __str__(self):
        return f"{self.code} — {self.name}"


class LearningOutcome(ImmutableCodeModel):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.PROTECT,
        related_name="learning_outcomes",
        verbose_name="konu",
    )
    code = models.CharField("MEB kazanım kodu", max_length=30, unique=True)
    description = models.TextField("kazanım açıklaması")
    created_at = models.DateTimeField("oluşturulma zamanı", auto_now_add=True)
    updated_at = models.DateTimeField("güncellenme zamanı", auto_now=True)

    class Meta:
        verbose_name = "kazanım"
        verbose_name_plural = "kazanımlar"
        ordering = ("code",)
        constraints = [
            models.CheckConstraint(
                condition=~Q(code=""),
                name="learning_outcome_code_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(description=""),
                name="learning_outcome_description_not_empty",
            ),
        ]

    def clean(self):
        super().clean()
        self.description = self.description.strip()

    def __str__(self):
        return f"{self.code} — {self.description}"


class QuestionCodeCounter(models.Model):
    last_value = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "soru kodu sayacı"
        verbose_name_plural = "soru kodu sayaçları"


class QuestionTypeCodeCounter(models.Model):
    last_value = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "soru tipi kodu sayacı"
        verbose_name_plural = "soru tipi kodu sayaçları"


class QuestionType(ImmutableCodeModel):
    code = models.CharField(
        "soru tipi kodu",
        max_length=6,
        unique=True,
        editable=False,
        blank=True,
    )
    name = models.CharField("ad", max_length=200, unique=True)
    short_description = models.TextField("kısa açıklama")
    solution_method = models.TextField("çözüm yöntemi veya işlem adımları")
    classification_criteria = models.TextField("ayırt edici sınıflandırma ölçütleri")
    example_questions = models.ManyToManyField(
        "Question",
        blank=True,
        related_name="example_for_question_types",
        verbose_name="örnek sorular",
    )
    created_at = models.DateTimeField("oluşturulma zamanı", auto_now_add=True)
    updated_at = models.DateTimeField("güncellenme zamanı", auto_now=True)

    class Meta:
        verbose_name = "soru tipi"
        verbose_name_plural = "soru tipleri"
        ordering = ("code",)
        constraints = [
            models.CheckConstraint(
                condition=~Q(code=""),
                name="question_type_code_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(name=""),
                name="question_type_name_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(short_description=""),
                name="question_type_short_description_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(solution_method=""),
                name="question_type_solution_method_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(classification_criteria=""),
                name="question_type_classification_criteria_not_empty",
            ),
        ]

    def clean(self):
        super().clean()
        for field_name in (
            "name",
            "short_description",
            "solution_method",
            "classification_criteria",
        ):
            value = getattr(self, field_name)
            if value is not None:
                setattr(self, field_name, value.strip())

    def validate_for_use(self):
        self.full_clean()
        if not self.pk or not self.example_questions.exists():
            raise ValidationError(
                {"example_questions": "En az bir örnek soru seçilmelidir."}
            )

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.code:
                raise ValidationError(
                    {"code": "Soru tipi kodu sistem tarafından otomatik oluşturulur."}
                )

            self.full_clean(exclude={"code"})
            with transaction.atomic():
                counter = QuestionTypeCodeCounter.objects.select_for_update().get(pk=1)
                next_value = counter.last_value + 1
                if next_value > 9999:
                    raise ValidationError(
                        {"code": "Kullanılabilir soru tipi kodu kalmadı."}
                    )
                counter.last_value = next_value
                counter.save(update_fields=("last_value",))
                self.code = f"QT{next_value:04d}"
                return models.Model.save(self, *args, **kwargs)

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} — {self.name}"


class Question(ImmutableCodeModel):
    class CorrectAnswer(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"

    code = models.CharField(
        "soru kodu",
        max_length=7,
        unique=True,
        editable=False,
        blank=True,
    )
    original_image = models.ImageField(
        "orijinal soru görseli",
        upload_to="questions/originals/%Y/%m/",
    )
    image_hash = models.CharField(
        "görsel özeti",
        max_length=64,
        blank=True,
        editable=False,
        db_index=True,
    )
    question_text = models.TextField("LaTeX soru metni")
    choice_a = models.TextField("LaTeX A şıkkı")
    choice_b = models.TextField("LaTeX B şıkkı")
    choice_c = models.TextField("LaTeX C şıkkı")
    choice_d = models.TextField("LaTeX D şıkkı")
    correct_answer = models.CharField(
        "doğru cevap",
        max_length=1,
        choices=CorrectAnswer.choices,
    )
    primary_topic = models.ForeignKey(
        Topic,
        on_delete=models.PROTECT,
        related_name="primary_questions",
        verbose_name="ana konu",
    )
    secondary_topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name="secondary_questions",
        verbose_name="ikincil konular",
    )
    learning_outcomes = models.ManyToManyField(
        LearningOutcome,
        related_name="questions",
        verbose_name="kazanımlar",
    )
    question_type = models.ForeignKey(
        QuestionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
        verbose_name="soru tipi",
    )
    difficulty = models.PositiveSmallIntegerField(
        "zorluk düzeyi",
        null=True,
        blank=True,
        validators=(MinValueValidator(1), MaxValueValidator(5)),
    )
    solution = models.TextField("çözüm", blank=True)
    source_pdf_name = models.CharField("kaynak PDF adı", max_length=255)
    source_page_number = models.PositiveIntegerField(
        "kaynak sayfa numarası",
        validators=(MinValueValidator(1),),
    )
    source_question_number = models.CharField(
        "kaynak soru numarası",
        max_length=50,
    )
    created_at = models.DateTimeField("oluşturulma zamanı", auto_now_add=True)
    updated_at = models.DateTimeField("güncellenme zamanı", auto_now=True)
    archived_at = models.DateTimeField("arşivlenme zamanı", null=True, blank=True)

    class Meta:
        verbose_name = "soru"
        verbose_name_plural = "sorular"
        ordering = ("code",)
        constraints = [
            models.CheckConstraint(
                condition=~Q(code=""),
                name="question_code_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(original_image=""),
                name="question_original_image_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(question_text=""),
                name="question_text_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(choice_a=""),
                name="question_choice_a_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(choice_b=""),
                name="question_choice_b_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(choice_c=""),
                name="question_choice_c_not_empty",
            ),
            models.CheckConstraint(
                condition=~Q(choice_d=""),
                name="question_choice_d_not_empty",
            ),
            models.CheckConstraint(
                condition=Q(correct_answer__in=("A", "B", "C", "D")),
                name="question_correct_answer_valid",
            ),
            models.CheckConstraint(
                condition=Q(difficulty__isnull=True)
                | Q(difficulty__gte=1, difficulty__lte=5),
                name="question_difficulty_valid",
            ),
            models.CheckConstraint(
                condition=~Q(source_pdf_name=""),
                name="question_source_pdf_name_not_empty",
            ),
            models.CheckConstraint(
                condition=Q(source_page_number__gte=1),
                name="question_source_page_number_positive",
            ),
            models.CheckConstraint(
                condition=~Q(source_question_number=""),
                name="question_source_question_number_not_empty",
            ),
        ]

    def clean(self):
        super().clean()
        for field_name in (
            "question_text",
            "choice_a",
            "choice_b",
            "choice_c",
            "choice_d",
            "solution",
            "source_pdf_name",
            "source_question_number",
        ):
            value = getattr(self, field_name)
            if value is not None:
                setattr(self, field_name, value.strip())

        if self.pk:
            self._validate_classification()

    def _validate_classification(self):
        errors = {}
        secondary_topic_ids = set(self.secondary_topics.values_list("pk", flat=True))

        if self.primary_topic_id in secondary_topic_ids:
            errors["secondary_topics"] = "Ana konu ikincil konu olarak seçilemez."

        allowed_topic_ids = secondary_topic_ids | {self.primary_topic_id}
        invalid_outcome_codes = list(
            self.learning_outcomes.exclude(topic_id__in=allowed_topic_ids).values_list(
                "code", flat=True
            )
        )
        if invalid_outcome_codes:
            errors["learning_outcomes"] = (
                "Kazanımlar yalnızca ana veya ikincil konulara bağlı olabilir: "
                + ", ".join(invalid_outcome_codes)
            )

        if errors:
            raise ValidationError(errors)

    @property
    def is_question_type_pending(self):
        return self.question_type_id is None

    @property
    def is_difficulty_pending(self):
        return self.difficulty is None

    @property
    def is_solution_pending(self):
        return not bool(self.solution.strip())

    @property
    def pending_statuses(self):
        statuses = []
        if self.is_question_type_pending:
            statuses.append("question_type")
        if self.is_difficulty_pending:
            statuses.append("difficulty")
        if self.is_solution_pending:
            statuses.append("solution")
        return tuple(statuses)

    @property
    def is_complete(self):
        return not self.pending_statuses

    @property
    def is_archived(self):
        return self.archived_at is not None

    def archive(self):
        if not self.archived_at:
            self.archived_at = timezone.now()
            self.save(update_fields=("archived_at", "updated_at"))

    def restore(self):
        if self.archived_at:
            self.archived_at = None
            self.save(update_fields=("archived_at", "updated_at"))

    def validate_for_pool(self):
        self.full_clean()
        errors = {}

        if not self.pk:
            errors["learning_outcomes"] = (
                "Soru havuza alınmadan önce kaydedilmeli ve kazanımı seçilmelidir."
            )
        elif not self.learning_outcomes.exists():
            errors["learning_outcomes"] = "En az bir kazanım seçilmelidir."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        image_is_new = self.original_image and (
            not self.image_hash
            or not getattr(self.original_image, "_committed", True)
        )
        old_image = None
        if image_is_new and not self._state.adding:
            old_image = (
                type(self).objects.only("original_image").get(pk=self.pk).original_image
            )
        if image_is_new:
            try:
                self.image_hash = calculate_file_hash(self.original_image)
            except (FileNotFoundError, OSError) as exc:
                raise ValidationError(
                    {"original_image": "Soru görseli okunamadı."}
                ) from exc

        if self._state.adding:
            if self.code:
                raise ValidationError(
                    {"code": "Soru kodu sistem tarafından otomatik oluşturulur."}
                )

            self.full_clean(exclude={"code"})
            with transaction.atomic():
                counter = QuestionCodeCounter.objects.select_for_update().get(pk=1)
                next_value = counter.last_value + 1
                if next_value > 999999:
                    raise ValidationError(
                        {"code": "Kullanılabilir soru kodu kalmadı."}
                    )
                counter.last_value = next_value
                counter.save(update_fields=("last_value",))
                self.code = f"Q{next_value:06d}"
                return models.Model.save(self, *args, **kwargs)

        result = super().save(*args, **kwargs)
        if old_image and old_image.name != self.original_image.name:
            old_image.delete(save=False)
        return result

    def __str__(self):
        return self.code
