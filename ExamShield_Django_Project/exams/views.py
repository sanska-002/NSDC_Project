import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Exam, Question, Attempt, Answer

def home(request):
    exams = Exam.objects.filter(is_published=True).prefetch_related("questions")
    return render(request, "exams/home.html", {"exams": exams})

@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    if request.method != "POST":
        return render(request, "exams/confirm_start.html", {"exam": exam})
    if not exam.questions.exists():
        messages.error(request, "This exam has no questions yet.")
        return redirect("home")
    existing = Attempt.objects.filter(student=request.user, exam=exam, is_submitted=False).first()
    if existing:
        return redirect("take_exam", attempt_id=existing.id)
    attempt = Attempt.objects.create(student=request.user, exam=exam, total_marks=sum(q.marks for q in exam.questions.all()))
    return redirect("take_exam", attempt_id=attempt.id)

@login_required
def take_exam(request, attempt_id):
    attempt = get_object_or_404(Attempt.objects.select_related("exam"), id=attempt_id, student=request.user)
    if attempt.is_submitted:
        return redirect("result_detail", attempt_id=attempt.id)
    deadline = attempt.started_at + timedelta(minutes=attempt.exam.duration_minutes)
    if timezone.now() >= deadline:
        _finalize_attempt(attempt, {}, "timeout")
        return redirect("result_detail", attempt_id=attempt.id)
    questions = attempt.exam.questions.all()
    return render(request, "exams/take_exam.html", {
        "attempt": attempt, "exam": attempt.exam, "questions": questions,
        "remaining_seconds": max(0, int((deadline-timezone.now()).total_seconds()))
    })

@login_required
@require_POST
def submit_exam(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id, student=request.user)
    if attempt.is_submitted:
        return JsonResponse({"ok": True, "redirect": f"/result/{attempt.id}/", "already_submitted": True})
    payload = {}
    try:
        payload = json.loads(request.body or "{}")
        answers = payload.get("answers", {})
        if not isinstance(answers, dict):
            answers = {}
    except (json.JSONDecodeError, AttributeError):
        answers = {}
    reason = payload.get("reason", "submitted") if isinstance(payload, dict) else "submitted"
    if reason not in {"submitted", "timeout", "tab_switch"}:
        reason = "submitted"
    deadline = attempt.started_at + timedelta(minutes=attempt.exam.duration_minutes)
    if timezone.now() >= deadline:
        reason = "timeout"
    _finalize_attempt(attempt, answers, reason)
    return JsonResponse({"ok": True, "redirect": f"/result/{attempt.id}/"})

@transaction.atomic
def _finalize_attempt(attempt, submitted_answers, reason):
    attempt = Attempt.objects.select_for_update().get(pk=attempt.pk)
    if attempt.is_submitted:
        return
    score = 0
    total = 0
    for question in attempt.exam.questions.all():
        total += question.marks
        selected = submitted_answers.get(str(question.id), "")
        if selected not in {"A", "B", "C", "D"}:
            selected = ""
        correct = selected == question.correct_option
        awarded = question.marks if correct else 0
        score += awarded
        Answer.objects.update_or_create(
            attempt=attempt, question=question,
            defaults={"selected_option": selected, "is_correct": correct, "marks_awarded": awarded}
        )
    attempt.score = score
    attempt.total_marks = total
    attempt.reason = reason
    attempt.submitted_at = timezone.now()
    attempt.is_submitted = True
    attempt.save()

@login_required
def results(request):
    attempts = Attempt.objects.filter(student=request.user, is_submitted=True).select_related("exam")
    return render(request, "exams/results.html", {"attempts": attempts})

@login_required
def result_detail(request, attempt_id):
    attempt = get_object_or_404(Attempt.objects.select_related("exam"), id=attempt_id, student=request.user, is_submitted=True)
    answers = attempt.answers.select_related("question")
    return render(request, "exams/result_detail.html", {"attempt": attempt, "answers": answers})
