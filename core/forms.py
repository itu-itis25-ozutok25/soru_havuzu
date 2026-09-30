from django import forms

from .models import LearningOutcome, Question, QuestionType, Topic, calculate_file_hash


class QuestionFilterForm(forms.Form):
    OUTCOME_MATCH_CHOICES = (
        ("any", "Herhangi birini içerir"),
        ("all", "Tamamını içerir"),
    )
    STATUS_CHOICES = (
        ("", "Tüm durumlar"),
        ("question_type_pending", "Soru tipi bekliyor"),
        ("difficulty_pending", "Zorluk bekliyor"),
        ("solution_pending", "Çözüm bekliyor"),
        ("completed", "Tamamlananlar"),
    )
    DIFFICULTY_CHOICES = (("", "Tümü"),) + tuple(
        (str(value), str(value)) for value in range(1, 6)
    )

    q = forms.CharField(
        required=False,
        label="Kod veya soru metni",
        widget=forms.TextInput(attrs={"placeholder": "Q000001 veya soru metni"}),
    )
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        required=False,
        label="Konular",
    )
    outcomes = forms.ModelMultipleChoiceField(
        queryset=LearningOutcome.objects.select_related("topic"),
        required=False,
        label="Kazanımlar",
    )
    outcome_match = forms.ChoiceField(
        choices=OUTCOME_MATCH_CHOICES,
        required=False,
        initial="any",
        label="Kazanım eşleşmesi",
    )
    question_type = forms.ModelChoiceField(
        queryset=QuestionType.objects.all(),
        required=False,
        label="Soru tipi",
        empty_label="Tümü",
    )
    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        required=False,
        label="Zorluk",
    )
    source_pdf = forms.CharField(
        required=False,
        label="Kaynak PDF",
        widget=forms.TextInput(attrs={"placeholder": "Dosya adında ara"}),
    )
    source_question_number = forms.CharField(
        required=False,
        label="Kaynak soru no",
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label="Tamamlanma durumu",
    )


class QuestionForm(forms.ModelForm):
    allow_duplicate_image = forms.BooleanField(
        required=False,
        label="Aynı görsele rağmen kaydet",
        help_text="Yalnızca tekrar uyarısını kontrol ettikten sonra işaretleyin.",
    )

    class Meta:
        model = Question
        fields = (
            "original_image",
            "primary_topic",
            "secondary_topics",
            "learning_outcomes",
            "question_text",
            "choice_a",
            "choice_b",
            "choice_c",
            "choice_d",
            "correct_answer",
            "source_pdf_name",
            "source_page_number",
            "source_question_number",
            "question_type",
            "difficulty",
            "solution",
        )
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 5}),
            "choice_a": forms.Textarea(attrs={"rows": 2}),
            "choice_b": forms.Textarea(attrs={"rows": 2}),
            "choice_c": forms.Textarea(attrs={"rows": 2}),
            "choice_d": forms.Textarea(attrs={"rows": 2}),
            "solution": forms.Textarea(attrs={"rows": 6}),
            "secondary_topics": forms.CheckboxSelectMultiple(),
            "learning_outcomes": forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        primary_topic = cleaned_data.get("primary_topic")
        secondary_topics = cleaned_data.get("secondary_topics")
        learning_outcomes = cleaned_data.get("learning_outcomes")

        if primary_topic and secondary_topics is not None:
            secondary_topic_ids = {topic.pk for topic in secondary_topics}
            if primary_topic.pk in secondary_topic_ids:
                self.add_error(
                    "secondary_topics",
                    "Ana konu ikincil konu olarak seçilemez.",
                )

            if learning_outcomes is not None:
                allowed_topic_ids = secondary_topic_ids | {primary_topic.pk}
                invalid_outcomes = [
                    outcome.code
                    for outcome in learning_outcomes
                    if outcome.topic_id not in allowed_topic_ids
                ]
                if invalid_outcomes:
                    self.add_error(
                        "learning_outcomes",
                        "Kazanımlar yalnızca ana veya ikincil konulara bağlı "
                        "olabilir: "
                        + ", ".join(invalid_outcomes),
                    )

        image = cleaned_data.get("original_image")
        image_is_new = image and not getattr(image, "_committed", False)
        if image_is_new:
            image_hash = calculate_file_hash(image)
            duplicate_codes = list(
                Question.objects.filter(image_hash=image_hash)
                .exclude(pk=self.instance.pk)
                .values_list("code", flat=True)
            )
            if duplicate_codes and not cleaned_data.get("allow_duplicate_image"):
                self.add_error(
                    "original_image",
                    "Bu görsel daha önce yüklendi: "
                    + ", ".join(duplicate_codes)
                    + ". Kaydetmek istiyorsanız tekrar onayını işaretleyin.",
                )

        return cleaned_data


class QuestionSolutionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("solution",)
        widgets = {"solution": forms.Textarea(attrs={"rows": 10})}
