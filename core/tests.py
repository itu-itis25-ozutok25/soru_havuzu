import base64
import hashlib
from io import StringIO

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token

from .api_permissions import API_SERVER_GROUP, API_STUDENT_GROUP
from .models import LearningOutcome, Question, QuestionType, Topic


TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}
TEST_IMAGE_BYTES = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
)


def test_image(name="question.gif"):
    return SimpleUploadedFile(name, TEST_IMAGE_BYTES, content_type="image/gif")


class FoundationEndpointTests(SimpleTestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "soru-havuzu",
            },
        )

    def test_api_v1_root(self):
        response = self.client.get(reverse("api-v1:root"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["version"], "v1")


class TopicAndLearningOutcomeModelTests(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(
            code="T001",
            name="Çarpanlar ve Katlar",
        )

    def test_learning_outcome_belongs_to_topic(self):
        outcome = LearningOutcome.objects.create(
            topic=self.topic,
            code="M.8.1.1.1",
            description="Verilen pozitif tam sayıların çarpanlarını bulur.",
        )

        self.assertEqual(outcome.topic, self.topic)
        self.assertSequenceEqual(self.topic.learning_outcomes.all(), [outcome])

    def test_codes_are_unique(self):
        with self.assertRaises(ValidationError):
            Topic.objects.create(code="T001", name="Başka konu")

        LearningOutcome.objects.create(
            topic=self.topic,
            code="M.8.1.1.1",
            description="Birinci kazanım",
        )
        with self.assertRaises(ValidationError):
            LearningOutcome.objects.create(
                topic=self.topic,
                code="M.8.1.1.1",
                description="Tekrarlanan kazanım",
            )

    def test_codes_cannot_be_changed(self):
        self.topic.code = "T002"

        with self.assertRaisesMessage(
            ValidationError,
            "Kod oluşturulduktan sonra değiştirilemez.",
        ):
            self.topic.save()

        with self.assertRaises(ValidationError):
            Topic.objects.filter(pk=self.topic.pk).update(code="T002")

    def test_blank_values_are_rejected(self):
        with self.assertRaises(ValidationError):
            Topic.objects.create(code="   ", name="Geçersiz konu")

        with self.assertRaises(ValidationError):
            LearningOutcome.objects.create(
                topic=self.topic,
                code="M.8.1.1.2",
                description="   ",
            )

    def test_database_rejects_empty_topic_name(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Topic.objects.filter(pk=self.topic.pk).update(name="")

    def test_topic_with_learning_outcome_is_protected_from_deletion(self):
        LearningOutcome.objects.create(
            topic=self.topic,
            code="M.8.1.1.1",
            description="Bir kazanım",
        )

        with self.assertRaises(ProtectedError):
            self.topic.delete()

    def test_models_are_registered_in_admin(self):
        self.assertIn(Topic, admin.site._registry)
        self.assertIn(LearningOutcome, admin.site._registry)


@override_settings(STORAGES=TEST_STORAGES)
class QuestionModelTests(TestCase):
    def setUp(self):
        self.primary_topic = Topic.objects.create(
            code="T001",
            name="Çarpanlar ve Katlar",
        )
        self.primary_outcome = LearningOutcome.objects.create(
            topic=self.primary_topic,
            code="M.8.1.1.1",
            description="Pozitif tam sayıların çarpanlarını bulur.",
        )

    def create_question(self, **overrides):
        values = {
            "original_image": test_image(),
            "question_text": r"$24$ sayısının pozitif çarpan sayısı kaçtır?",
            "choice_a": r"$4$",
            "choice_b": r"$6$",
            "choice_c": r"$8$",
            "choice_d": r"$10$",
            "correct_answer": Question.CorrectAnswer.C,
            "primary_topic": self.primary_topic,
            "source_pdf_name": "ornek-sorular.pdf",
            "source_page_number": 3,
            "source_question_number": "12",
        }
        values.update(overrides)
        return Question.objects.create(**values)

    def test_question_code_is_generated_sequentially(self):
        first_question = self.create_question()
        second_question = self.create_question(source_question_number="13")

        self.assertEqual(first_question.code, "Q000001")
        self.assertEqual(second_question.code, "Q000002")

    def test_deleted_question_code_is_not_reused(self):
        first_question = self.create_question()
        first_question.delete()

        second_question = self.create_question(source_question_number="13")

        self.assertEqual(second_question.code, "Q000002")

    def test_question_code_cannot_be_supplied_or_changed(self):
        with self.assertRaises(ValidationError):
            self.create_question(code="Q123456")

        question = self.create_question()
        question.code = "Q123456"
        with self.assertRaises(ValidationError):
            question.save()

        with self.assertRaises(ValidationError):
            Question.objects.filter(pk=question.pk).update(code="Q123456")

    def test_question_supports_secondary_topics_and_multiple_outcomes(self):
        secondary_topic = Topic.objects.create(code="T002", name="Üslü İfadeler")
        secondary_outcome = LearningOutcome.objects.create(
            topic=secondary_topic,
            code="M.8.1.2.1",
            description="Tam sayıların kuvvetlerini hesaplar.",
        )
        question = self.create_question()

        question.secondary_topics.add(secondary_topic)
        question.learning_outcomes.add(self.primary_outcome, secondary_outcome)

        self.assertSequenceEqual(
            question.secondary_topics.all(),
            [secondary_topic],
        )
        self.assertSetEqual(
            set(question.learning_outcomes.all()),
            {self.primary_outcome, secondary_outcome},
        )
        question.validate_for_pool()

    def test_primary_topic_cannot_also_be_secondary(self):
        question = self.create_question()

        with self.assertRaises(ValidationError):
            question.secondary_topics.add(self.primary_topic)

    def test_outcome_must_belong_to_a_selected_topic(self):
        unrelated_topic = Topic.objects.create(code="T002", name="Üslü İfadeler")
        unrelated_outcome = LearningOutcome.objects.create(
            topic=unrelated_topic,
            code="M.8.1.2.1",
            description="Tam sayıların kuvvetlerini hesaplar.",
        )
        question = self.create_question()

        with self.assertRaises(ValidationError):
            question.learning_outcomes.add(unrelated_outcome)

    def test_secondary_topic_cannot_be_removed_while_its_outcome_is_selected(self):
        secondary_topic = Topic.objects.create(code="T002", name="Üslü İfadeler")
        secondary_outcome = LearningOutcome.objects.create(
            topic=secondary_topic,
            code="M.8.1.2.1",
            description="Tam sayıların kuvvetlerini hesaplar.",
        )
        question = self.create_question()
        question.secondary_topics.add(secondary_topic)
        question.learning_outcomes.add(secondary_outcome)

        with self.assertRaises(ValidationError):
            question.secondary_topics.remove(secondary_topic)

    def test_primary_topic_change_cannot_invalidate_outcomes(self):
        other_topic = Topic.objects.create(code="T002", name="Üslü İfadeler")
        question = self.create_question()
        question.learning_outcomes.add(self.primary_outcome)
        question.primary_topic = other_topic

        with self.assertRaises(ValidationError):
            question.save()

    def test_pool_validation_requires_at_least_one_outcome(self):
        question = self.create_question()

        with self.assertRaises(ValidationError):
            question.validate_for_pool()

        question.learning_outcomes.add(self.primary_outcome)
        question.validate_for_pool()

    def test_required_question_fields_are_validated(self):
        with self.assertRaises(ValidationError):
            self.create_question(question_text="   ")

        with self.assertRaises(ValidationError):
            self.create_question(source_page_number=0)

        with self.assertRaises(ValidationError):
            self.create_question(original_image="")

    def test_database_rejects_invalid_correct_answer(self):
        question = self.create_question()

        with self.assertRaises(IntegrityError), transaction.atomic():
            Question.objects.filter(pk=question.pk).update(correct_answer="E")

    def test_database_rejects_empty_original_image(self):
        question = self.create_question()

        with self.assertRaises(IntegrityError), transaction.atomic():
            Question.objects.filter(pk=question.pk).update(original_image="")

    def test_new_question_starts_with_all_optional_fields_pending(self):
        question = self.create_question()

        self.assertTrue(question.is_question_type_pending)
        self.assertTrue(question.is_difficulty_pending)
        self.assertTrue(question.is_solution_pending)
        self.assertEqual(
            question.pending_statuses,
            ("question_type", "difficulty", "solution"),
        )
        self.assertFalse(question.is_complete)

    def test_question_is_complete_when_optional_fields_are_filled(self):
        question = self.create_question()
        question_type = QuestionType.objects.create(
            name="Doğrudan işlem",
            short_description="Tek işlemle çözülen soru.",
            solution_method="Verilen işlemi uygula.",
            classification_criteria="Ek yorum gerektirmez.",
        )
        question_type.example_questions.add(question)
        question.question_type = question_type
        question.difficulty = 3
        question.solution = r"$24=2^3\cdot3$ olduğundan cevap $8$'dir."
        question.save()

        self.assertEqual(question.pending_statuses, ())
        self.assertTrue(question.is_complete)

    def test_difficulty_must_be_between_one_and_five(self):
        with self.assertRaises(ValidationError):
            self.create_question(difficulty=0)

        question = self.create_question()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Question.objects.filter(pk=question.pk).update(difficulty=6)

    def test_question_is_registered_in_admin(self):
        self.assertIn(Question, admin.site._registry)


@override_settings(STORAGES=TEST_STORAGES)
class QuestionTypeModelTests(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(code="T001", name="Çarpanlar ve Katlar")
        self.outcome = LearningOutcome.objects.create(
            topic=self.topic,
            code="M.8.1.1.1",
            description="Pozitif tam sayıların çarpanlarını bulur.",
        )

    def create_question(self):
        question = Question.objects.create(
            original_image=test_image(),
            question_text="Örnek soru",
            choice_a="1",
            choice_b="2",
            choice_c="3",
            choice_d="4",
            correct_answer=Question.CorrectAnswer.A,
            primary_topic=self.topic,
            source_pdf_name="ornek.pdf",
            source_page_number=1,
            source_question_number="1",
        )
        question.learning_outcomes.add(self.outcome)
        return question

    def create_question_type(self, **overrides):
        values = {
            "name": "Doğrudan işlem",
            "short_description": "Tek işlemle çözülen soru.",
            "solution_method": "Verilen işlemi uygula.",
            "classification_criteria": "Ek yorum gerektirmez.",
        }
        values.update(overrides)
        return QuestionType.objects.create(**values)

    def test_question_type_code_is_generated_sequentially(self):
        first_type = self.create_question_type()
        second_type = self.create_question_type(name="Tablo yorumlama")

        self.assertEqual(first_type.code, "QT0001")
        self.assertEqual(second_type.code, "QT0002")

    def test_deleted_question_type_code_is_not_reused(self):
        first_type = self.create_question_type()
        first_type.delete()

        second_type = self.create_question_type(name="Tablo yorumlama")

        self.assertEqual(second_type.code, "QT0002")

    def test_question_type_code_cannot_be_supplied_or_changed(self):
        with self.assertRaises(ValidationError):
            self.create_question_type(code="QT9999")

        question_type = self.create_question_type()
        question_type.code = "QT9999"
        with self.assertRaises(ValidationError):
            question_type.save()

        with self.assertRaises(ValidationError):
            QuestionType.objects.filter(pk=question_type.pk).update(code="QT9999")

    def test_question_type_requires_descriptive_fields(self):
        with self.assertRaises(ValidationError):
            self.create_question_type(short_description="   ")

        with self.assertRaises(ValidationError):
            self.create_question_type(solution_method="")

        with self.assertRaises(ValidationError):
            self.create_question_type(classification_criteria="")

    def test_question_type_requires_example_before_use(self):
        question_type = self.create_question_type()

        with self.assertRaises(ValidationError):
            question_type.validate_for_use()

        question_type.example_questions.add(self.create_question())
        question_type.validate_for_use()

    def test_deleting_question_type_returns_question_to_pending_status(self):
        question_type = self.create_question_type()
        question = self.create_question()
        question_type.example_questions.add(question)
        question.question_type = question_type
        question.save()

        question_type.delete()
        question.refresh_from_db()

        self.assertIsNone(question.question_type)
        self.assertTrue(question.is_question_type_pending)

    def test_question_type_is_registered_in_admin(self):
        self.assertIn(QuestionType, admin.site._registry)


@override_settings(STORAGES=TEST_STORAGES)
class QuestionManagementViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="yonetici",
            password="test-parolasi",
        )
        self.topic = Topic.objects.create(code="T001", name="Çarpanlar ve Katlar")
        self.outcome = LearningOutcome.objects.create(
            topic=self.topic,
            code="M.8.1.1.1",
            description="Pozitif tam sayıların çarpanlarını bulur.",
        )

    def question_form_data(self, **overrides):
        values = {
            "primary_topic": self.topic.pk,
            "learning_outcomes": [self.outcome.pk],
            "question_text": r"$24$ sayısının pozitif çarpan sayısı kaçtır?",
            "choice_a": "4",
            "choice_b": "6",
            "choice_c": "8",
            "choice_d": "10",
            "correct_answer": "C",
            "source_pdf_name": "ornek.pdf",
            "source_page_number": 3,
            "source_question_number": "12",
        }
        values.update(overrides)
        return values

    def create_question(
        self,
        image_name="question.gif",
        outcomes=None,
        secondary_topics=None,
        **overrides,
    ):
        values = {
            "original_image": test_image(image_name),
            "question_text": "Örnek soru",
            "choice_a": "1",
            "choice_b": "2",
            "choice_c": "3",
            "choice_d": "4",
            "correct_answer": "A",
            "primary_topic": self.topic,
            "source_pdf_name": "ornek.pdf",
            "source_page_number": 1,
            "source_question_number": "1",
        }
        values.update(overrides)
        question = Question.objects.create(**values)
        if secondary_topics:
            question.secondary_topics.add(*secondary_topics)
        question.learning_outcomes.add(*(outcomes or [self.outcome]))
        return question

    def test_question_pages_require_login(self):
        response = self.client.get(reverse("question-list"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('question-list')}",
        )

    def test_authenticated_user_can_create_and_view_question(self):
        self.client.force_login(self.user)
        data = self.question_form_data(original_image=test_image())

        response = self.client.post(reverse("question-create"), data)

        question = Question.objects.get()
        self.assertRedirects(
            response,
            reverse("question-detail", kwargs={"code": question.code}),
        )
        self.assertEqual(
            question.image_hash,
            hashlib.sha256(TEST_IMAGE_BYTES).hexdigest(),
        )
        detail_response = self.client.get(
            reverse("question-detail", kwargs={"code": question.code})
        )
        self.assertContains(detail_response, question.code)
        self.assertContains(detail_response, "Çarpanlar ve Katlar")

    def test_duplicate_image_requires_explicit_confirmation(self):
        self.client.force_login(self.user)
        self.create_question("original.gif")
        data = self.question_form_data(
            original_image=test_image("duplicate.gif"),
            source_question_number="2",
        )

        response = self.client.post(reverse("question-create"), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bu görsel daha önce yüklendi")
        self.assertEqual(Question.objects.count(), 1)

        data["original_image"] = test_image("duplicate-confirmed.gif")
        data["allow_duplicate_image"] = "on"
        response = self.client.post(reverse("question-create"), data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 2)

    def test_question_can_be_edited(self):
        self.client.force_login(self.user)
        question = self.create_question()
        data = self.question_form_data(question_text="Güncellenmiş soru")

        response = self.client.post(
            reverse("question-update", kwargs={"code": question.code}),
            data,
        )

        self.assertRedirects(
            response,
            reverse("question-detail", kwargs={"code": question.code}),
        )
        question.refresh_from_db()
        self.assertEqual(question.question_text, "Güncellenmiş soru")

    def test_replacing_image_removes_old_file(self):
        self.client.force_login(self.user)
        question = self.create_question("old.gif")
        old_image_name = question.original_image.name
        storage = question.original_image.storage
        data = self.question_form_data(original_image=test_image("new.gif"))

        response = self.client.post(
            reverse("question-update", kwargs={"code": question.code}),
            data,
        )

        self.assertEqual(response.status_code, 302)
        question.refresh_from_db()
        self.assertNotEqual(question.original_image.name, old_image_name)
        self.assertFalse(storage.exists(old_image_name))
        self.assertTrue(storage.exists(question.original_image.name))

    def test_solution_can_be_updated_separately(self):
        self.client.force_login(self.user)
        question = self.create_question()

        response = self.client.post(
            reverse("question-solution", kwargs={"code": question.code}),
            {"solution": r"$24=2^3\cdot3$"},
        )

        self.assertRedirects(
            response,
            reverse("question-detail", kwargs={"code": question.code}),
        )
        question.refresh_from_db()
        self.assertEqual(question.solution, r"$24=2^3\cdot3$")
        self.assertFalse(question.is_solution_pending)

    def test_question_can_be_archived_and_restored(self):
        self.client.force_login(self.user)
        question = self.create_question()

        self.client.post(reverse("question-archive", kwargs={"code": question.code}))
        question.refresh_from_db()
        self.assertTrue(question.is_archived)
        active_response = self.client.get(reverse("question-list"))
        archived_response = self.client.get(reverse("question-list") + "?state=archived")
        self.assertNotIn(question, active_response.context["questions"])
        self.assertIn(question, archived_response.context["questions"])

        self.client.post(reverse("question-restore", kwargs={"code": question.code}))
        question.refresh_from_db()
        self.assertFalse(question.is_archived)

    def test_permanent_delete_removes_record_and_image(self):
        self.client.force_login(self.user)
        question = self.create_question()
        image_name = question.original_image.name
        storage = question.original_image.storage
        self.assertTrue(storage.exists(image_name))

        response = self.client.post(
            reverse("question-delete", kwargs={"code": question.code})
        )

        self.assertRedirects(response, reverse("question-list"))
        self.assertFalse(Question.objects.filter(code=question.code).exists())
        self.assertFalse(storage.exists(image_name))

    def test_delete_confirmation_does_not_delete_on_get(self):
        self.client.force_login(self.user)
        question = self.create_question()

        response = self.client.get(
            reverse("question-delete", kwargs={"code": question.code})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Question.objects.filter(pk=question.pk).exists())

    def test_searches_by_code_question_text_and_source(self):
        self.client.force_login(self.user)
        first = self.create_question(
            "first.gif",
            question_text="Asal çarpanlara ayırma sorusu",
            source_pdf_name="deneme-bir.pdf",
            source_question_number="17",
        )
        second = self.create_question(
            "second.gif",
            question_text="EBOB sorusu",
            source_pdf_name="deneme-iki.pdf",
            source_question_number="22",
        )

        response = self.client.get(reverse("question-list"), {"q": first.code})
        self.assertSequenceEqual(list(response.context["questions"]), [first])

        response = self.client.get(reverse("question-list"), {"q": "EBOB"})
        self.assertSequenceEqual(list(response.context["questions"]), [second])

        response = self.client.get(
            reverse("question-list"),
            {"source_pdf": "deneme-bir", "source_question_number": "17"},
        )
        self.assertSequenceEqual(list(response.context["questions"]), [first])

    def test_topic_filter_matches_primary_and_secondary_topics(self):
        self.client.force_login(self.user)
        second_topic = Topic.objects.create(code="T002", name="Üslü İfadeler")
        second_outcome = LearningOutcome.objects.create(
            topic=second_topic,
            code="M.8.1.2.1",
            description="Tam sayıların kuvvetlerini hesaplar.",
        )
        primary_match = self.create_question(
            "primary.gif",
            primary_topic=second_topic,
            outcomes=[second_outcome],
            source_question_number="2",
        )
        secondary_match = self.create_question(
            "secondary.gif",
            secondary_topics=[second_topic],
            outcomes=[self.outcome, second_outcome],
            source_question_number="3",
        )

        response = self.client.get(
            reverse("question-list"),
            {"topics": [second_topic.pk]},
        )

        self.assertSetEqual(
            set(response.context["questions"]),
            {primary_match, secondary_match},
        )

    def test_outcome_filter_supports_any_and_all_matching(self):
        self.client.force_login(self.user)
        second_outcome = LearningOutcome.objects.create(
            topic=self.topic,
            code="M.8.1.1.2",
            description="İki doğal sayının EBOB'unu bulur.",
        )
        both = self.create_question(
            "both.gif",
            outcomes=[self.outcome, second_outcome],
            source_question_number="2",
        )
        one = self.create_question(
            "one.gif",
            outcomes=[self.outcome],
            source_question_number="3",
        )

        any_response = self.client.get(
            reverse("question-list"),
            {"outcomes": [self.outcome.pk, second_outcome.pk], "outcome_match": "any"},
        )
        self.assertSetEqual(set(any_response.context["questions"]), {both, one})

        all_response = self.client.get(
            reverse("question-list"),
            {"outcomes": [self.outcome.pk, second_outcome.pk], "outcome_match": "all"},
        )
        self.assertSequenceEqual(list(all_response.context["questions"]), [both])

    def test_type_difficulty_and_completion_filters(self):
        self.client.force_login(self.user)
        completed = self.create_question("completed.gif", source_question_number="2")
        pending = self.create_question("pending.gif", source_question_number="3")
        question_type = QuestionType.objects.create(
            name="Doğrudan işlem",
            short_description="Tek işlemle çözülen soru.",
            solution_method="İşlemi uygula.",
            classification_criteria="Ek yorum gerektirmez.",
        )
        question_type.example_questions.add(completed)
        completed.question_type = question_type
        completed.difficulty = 4
        completed.solution = "Çözüm"
        completed.save()

        completed_response = self.client.get(
            reverse("question-list"),
            {
                "question_type": question_type.pk,
                "difficulty": "4",
                "status": "completed",
            },
        )
        self.assertSequenceEqual(
            list(completed_response.context["questions"]),
            [completed],
        )

        pending_response = self.client.get(
            reverse("question-list"),
            {"status": "question_type_pending"},
        )
        self.assertSequenceEqual(list(pending_response.context["questions"]), [pending])

    def test_question_list_is_paginated_by_twenty_five(self):
        self.client.force_login(self.user)
        for index in range(26):
            self.create_question(
                f"question-{index}.gif",
                source_question_number=str(index + 1),
            )

        first_page = self.client.get(reverse("question-list"))
        second_page = self.client.get(reverse("question-list"), {"page": 2})

        self.assertEqual(len(first_page.context["questions"]), 25)
        self.assertEqual(len(second_page.context["questions"]), 1)
        self.assertEqual(first_page.context["questions"].paginator.count, 26)


@override_settings(STORAGES=TEST_STORAGES)
class QuestionAPITests(TestCase):
    def setUp(self):
        self.server_user = get_user_model().objects.create_user(
            username="api-server",
            password="test-parolasi",
        )
        self.server_user.groups.add(Group.objects.get(name=API_SERVER_GROUP))
        self.server_token = Token.objects.create(user=self.server_user)
        self.student_user = get_user_model().objects.create_user(
            username="api-student",
            password="test-parolasi",
        )
        self.student_user.groups.add(Group.objects.get(name=API_STUDENT_GROUP))
        self.student_token = Token.objects.create(user=self.student_user)
        self.topic = Topic.objects.create(code="T001", name="Çarpanlar ve Katlar")
        self.outcome = LearningOutcome.objects.create(
            topic=self.topic,
            code="M.8.1.1.1",
            description="Pozitif tam sayıların çarpanlarını bulur.",
        )
        self.question_type = QuestionType.objects.create(
            name="Doğrudan işlem",
            short_description="Tek işlemle çözülen soru.",
            solution_method="İşlemi uygula.",
            classification_criteria="Ek yorum gerektirmez.",
        )

    @property
    def server_token_header(self):
        return {"HTTP_AUTHORIZATION": f"Token {self.server_token.key}"}

    @property
    def student_token_header(self):
        return {"HTTP_AUTHORIZATION": f"Token {self.student_token.key}"}

    def create_question(self, image_name="api.gif", outcomes=None, **overrides):
        values = {
            "original_image": test_image(image_name),
            "question_text": "API örnek sorusu",
            "choice_a": "1",
            "choice_b": "2",
            "choice_c": "3",
            "choice_d": "4",
            "correct_answer": "A",
            "primary_topic": self.topic,
            "question_type": self.question_type,
            "difficulty": 3,
            "solution": "Örnek çözüm",
            "source_pdf_name": "api-ornek.pdf",
            "source_page_number": 1,
            "source_question_number": "1",
        }
        values.update(overrides)
        question = Question.objects.create(**values)
        question.learning_outcomes.add(*(outcomes or [self.outcome]))
        self.question_type.example_questions.add(question)
        return question

    def test_api_root_and_schema_are_public(self):
        root_response = self.client.get(reverse("api-v1:root"))
        schema_response = self.client.get(reverse("api-v1:schema"))

        self.assertEqual(root_response.status_code, 200)
        self.assertEqual(root_response.json()["status"], "ready")
        self.assertEqual(schema_response.status_code, 200)
        self.assertEqual(schema_response.json()["openapi"], "3.0.3")

    def test_question_endpoints_reject_anonymous_requests(self):
        list_response = self.client.get(reverse("api-v1:question-list"))
        random_response = self.client.get(reverse("api-v1:question-random"))

        self.assertEqual(list_response.status_code, 401)
        self.assertEqual(random_response.status_code, 401)

    def test_token_without_api_role_is_forbidden(self):
        user = get_user_model().objects.create_user(username="api-role-yok")
        token = Token.objects.create(user=user)

        response = self.client.get(
            reverse("api-v1:question-list"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        self.assertEqual(response.status_code, 403)

    def test_student_list_hides_answers_and_excludes_unavailable_questions(self):
        available = self.create_question("available.gif")
        self.create_question(
            "incomplete.gif",
            question_type=None,
            difficulty=None,
            solution="",
            source_question_number="2",
        )
        archived = self.create_question("archived.gif", source_question_number="3")
        archived.archive()

        response = self.client.get(
            reverse("api-v1:question-list"),
            **self.student_token_header,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual([item["code"] for item in payload["results"]], [available.code])
        self.assertNotIn("correct_answer", payload["results"][0])
        self.assertNotIn("solution", payload["results"][0])

    def test_authorized_server_receives_answer_and_solution(self):
        question = self.create_question()

        response = self.client.get(
            reverse("api-v1:question-detail", kwargs={"code": question.code}),
            **self.server_token_header,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["correct_answer"], "A")
        self.assertEqual(response.json()["solution"], "Örnek çözüm")

    def test_authorized_server_can_explicitly_include_incomplete_and_archived(self):
        available = self.create_question("available.gif")
        incomplete = self.create_question(
            "incomplete.gif",
            question_type=None,
            difficulty=None,
            solution="",
            source_question_number="2",
        )
        archived = self.create_question("archived.gif", source_question_number="3")
        archived.archive()

        response = self.client.get(
            reverse("api-v1:question-list"),
            {"include_incomplete": "true", "include_archived": "true"},
            **self.server_token_header,
        )

        self.assertSetEqual(
            {item["code"] for item in response.json()["results"]},
            {available.code, incomplete.code, archived.code},
        )

    def test_student_cannot_override_visibility_defaults(self):
        available = self.create_question("available.gif")
        self.create_question(
            "incomplete.gif",
            question_type=None,
            difficulty=None,
            solution="",
            source_question_number="2",
        )

        response = self.client.get(
            reverse("api-v1:question-list"),
            {"include_incomplete": "true", "include_archived": "true"},
            **self.student_token_header,
        )

        self.assertEqual(
            [item["code"] for item in response.json()["results"]],
            [available.code],
        )

    def test_question_images_follow_the_same_access_roles(self):
        question = self.create_question()
        image_url = question.original_image.url

        anonymous_response = self.client.get(image_url)
        student_response = self.client.get(image_url, **self.student_token_header)
        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(student_response.status_code, 200)

        question.archive()
        archived_student_response = self.client.get(
            image_url,
            **self.student_token_header,
        )
        archived_server_response = self.client.get(
            image_url,
            **self.server_token_header,
        )
        self.assertEqual(archived_student_response.status_code, 404)
        self.assertEqual(archived_server_response.status_code, 200)

        self.client.force_login(self.server_user)
        session_response = self.client.get(image_url)
        self.assertEqual(session_response.status_code, 200)

    def test_filters_support_topics_outcomes_type_difficulty_and_exclusions(self):
        second_outcome = LearningOutcome.objects.create(
            topic=self.topic,
            code="M.8.1.1.2",
            description="İki doğal sayının EBOB'unu bulur.",
        )
        both = self.create_question(
            "both.gif",
            outcomes=[self.outcome, second_outcome],
            source_question_number="2",
        )
        one = self.create_question(
            "one.gif",
            outcomes=[self.outcome],
            source_question_number="3",
        )

        response = self.client.get(
            reverse("api-v1:question-list"),
            {
                "topics": self.topic.code,
                "outcomes": f"{self.outcome.code},{second_outcome.code}",
                "outcome_match": "all",
                "question_type": self.question_type.code,
                "difficulty": 3,
                "exclude": one.code,
            },
            **self.student_token_header,
        )

        self.assertEqual(
            [item["code"] for item in response.json()["results"]],
            [both.code],
        )

    def test_random_endpoint_honors_count_and_exclusions(self):
        first = self.create_question("first.gif")
        second = self.create_question("second.gif", source_question_number="2")
        third = self.create_question("third.gif", source_question_number="3")

        response = self.client.get(
            reverse("api-v1:question-random"),
            {"count": 2, "exclude": first.code},
            **self.student_token_header,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertSetEqual(
            {item["code"] for item in response.json()},
            {second.code, third.code},
        )

    def test_invalid_filter_values_return_bad_request(self):
        invalid_match = self.client.get(
            reverse("api-v1:question-list"),
            {"outcome_match": "none"},
            **self.student_token_header,
        )
        invalid_difficulty = self.client.get(
            reverse("api-v1:question-list"),
            {"difficulty": "9"},
            **self.student_token_header,
        )
        invalid_count = self.client.get(
            reverse("api-v1:question-random"),
            {"count": "101"},
            **self.student_token_header,
        )

        self.assertEqual(invalid_match.status_code, 400)
        self.assertEqual(invalid_difficulty.status_code, 400)
        self.assertEqual(invalid_count.status_code, 400)

    def test_invalid_token_is_rejected(self):
        response = self.client.get(
            reverse("api-v1:question-list"),
            HTTP_AUTHORIZATION="Token gecersiz-token",
        )

        self.assertEqual(response.status_code, 401)


class APITokenManagementCommandTests(TestCase):
    def test_command_creates_integration_user_with_selected_role(self):
        output = StringIO()

        call_command(
            "manage_api_token",
            "istemci-bir",
            role="student",
            stdout=output,
        )

        user = get_user_model().objects.get(username="istemci-bir")
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.groups.filter(name=API_STUDENT_GROUP).exists())
        self.assertFalse(user.groups.filter(name=API_SERVER_GROUP).exists())
        self.assertTrue(Token.objects.filter(user=user).exists())
        self.assertIn("Token oluşturuldu", output.getvalue())

    def test_command_rejects_human_or_admin_account(self):
        get_user_model().objects.create_user(
            username="yonetici-hesabi",
            password="insan-parolasi",
            is_staff=True,
        )

        with self.assertRaises(CommandError):
            call_command(
                "manage_api_token",
                "yonetici-hesabi",
                role="server",
                stdout=StringIO(),
            )

        self.assertFalse(
            Token.objects.filter(user__username="yonetici-hesabi").exists()
        )

    def test_command_rotates_and_revokes_token(self):
        call_command("manage_api_token", "sunucu-bir", role="server", stdout=StringIO())
        user = get_user_model().objects.get(username="sunucu-bir")
        old_key = Token.objects.get(user=user).key

        with self.assertRaises(CommandError):
            call_command(
                "manage_api_token",
                "sunucu-bir",
                role="server",
                stdout=StringIO(),
            )

        call_command(
            "manage_api_token",
            "sunucu-bir",
            role="server",
            rotate=True,
            stdout=StringIO(),
        )
        self.assertNotEqual(Token.objects.get(user=user).key, old_key)

        call_command(
            "manage_api_token",
            "sunucu-bir",
            revoke=True,
            stdout=StringIO(),
        )
        self.assertFalse(Token.objects.filter(user=user).exists())
