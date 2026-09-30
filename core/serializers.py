from rest_framework import serializers

from .models import LearningOutcome, Question, QuestionType, Topic


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ("code", "name")


class LearningOutcomeSerializer(serializers.ModelSerializer):
    topic = serializers.CharField(source="topic.code", read_only=True)

    class Meta:
        model = LearningOutcome
        fields = ("code", "description", "topic")


class QuestionTypeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ("code", "name", "short_description")


class StudentQuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()
    primary_topic = TopicSerializer(read_only=True)
    secondary_topics = TopicSerializer(many=True, read_only=True)
    learning_outcomes = LearningOutcomeSerializer(many=True, read_only=True)
    question_type = QuestionTypeSummarySerializer(read_only=True)
    source = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "code",
            "original_image",
            "question_text",
            "choices",
            "primary_topic",
            "secondary_topics",
            "learning_outcomes",
            "question_type",
            "difficulty",
            "source",
        )

    def get_choices(self, obj):
        return {
            "A": obj.choice_a,
            "B": obj.choice_b,
            "C": obj.choice_c,
            "D": obj.choice_d,
        }

    def get_source(self, obj):
        return {
            "pdf_name": obj.source_pdf_name,
            "page_number": obj.source_page_number,
            "question_number": obj.source_question_number,
        }


class ServerQuestionSerializer(StudentQuestionSerializer):
    class Meta(StudentQuestionSerializer.Meta):
        fields = StudentQuestionSerializer.Meta.fields + (
            "correct_answer",
            "solution",
            "archived_at",
        )
