from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import QuestionFilterForm, QuestionForm, QuestionSolutionForm
from .models import Question


def health_check(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "soru-havuzu",
        }
    )


@login_required
def question_list(request):
    state = request.GET.get("state", "active")
    base_questions = Question.objects.select_related(
        "primary_topic",
        "question_type",
    ).prefetch_related("learning_outcomes")

    if state == "archived":
        questions = base_questions.filter(archived_at__isnull=False)
    else:
        state = "active"
        questions = base_questions.filter(archived_at__isnull=True)

    filter_form = QuestionFilterForm(request.GET)
    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        search_term = filters.get("q")
        if search_term:
            questions = questions.filter(
                Q(code__icontains=search_term)
                | Q(question_text__icontains=search_term)
            )

        topics = filters.get("topics")
        if topics:
            questions = questions.filter(
                Q(primary_topic__in=topics) | Q(secondary_topics__in=topics)
            )

        outcomes = filters.get("outcomes")
        if outcomes:
            outcome_ids = list(outcomes.values_list("pk", flat=True))
            if filters.get("outcome_match") == "all":
                questions = questions.annotate(
                    selected_outcome_count=Count(
                        "learning_outcomes",
                        filter=Q(learning_outcomes__in=outcome_ids),
                        distinct=True,
                    )
                ).filter(selected_outcome_count=len(outcome_ids))
            else:
                questions = questions.filter(learning_outcomes__in=outcome_ids)

        if filters.get("question_type"):
            questions = questions.filter(question_type=filters["question_type"])
        if filters.get("difficulty"):
            questions = questions.filter(difficulty=int(filters["difficulty"]))
        if filters.get("source_pdf"):
            questions = questions.filter(
                source_pdf_name__icontains=filters["source_pdf"]
            )
        if filters.get("source_question_number"):
            questions = questions.filter(
                source_question_number__icontains=filters["source_question_number"]
            )

        status = filters.get("status")
        if status == "question_type_pending":
            questions = questions.filter(question_type__isnull=True)
        elif status == "difficulty_pending":
            questions = questions.filter(difficulty__isnull=True)
        elif status == "solution_pending":
            questions = questions.filter(solution="")
        elif status == "completed":
            questions = questions.filter(
                question_type__isnull=False,
                difficulty__isnull=False,
            ).exclude(solution="")

    questions = questions.distinct().order_by("code")
    paginator = Paginator(questions, 25)
    page = paginator.get_page(request.GET.get("page"))

    active_questions = Question.objects.filter(archived_at__isnull=True)
    worklist_counts = {
        "active": active_questions.count(),
        "question_type_pending": active_questions.filter(
            question_type__isnull=True
        ).count(),
        "difficulty_pending": active_questions.filter(difficulty__isnull=True).count(),
        "solution_pending": active_questions.filter(solution="").count(),
        "completed": active_questions.filter(
            question_type__isnull=False,
            difficulty__isnull=False,
        ).exclude(solution="").count(),
        "archived": Question.objects.filter(archived_at__isnull=False).count(),
    }

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "core/question_list.html",
        {
            "questions": page,
            "filter_form": filter_form,
            "state": state,
            "worklist_counts": worklist_counts,
            "query_string": query_params.urlencode(),
        },
    )


@login_required
def question_detail(request, code):
    question = get_object_or_404(
        Question.objects.select_related("primary_topic", "question_type").prefetch_related(
            "secondary_topics",
            "learning_outcomes",
        ),
        code=code,
    )
    return render(request, "core/question_detail.html", {"question": question})


@login_required
def question_create(request):
    form = QuestionForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        question = form.save()
        messages.success(request, f"{question.code} başarıyla oluşturuldu.")
        return redirect("question-detail", code=question.code)
    return render(
        request,
        "core/question_form.html",
        {"form": form, "page_title": "Yeni soru"},
    )


@login_required
def question_update(request, code):
    question = get_object_or_404(Question, code=code)
    form = QuestionForm(
        request.POST or None,
        request.FILES or None,
        instance=question,
    )
    if request.method == "POST" and form.is_valid():
        question = form.save()
        messages.success(request, f"{question.code} başarıyla güncellendi.")
        return redirect("question-detail", code=question.code)
    return render(
        request,
        "core/question_form.html",
        {"form": form, "page_title": f"{question.code} düzenle", "question": question},
    )


@login_required
def question_solution(request, code):
    question = get_object_or_404(Question, code=code)
    form = QuestionSolutionForm(request.POST or None, instance=question)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{question.code} çözümü güncellendi.")
        return redirect("question-detail", code=question.code)
    return render(
        request,
        "core/question_solution_form.html",
        {"form": form, "question": question},
    )


@login_required
@require_POST
def question_archive(request, code):
    question = get_object_or_404(Question, code=code)
    question.archive()
    messages.success(request, f"{question.code} arşivlendi.")
    return redirect("question-detail", code=question.code)


@login_required
@require_POST
def question_restore(request, code):
    question = get_object_or_404(Question, code=code)
    question.restore()
    messages.success(request, f"{question.code} arşivden çıkarıldı.")
    return redirect("question-detail", code=question.code)


@login_required
def question_delete(request, code):
    question = get_object_or_404(Question, code=code)
    if request.method == "POST":
        image = question.original_image
        question_code = question.code
        question.delete()
        image.delete(save=False)
        messages.success(request, f"{question_code} kalıcı olarak silindi.")
        return redirect("question-list")
    return render(request, "core/question_confirm_delete.html", {"question": question})
