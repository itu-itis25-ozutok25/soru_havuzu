from django.contrib import admin
from django import forms

from .forms import QuestionForm
from .models import LearningOutcome, Question, QuestionType, Topic


class LearningOutcomeInline(admin.TabularInline):
    model = LearningOutcome
    extra = 0
    fields = ("code", "description")
    show_change_link = True


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "updated_at")
    search_fields = ("code", "name", "description")
    readonly_fields = ("created_at", "updated_at")
    inlines = (LearningOutcomeInline,)


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ("code", "topic", "updated_at")
    list_filter = ("topic",)
    search_fields = ("code", "description", "topic__code", "topic__name")
    autocomplete_fields = ("topic",)
    readonly_fields = ("created_at", "updated_at")


class QuestionTypeAdminForm(forms.ModelForm):
    class Meta:
        model = QuestionType
        fields = "__all__"

    def clean_example_questions(self):
        example_questions = self.cleaned_data["example_questions"]
        if not example_questions:
            raise forms.ValidationError("En az bir örnek soru seçilmelidir.")
        return example_questions


@admin.register(QuestionType)
class QuestionTypeAdmin(admin.ModelAdmin):
    form = QuestionTypeAdminForm
    list_display = ("code", "name", "updated_at")
    search_fields = (
        "code",
        "name",
        "short_description",
        "solution_method",
        "classification_criteria",
    )
    filter_horizontal = ("example_questions",)
    readonly_fields = ("code", "created_at", "updated_at")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    list_display = (
        "code",
        "primary_topic",
        "question_type",
        "difficulty",
        "completion_status",
        "correct_answer",
        "source_pdf_name",
        "source_question_number",
        "updated_at",
    )
    list_filter = ("primary_topic", "question_type", "difficulty", "correct_answer")
    search_fields = (
        "code",
        "question_text",
        "source_pdf_name",
        "source_question_number",
    )
    filter_horizontal = ("secondary_topics", "learning_outcomes")
    readonly_fields = ("code", "created_at", "updated_at")

    @admin.display(description="durum")
    def completion_status(self, obj):
        if obj.is_complete:
            return "Tamamlandı"

        labels = {
            "question_type": "Soru tipi bekliyor",
            "difficulty": "Zorluk bekliyor",
            "solution": "Çözüm bekliyor",
        }
        return ", ".join(labels[status] for status in obj.pending_statuses)
