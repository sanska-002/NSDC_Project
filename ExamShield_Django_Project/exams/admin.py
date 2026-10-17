from django.contrib import admin
from .models import Exam, Question, Attempt, Answer

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_minutes", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title",)
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "exam", "correct_option", "marks")
    list_filter = ("exam",)
    search_fields = ("text",)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ("question", "selected_option", "is_correct", "marks_awarded")

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "score", "total_marks", "reason", "is_submitted", "started_at")
    list_filter = ("exam", "reason", "is_submitted")
    search_fields = ("student__username", "exam__title")
    inlines = [AnswerInline]
    readonly_fields = ("student", "exam", "started_at", "submitted_at", "reason", "score", "total_marks", "is_submitted")
