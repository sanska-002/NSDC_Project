from django.conf import settings
from django.db import models
from django.utils import timezone

class Exam(models.Model):
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class Question(models.Model):
    exam = models.ForeignKey(Exam, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_option = models.CharField(max_length=1, choices=[("A","A"),("B","B"),("C","C"),("D","D")])
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ["order", "id"]
    def __str__(self): return self.text[:70]

class Attempt(models.Model):
    REASONS = [("submitted","Submitted by student"),("timeout","Time expired"),("tab_switch","Tab/window switch detected")]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=20, choices=REASONS, default="submitted")
    score = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    class Meta: ordering = ["-started_at"]
    def __str__(self): return f"{self.student} — {self.exam}"
    @property
    def percentage(self):
        return round(self.score * 100 / self.total_marks, 1) if self.total_marks else 0

class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.PositiveIntegerField(default=0)
    class Meta: unique_together = ("attempt", "question")
